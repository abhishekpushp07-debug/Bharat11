"""
Bharat 11 - Per-Match Score Fetcher
Fetches scorecard from CricketData.org every 15 seconds for specific matches.

Admin clicks "Score Fetch" on a match → starts 15s polling for THAT match.
Auto-stops when:
  1. Match is 100% completed (matchEnded=true from API)
  2. 5 hours elapsed since start
  Whichever comes first.
"""
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional

logger = logging.getLogger(__name__)

MAX_FETCH_HOURS = 5  # Auto-stop after 5 hours
FETCH_INTERVAL = 15  # seconds


class MatchScoreFetcher:
    """Manages per-match scorecard fetching tasks."""

    def __init__(self):
        self._tasks: Dict[str, asyncio.Task] = {}  # match_id → Task
        self._started_at: Dict[str, datetime] = {}  # match_id → start time
        self._fetch_counts: Dict[str, int] = {}  # match_id → fetch count
        self._last_scores: Dict[str, dict] = {}  # match_id → last score summary
        self._stopped_reason: Dict[str, str] = {}  # match_id → reason

    def get_status(self) -> dict:
        """Get status of all active fetchers."""
        active = {}
        for mid in list(self._tasks.keys()):
            task = self._tasks.get(mid)
            is_running = task and not task.done()
            if is_running:
                started = self._started_at.get(mid)
                elapsed = (datetime.now(timezone.utc) - started).total_seconds() if started else 0
                active[mid] = {
                    "running": True,
                    "fetch_count": self._fetch_counts.get(mid, 0),
                    "started_at": started.isoformat() if started else None,
                    "elapsed_minutes": round(elapsed / 60, 1),
                    "last_score": self._last_scores.get(mid),
                }
        return {
            "active_fetchers": len(active),
            "matches": active,
        }

    def get_match_status(self, match_id: str) -> dict:
        """Get fetch status for a specific match."""
        task = self._tasks.get(match_id)
        is_running = task and not task.done()
        started = self._started_at.get(match_id)
        elapsed = (datetime.now(timezone.utc) - started).total_seconds() if started else 0

        return {
            "match_id": match_id,
            "running": is_running,
            "fetch_count": self._fetch_counts.get(match_id, 0),
            "started_at": started.isoformat() if started else None,
            "elapsed_minutes": round(elapsed / 60, 1),
            "last_score": self._last_scores.get(match_id),
            "stopped_reason": self._stopped_reason.get(match_id),
        }

    async def start_fetch(self, match_id: str, cricketdata_id: str, db) -> dict:
        """Start 15s scorecard fetching for a specific match."""
        # Already running?
        existing = self._tasks.get(match_id)
        if existing and not existing.done():
            return {
                "message": "Already fetching",
                "match_id": match_id,
                "running": True,
                "fetch_count": self._fetch_counts.get(match_id, 0),
            }

        # Start new fetch task
        self._started_at[match_id] = datetime.now(timezone.utc)
        self._fetch_counts[match_id] = 0
        self._stopped_reason.pop(match_id, None)
        self._tasks[match_id] = asyncio.create_task(
            self._fetch_loop(match_id, cricketdata_id, db)
        )

        logger.info(f"ScoreFetcher: STARTED for match {match_id} (cd_id: {cricketdata_id})")
        return {
            "message": "Score fetching started (every 15s)",
            "match_id": match_id,
            "running": True,
            "interval": FETCH_INTERVAL,
            "max_hours": MAX_FETCH_HOURS,
        }

    async def stop_fetch(self, match_id: str) -> dict:
        """Stop scorecard fetching for a specific match."""
        task = self._tasks.get(match_id)
        if task and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            self._stopped_reason[match_id] = "manual_stop"
            logger.info(f"ScoreFetcher: STOPPED (manual) for match {match_id}")

        self._tasks.pop(match_id, None)
        return {
            "message": "Score fetching stopped",
            "match_id": match_id,
            "running": False,
            "total_fetches": self._fetch_counts.get(match_id, 0),
        }

    async def _fetch_loop(self, match_id: str, cricketdata_id: str, db):
        """Fetch scorecard every 15 seconds until match ends or 5h timeout."""
        from services.cricket_data import cricket_service
        from services.api_cache import set_cache

        deadline = self._started_at[match_id] + timedelta(hours=MAX_FETCH_HOURS)

        while True:
            try:
                now = datetime.now(timezone.utc)

                # Check 5-hour timeout
                if now >= deadline:
                    self._stopped_reason[match_id] = "timeout_5h"
                    logger.info(f"ScoreFetcher: STOPPED (5h timeout) for match {match_id}")
                    break

                # Clear in-memory cache to force fresh API call
                sc_key = f"scorecard_{cricketdata_id}"
                cricket_service._cache.pop(sc_key, None)
                cricket_service._cache_time.pop(sc_key, None)

                # Fetch fresh scorecard
                data = await cricket_service.get_scorecard(cricketdata_id)
                self._fetch_counts[match_id] = self._fetch_counts.get(match_id, 0) + 1

                if data:
                    is_ended = data.get("matchEnded", False)

                    # Store in MongoDB cache (permanent if match ended)
                    await set_cache(db, "scorecard", cricketdata_id, data, permanent=is_ended)

                    # Update live_score in match document
                    now_iso = now.isoformat()
                    score_data = data.get("score", [])
                    if isinstance(score_data, list) and score_data:
                        scores = []
                        for s in score_data:
                            if isinstance(s, dict):
                                scores.append({
                                    "inning": s.get("inning", ""),
                                    "r": s.get("r", 0), "runs": s.get("r", 0),
                                    "w": s.get("w", 0), "wickets": s.get("w", 0),
                                    "o": s.get("o", 0), "overs": s.get("o", 0),
                                })
                        if scores:
                            await db.matches.update_one(
                                {"id": match_id},
                                {"$set": {
                                    "live_score": {"scores": scores, "updated_at": now_iso},
                                    "status_text": data.get("status", ""),
                                    "updated_at": now_iso,
                                }}
                            )
                            self._last_scores[match_id] = {
                                "scores": [f"{s['inning']}: {s['r']}/{s['w']} ({s['o']} ov)" for s in scores[:2]],
                                "updated_at": now_iso,
                            }

                    # Match completed → auto-stop + mark completed in DB
                    if is_ended:
                        await db.matches.update_one(
                            {"id": match_id},
                            {"$set": {"status": "completed", "updated_at": now_iso}}
                        )
                        self._stopped_reason[match_id] = "match_completed"
                        logger.info(f"ScoreFetcher: STOPPED (match completed) for match {match_id}")
                        break

            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.error(f"ScoreFetcher error for {match_id}: {e}")

            # Wait 15 seconds
            try:
                await asyncio.sleep(FETCH_INTERVAL)
            except asyncio.CancelledError:
                raise

        # Cleanup
        self._tasks.pop(match_id, None)


# Singleton
score_fetcher = MatchScoreFetcher()
