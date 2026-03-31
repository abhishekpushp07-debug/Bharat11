"""
Bharat 11 - Auto-Pilot Mode
Full hands-free IPL season management.

Every 45 seconds:
1. Fetches live match scorecards from CricketData.org Premium API
2. Evaluates all unresolved questions against live metrics
3. Auto-resolves when conditions are met
4. Auto-finalizes contests and distributes prizes

Admin can start/stop via API.
"""
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class AutoPilot:
    """Singleton auto-pilot manager."""

    def __init__(self):
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._interval = 45  # seconds
        self._last_run = None
        self._run_count = 0
        self._last_result = None
        self._log: list = []

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
            "recent_log": self._log[-10:],
        }

    def _add_log(self, msg: str):
        ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
        entry = f"[{ts}] {msg}"
        self._log.append(entry)
        if len(self._log) > 50:
            self._log = self._log[-30:]
        logger.info(f"AutoPilot: {msg}")

    async def start(self, db):
        """Start the auto-pilot background loop."""
        if self._running:
            return {"message": "Already running", "running": True}

        self._running = True
        self._task = asyncio.create_task(self._loop(db))
        self._add_log("Auto-Pilot STARTED")
        return {"message": "Auto-Pilot started", "running": True, "interval": self._interval}

    async def stop(self):
        """Stop the auto-pilot."""
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._task = None
        self._add_log("Auto-Pilot STOPPED")
        return {"message": "Auto-Pilot stopped", "running": False}

    async def _loop(self, db):
        """Main auto-pilot loop — runs every 45 seconds."""
        while self._running:
            try:
                await self._run_cycle(db)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._add_log(f"Error in cycle: {str(e)[:100]}")
                logger.exception("AutoPilot cycle error")

            # Wait for interval
            try:
                await asyncio.sleep(self._interval)
            except asyncio.CancelledError:
                break

    async def _run_cycle(self, db):
        """Single auto-pilot cycle: check all active matches."""
        from services.settlement_engine import run_settlement_for_match

        self._run_count += 1
        self._last_run = datetime.now(timezone.utc).isoformat()

        # Every 10th cycle (~7.5 min): auto-create contests for upcoming matches within 24h
        if self._run_count % 10 == 1:
            try:
                from services.match_engine import auto_create_contests_24h
                ac_result = await auto_create_contests_24h(db)
                created = [r for r in ac_result.get("results", []) if r.get("status") == "created"]
                if created:
                    self._add_log(f"Auto-contests: {len(created)} new contests created")
            except Exception as e:
                self._add_log(f"Auto-contest error: {str(e)[:60]}")

        # ==================== AUTO LIVE/UNLIVE CONTESTS ====================
        # Every 5th cycle (~3.75 min): manage contest lifecycle
        if self._run_count % 5 == 0:
            try:
                await self._manage_contest_lifecycle(db)
            except Exception as e:
                self._add_log(f"Contest lifecycle error: {str(e)[:60]}")

        # Find matches that need settlement (live or completed, with active contests)
        matches = await db.matches.find(
            {"status": {"$in": ["live", "completed"]}},
            {"_id": 0, "id": 1, "team_a": 1, "team_b": 1, "status": 1}
        ).sort("updated_at", -1).to_list(length=20)

        if not matches:
            self._last_result = {"cycle": self._run_count, "matches_checked": 0}
            return

        total_resolved = 0
        total_finalized = 0

        for match in matches:
            mid = match["id"]
            ta = match.get("team_a", {}).get("short_name", "?")
            tb = match.get("team_b", {}).get("short_name", "?")

            # Check if there are unresolved contests
            active_contests = await db.contests.count_documents(
                {"match_id": mid, "status": {"$ne": "completed"}}
            )
            if active_contests == 0:
                continue

            # Run settlement
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
                self._add_log(f"{ta}v{tb}: Error - {str(e)[:60]}")

        self._last_result = {
            "cycle": self._run_count,
            "matches_checked": len(matches),
            "total_resolved": total_resolved,
            "total_finalized": total_finalized,
        }

        if total_resolved > 0 or total_finalized > 0:
            self._add_log(f"Cycle #{self._run_count}: {total_resolved} resolved, {total_finalized} finalized")

    async def _manage_contest_lifecycle(self, db):
        """
        Auto Live/Unlive contest lifecycle:
        1. Auto-Live: 24 hrs before match start → contest status "open" → "live"
        2. Auto-Lock (full_match): After 1st innings 6th over → "locked"
        3. Auto-Lock (in_match): Before innings interval → "locked"
        IMPORTANT: Skips matches/contests with manual_override=True
        """
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        cutoff_24h = (now + timedelta(hours=24)).isoformat()

        # 1. AUTO-LIVE: Find matches starting within 24 hours, set their "open" contests to "live"
        upcoming_matches = await db.matches.find(
            {
                "status": {"$in": ["upcoming", "live"]},
                "start_time": {"$lte": cutoff_24h},
                "manual_override": {"$ne": True},
            },
            {"_id": 0, "id": 1, "start_time": 1}
        ).to_list(None)

        for m in upcoming_matches:
            result = await db.contests.update_many(
                {"match_id": m["id"], "status": "open", "manual_override": {"$ne": True}},
                {"$set": {"status": "live", "updated_at": now_iso}}
            )
            if result.modified_count > 0:
                self._add_log(f"Auto-LIVE: {result.modified_count} contests for match starting {m.get('start_time','?')[:16]}")

        # 2. AUTO-LOCK (full_match): After 1st innings 6th over → lock full_match contests
        live_matches = await db.matches.find(
            {"status": "live", "manual_override": {"$ne": True}},
            {"_id": 0, "id": 1, "live_score": 1, "team_a": 1, "team_b": 1}
        ).to_list(None)

        for m in live_matches:
            live_score = m.get("live_score", {})
            scores = live_score.get("scores", [])
            if not scores:
                continue

            # Check if 1st innings has crossed 6 overs
            innings_1 = scores[0] if len(scores) > 0 else {}
            overs_str = str(innings_1.get("o", innings_1.get("overs", "0")))
            try:
                overs_float = float(overs_str)
            except (ValueError, TypeError):
                overs_float = 0

            if overs_float >= 6.0:
                # Lock all full_match contests for this match (skip manual overrides)
                full_match_contests = await db.contests.find(
                    {"match_id": m["id"], "status": "live", "manual_override": {"$ne": True}},
                    {"_id": 0, "id": 1, "template_id": 1}
                ).to_list(None)

                for c in full_match_contests:
                    # Check if template is full_match
                    template = await db.templates.find_one(
                        {"id": c.get("template_id")},
                        {"_id": 0, "template_type": 1}
                    )
                    if template and template.get("template_type") == "full_match":
                        await db.contests.update_one(
                            {"id": c["id"]},
                            {"$set": {"status": "locked", "updated_at": now_iso}}
                        )
                        ta = m.get("team_a", {}).get("short_name", "?")
                        tb = m.get("team_b", {}).get("short_name", "?")
                        self._add_log(f"Auto-LOCK full_match: {ta}v{tb} after 6th over")

            # 3. AUTO-LOCK (in_match): Check if innings interval (2nd innings started or break)
            if len(scores) >= 2:
                # 2nd innings exists — lock in_match contests (skip manual overrides)
                in_match_contests = await db.contests.find(
                    {"match_id": m["id"], "status": "live", "manual_override": {"$ne": True}},
                    {"_id": 0, "id": 1, "template_id": 1}
                ).to_list(None)

                for c in in_match_contests:
                    template = await db.templates.find_one(
                        {"id": c.get("template_id")},
                        {"_id": 0, "template_type": 1}
                    )
                    if template and template.get("template_type") == "in_match":
                        await db.contests.update_one(
                            {"id": c["id"]},
                            {"$set": {"status": "locked", "updated_at": now_iso}}
                        )
                        ta = m.get("team_a", {}).get("short_name", "?")
                        tb = m.get("team_b", {}).get("short_name", "?")
                        self._add_log(f"Auto-LOCK in_match: {ta}v{tb} before interval")


# Singleton
autopilot = AutoPilot()
