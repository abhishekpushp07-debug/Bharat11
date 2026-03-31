"""
Bharat 11 - Auto-Pilot Mode v3
Full hands-free scorecard + settlement engine.

Every 15 seconds:
1. Checks CricketData.org API for which real IPL matches have started
2. For started matches: Fetches fresh scorecard every 15s and updates DB
3. Runs settlement engine (auto-resolves questions, auto-finalizes contests)

IMPORTANT: Match status (upcoming/live/completed) is ADMIN-CONTROLLED.
AutoPilot does NOT change match status — admin manually sets "Live"/"Completed".
AutoPilot only auto-fetches real-time scorecard data when real match has started.
"""
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


class AutoPilot:
    """Singleton auto-pilot manager."""

    def __init__(self):
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._interval = 15  # 15 seconds
        self._last_run = None
        self._run_count = 0
        self._last_result = None
        self._log: list = []
        # Track which cricketdata_ids have real matches running (matchStarted=true from API)
        self._real_live_ids: set = set()

    @property
    def is_running(self) -> bool:
        return self._running

    def get_status(self) -> dict:
        return {
            "running": self._running,
            "interval_seconds": self._interval,
            "run_count": self._run_count,
            "last_run": self._last_run,
            "last_result": self._last_result,
            "real_live_matches": len(self._real_live_ids),
            "recent_log": self._log[-15:],
        }

    def _add_log(self, msg: str):
        ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
        entry = f"[{ts}] {msg}"
        self._log.append(entry)
        if len(self._log) > 50:
            self._log = self._log[-30:]
        logger.info(f"AutoPilot: {msg}")

    async def start(self, db):
        if self._running:
            return {"message": "Already running", "running": True}
        self._running = True
        self._task = asyncio.create_task(self._loop(db))
        self._add_log("Auto-Pilot STARTED (15s real-time scorecard)")
        return {"message": "Auto-Pilot started", "running": True, "interval": self._interval}

    async def stop(self):
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._task = None
        self._real_live_ids.clear()
        self._add_log("Auto-Pilot STOPPED")
        return {"message": "Auto-Pilot stopped", "running": False}

    async def _loop(self, db):
        while self._running:
            try:
                await self._run_cycle(db)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._add_log(f"Cycle error: {str(e)[:100]}")
                logger.exception("AutoPilot cycle error")
            try:
                await asyncio.sleep(self._interval)
            except asyncio.CancelledError:
                break

    async def _run_cycle(self, db):
        from services.settlement_engine import run_settlement_for_match

        self._run_count += 1
        self._last_run = datetime.now(timezone.utc).isoformat()

        # ========== STEP 1: Detect real live matches from CricketData API ==========
        # Uses lightweight cric_score endpoint (1 API call = all matches)
        await self._detect_real_live_matches(db)

        # ========== STEP 2: Fetch scorecards for real live matches ==========
        scorecard_updates = await self._auto_fetch_scorecards(db)

        # ========== STEP 3: Settlement for admin-set "live" matches ==========
        live_matches = await db.matches.find(
            {"status": {"$in": ["live", "completed"]}},
            {"_id": 0, "id": 1, "team_a": 1, "team_b": 1, "status": 1}
        ).sort("updated_at", -1).to_list(length=20)

        total_resolved = 0
        total_finalized = 0

        for match in live_matches:
            mid = match["id"]
            ta = match.get("team_a", {}).get("short_name", "?")
            tb = match.get("team_b", {}).get("short_name", "?")

            active_contests = await db.contests.count_documents(
                {"match_id": mid, "status": {"$ne": "completed"}}
            )
            if active_contests == 0:
                continue

            try:
                result = await run_settlement_for_match(mid, db)
                resolved = result.get("total_resolved", 0)
                total_resolved += resolved
                for c in result.get("contests", []):
                    if c.get("auto_finalized"):
                        total_finalized += 1
                if resolved > 0:
                    self._add_log(f"{ta}v{tb}: {resolved} resolved")
                if total_finalized > 0:
                    self._add_log(f"{ta}v{tb}: Contest FINALIZED!")
            except Exception as e:
                self._add_log(f"{ta}v{tb}: Settlement error - {str(e)[:60]}")

        # ========== STEP 4: Periodic tasks ==========
        # Every 10th cycle (~2.5 min): auto-create contests for upcoming 24h matches
        if self._run_count % 10 == 1:
            try:
                from services.match_engine import auto_create_contests_24h
                ac_result = await auto_create_contests_24h(db)
                created = [r for r in ac_result.get("results", []) if r.get("status") == "created"]
                if created:
                    self._add_log(f"Auto-contests: {len(created)} new")
            except Exception as e:
                self._add_log(f"Auto-contest error: {str(e)[:60]}")

        # Every 5th cycle (~1.25 min): manage contest lifecycle
        if self._run_count % 5 == 0:
            try:
                await self._manage_contest_lifecycle(db)
            except Exception as e:
                self._add_log(f"Contest lifecycle error: {str(e)[:60]}")

        self._last_result = {
            "cycle": self._run_count,
            "real_live_matches": len(self._real_live_ids),
            "scorecards_updated": scorecard_updates,
            "matches_checked": len(live_matches),
            "total_resolved": total_resolved,
            "total_finalized": total_finalized,
        }

        if scorecard_updates > 0 or total_resolved > 0 or total_finalized > 0:
            self._add_log(f"Cycle #{self._run_count}: {scorecard_updates} scorecards, {total_resolved} resolved, {total_finalized} finalized")

    async def _detect_real_live_matches(self, db):
        """
        Check CricketData.org API (cric_score) to find which IPL matches
        have actually started in real life (matchStarted=true).
        Does NOT change match status in DB — that's admin's job.
        """
        from services.cricket_data import cricket_service

        try:
            live_data = await cricket_service.get_cric_score()
            if not live_data:
                return

            new_live_ids = set()
            for api_match in live_data:
                cd_id = api_match.get("id", "")
                if not cd_id:
                    continue

                match_started = api_match.get("matchStarted", False)
                match_ended = api_match.get("matchEnded", False)
                status_text = api_match.get("status", "")

                # Skip false positives
                if match_started and not match_ended and "match starts at" in status_text.lower():
                    continue

                if match_started and not match_ended:
                    # Real match is live — check if it's in our DB
                    db_match = await db.matches.find_one(
                        {"$or": [{"cricketdata_id": cd_id}, {"external_match_id": cd_id}]},
                        {"_id": 0, "id": 1, "team_a": 1, "team_b": 1}
                    )
                    if db_match:
                        new_live_ids.add(cd_id)

                        # Log when a new match goes live
                        if cd_id not in self._real_live_ids:
                            ta = db_match.get("team_a", {}).get("short_name", "?")
                            tb = db_match.get("team_b", {}).get("short_name", "?")
                            self._add_log(f"REAL MATCH STARTED: {ta} vs {tb}")

                        # Update live_score from cric_score data (lightweight)
                        scores = []
                        for s in api_match.get("score", []):
                            scores.append({
                                "inning": s.get("inning", ""),
                                "r": s.get("r", 0), "runs": s.get("r", 0),
                                "w": s.get("w", 0), "wickets": s.get("w", 0),
                                "o": s.get("o", 0), "overs": s.get("o", 0),
                            })
                        if scores:
                            now_iso = datetime.now(timezone.utc).isoformat()
                            await db.matches.update_one(
                                {"$or": [{"cricketdata_id": cd_id}, {"external_match_id": cd_id}]},
                                {"$set": {
                                    "live_score": {"scores": scores, "updated_at": now_iso},
                                    "status_text": status_text,
                                    "updated_at": now_iso
                                }}
                            )

            self._real_live_ids = new_live_ids

        except Exception as e:
            self._add_log(f"Detect live error: {str(e)[:80]}")

    async def _auto_fetch_scorecards(self, db) -> int:
        """
        For every REAL LIVE match (detected from API), fetch fresh scorecard
        from CricketData Premium API and update DB cache.
        """
        from services.cricket_data import cricket_service
        from services.api_cache import set_cache

        if not self._real_live_ids:
            return 0

        updated = 0

        for cd_id in list(self._real_live_ids):
            try:
                # Clear in-memory cache to force fresh fetch
                sc_key = f"scorecard_{cd_id}"
                cricket_service._cache.pop(sc_key, None)
                cricket_service._cache_time.pop(sc_key, None)

                # Fetch fresh scorecard from Premium API
                data = await cricket_service.get_scorecard(cd_id)
                if data:
                    is_ended = data.get("matchEnded", False)
                    await set_cache(db, "scorecard", cd_id, data, permanent=is_ended)

                    # If match ended, remove from real_live tracking
                    if is_ended:
                        self._real_live_ids.discard(cd_id)
                        self._add_log(f"REAL MATCH ENDED: {cd_id[:12]}...")

                    updated += 1

            except Exception as e:
                self._add_log(f"Scorecard {cd_id[:12]}: {str(e)[:60]}")

        return updated

    async def _manage_contest_lifecycle(self, db):
        """
        Auto Live/Unlive contest lifecycle:
        1. Auto-Live: 24 hrs before match start → contest "open" → "live"
        2. Auto-Lock (full_match): After 1st innings 6th over → "locked"
        3. Auto-Lock (in_match): 2nd innings started → "locked"
        Skips manual_override=True.
        """
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        cutoff_24h = (now + timedelta(hours=24)).isoformat()

        # 1. AUTO-LIVE contests
        upcoming_matches = await db.matches.find(
            {
                "status": {"$in": ["upcoming", "live"]},
                "start_time": {"$lte": cutoff_24h},
                "manual_override": {"$ne": True},
            },
            {"_id": 0, "id": 1}
        ).to_list(None)

        for m in upcoming_matches:
            result = await db.contests.update_many(
                {"match_id": m["id"], "status": "open", "manual_override": {"$ne": True}},
                {"$set": {"status": "live", "updated_at": now_iso}}
            )
            if result.modified_count > 0:
                self._add_log(f"Auto-LIVE: {result.modified_count} contests")

        # 2. AUTO-LOCK full_match after 6th over
        live_matches = await db.matches.find(
            {"status": "live", "manual_override": {"$ne": True}},
            {"_id": 0, "id": 1, "live_score": 1, "team_a": 1, "team_b": 1}
        ).to_list(None)

        for m in live_matches:
            scores = m.get("live_score", {}).get("scores", [])
            if not scores:
                continue

            innings_1 = scores[0] if scores else {}
            try:
                overs = float(str(innings_1.get("o", innings_1.get("overs", "0"))))
            except (ValueError, TypeError):
                overs = 0

            if overs >= 6.0:
                contests = await db.contests.find(
                    {"match_id": m["id"], "status": "live", "manual_override": {"$ne": True}},
                    {"_id": 0, "id": 1, "template_id": 1}
                ).to_list(None)

                for c in contests:
                    tmpl = await db.templates.find_one({"id": c.get("template_id")}, {"_id": 0, "template_type": 1})
                    if tmpl and tmpl.get("template_type") == "full_match":
                        await db.contests.update_one({"id": c["id"]}, {"$set": {"status": "locked", "updated_at": now_iso}})
                        ta = m.get("team_a", {}).get("short_name", "?")
                        tb = m.get("team_b", {}).get("short_name", "?")
                        self._add_log(f"Auto-LOCK full_match: {ta}v{tb}")

            # 3. AUTO-LOCK in_match when 2nd innings starts
            if len(scores) >= 2:
                contests = await db.contests.find(
                    {"match_id": m["id"], "status": "live", "manual_override": {"$ne": True}},
                    {"_id": 0, "id": 1, "template_id": 1}
                ).to_list(None)

                for c in contests:
                    tmpl = await db.templates.find_one({"id": c.get("template_id")}, {"_id": 0, "template_type": 1})
                    if tmpl and tmpl.get("template_type") == "in_match":
                        await db.contests.update_one({"id": c["id"]}, {"$set": {"status": "locked", "updated_at": now_iso}})
                        ta = m.get("team_a", {}).get("short_name", "?")
                        tb = m.get("team_b", {}).get("short_name", "?")
                        self._add_log(f"Auto-LOCK in_match: {ta}v{tb}")


# Singleton
autopilot = AutoPilot()
