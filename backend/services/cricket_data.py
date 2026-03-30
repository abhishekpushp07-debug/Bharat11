"""
CrickPredict - Live Cricket Data Service
Uses pycricbuzz for real Cricbuzz data with graceful fallback.
When deployed to production (with internet access), this provides real live scores.
In restricted environments, returns cached/demo data.
"""
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, List, Any

logger = logging.getLogger(__name__)

# Try to import pycricbuzz
try:
    from pycricbuzz import Cricbuzz
    CRICBUZZ_AVAILABLE = True
except ImportError:
    CRICBUZZ_AVAILABLE = False
    logger.warning("pycricbuzz not installed. Live cricket data unavailable.")


class CricketDataService:
    """
    Live cricket data service using Cricbuzz.
    - Fetches real matches, live scores, scorecards
    - Caches data to reduce API calls (max 100 entries)
    - Graceful fallback when Cricbuzz unreachable
    """

    MAX_CACHE_ENTRIES = 100

    def __init__(self):
        self._cb = Cricbuzz() if CRICBUZZ_AVAILABLE else None
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = 30  # seconds
        self._last_fetch: Dict[str, float] = {}
        self._connected = False

    def _is_cache_valid(self, key: str) -> bool:
        last = self._last_fetch.get(key, 0)
        return (datetime.now(timezone.utc).timestamp() - last) < self._cache_ttl

    def _evict_stale_cache(self):
        """Remove expired entries if cache exceeds max size."""
        if len(self._cache) <= self.MAX_CACHE_ENTRIES:
            return
        now = datetime.now(timezone.utc).timestamp()
        stale_keys = [k for k, t in self._last_fetch.items() if (now - t) > self._cache_ttl]
        for k in stale_keys:
            self._cache.pop(k, None)
            self._last_fetch.pop(k, None)

    async def fetch_live_matches(self) -> List[Dict]:
        """
        Fetch all current matches from Cricbuzz.
        Returns list of match dicts with id, teams, status, scores.
        """
        cache_key = "matches"
        if self._is_cache_valid(cache_key):
            return self._cache.get(cache_key, [])

        if not self._cb:
            return []

        try:
            # Run sync pycricbuzz in executor to not block async loop
            loop = asyncio.get_running_loop()
            raw_matches = await loop.run_in_executor(None, self._cb.matches)
            self._connected = True

            matches = []
            for m in raw_matches:
                match = self._parse_match(m)
                if match:
                    matches.append(match)

            self._cache[cache_key] = matches
            self._last_fetch[cache_key] = datetime.now(timezone.utc).timestamp()
            self._evict_stale_cache()
            logger.info(f"Fetched {len(matches)} matches from Cricbuzz")
            return matches

        except Exception as e:
            logger.warning(f"Cricbuzz fetch failed: {e}")
            self._connected = False
            return self._cache.get(cache_key, [])

    async def fetch_live_score(self, cricbuzz_match_id: str) -> Optional[Dict]:
        """
        Fetch live score for a specific match.
        """
        cache_key = f"score:{cricbuzz_match_id}"
        if self._is_cache_valid(cache_key):
            return self._cache.get(cache_key)

        if not self._cb:
            return None

        try:
            loop = asyncio.get_running_loop()
            raw = await loop.run_in_executor(None, self._cb.livescore, cricbuzz_match_id)
            self._connected = True

            score = self._parse_live_score(raw)
            self._cache[cache_key] = score
            self._last_fetch[cache_key] = datetime.now(timezone.utc).timestamp()
            self._evict_stale_cache()
            return score

        except Exception as e:
            logger.warning(f"Cricbuzz live score fetch failed for {cricbuzz_match_id}: {e}")
            return self._cache.get(cache_key)

    async def fetch_scorecard(self, cricbuzz_match_id: str) -> Optional[Dict]:
        """Fetch full scorecard for a match."""
        cache_key = f"scorecard:{cricbuzz_match_id}"
        if self._is_cache_valid(cache_key):
            return self._cache.get(cache_key)

        if not self._cb:
            return None

        try:
            loop = asyncio.get_running_loop()
            raw = await loop.run_in_executor(None, self._cb.scorecard, cricbuzz_match_id)
            self._connected = True
            self._cache[cache_key] = raw
            self._last_fetch[cache_key] = datetime.now(timezone.utc).timestamp()
            self._evict_stale_cache()
            return raw

        except Exception as e:
            logger.warning(f"Cricbuzz scorecard fetch failed: {e}")
            return self._cache.get(cache_key)

    def _parse_match(self, raw: Dict) -> Optional[Dict]:
        """Parse raw Cricbuzz match into our format."""
        try:
            match_id = raw.get("id", "")
            status_raw = raw.get("mchstate", "").lower()

            # Map Cricbuzz states to our states
            if "live" in status_raw or "progress" in status_raw or "innings" in status_raw:
                status = "live"
            elif "complete" in status_raw or "result" in status_raw:
                status = "completed"
            elif "upcoming" in status_raw or "toss" in status_raw:
                status = "upcoming"
            else:
                status = "upcoming"

            # Extract team names from match description
            mchdesc = raw.get("mchdesc", "")
            teams = mchdesc.split(" vs ") if " vs " in mchdesc else [mchdesc, ""]

            team_a_name = teams[0].strip() if len(teams) > 0 else "Team A"
            team_b_name = teams[1].strip() if len(teams) > 1 else "Team B"

            # Generate short names (first 2-3 chars or known abbreviations)
            IPL_TEAMS = {
                "Mumbai Indians": "MI", "Chennai Super Kings": "CSK",
                "Royal Challengers": "RCB", "Royal Challengers Bengaluru": "RCB",
                "Kolkata Knight Riders": "KKR", "Delhi Capitals": "DC",
                "Punjab Kings": "PBKS", "Sunrisers Hyderabad": "SRH",
                "Rajasthan Royals": "RR", "Gujarat Titans": "GT",
                "Lucknow Super Giants": "LSG",
                "India": "IND", "Australia": "AUS", "England": "ENG",
                "Pakistan": "PAK", "South Africa": "SA", "New Zealand": "NZ",
                "Sri Lanka": "SL", "Bangladesh": "BAN", "West Indies": "WI",
                "Afghanistan": "AFG", "Zimbabwe": "ZIM", "Ireland": "IRE",
            }

            def get_short(name):
                for full, short in IPL_TEAMS.items():
                    if full.lower() in name.lower():
                        return short
                return name[:3].upper()

            return {
                "cricbuzz_id": str(match_id),
                "team_a": {
                    "name": team_a_name,
                    "short_name": get_short(team_a_name)
                },
                "team_b": {
                    "name": team_b_name,
                    "short_name": get_short(team_b_name)
                },
                "series": raw.get("srs", ""),
                "match_number": raw.get("mnum", ""),
                "status": status,
                "status_text": raw.get("status", ""),
                "venue": raw.get("venue", {}).get("name", "") if isinstance(raw.get("venue"), dict) else raw.get("vcity", ""),
                "match_type": raw.get("type", "T20").upper()
            }
        except Exception as e:
            logger.warning(f"Error parsing match: {e}")
            return None

    def _parse_live_score(self, raw: Dict) -> Optional[Dict]:
        """Parse live score data."""
        try:
            innings = raw.get("innings", [])
            current = innings[-1] if innings else {}

            batting_team = current.get("batting_team", "")
            score = current.get("score", "0/0")
            overs = current.get("overs", "0.0")

            # Parse score components
            parts = score.split("/")
            runs = int(parts[0]) if parts else 0
            wickets = int(parts[1]) if len(parts) > 1 else 0

            # Parse batsmen
            batsmen = []
            for b in current.get("batsmen", []):
                batsmen.append({
                    "name": b.get("name", ""),
                    "runs": b.get("runs", 0),
                    "balls": b.get("balls", 0),
                    "fours": b.get("fours", 0),
                    "sixes": b.get("sixes", 0),
                    "strike_rate": b.get("strike_rate", "0.0")
                })

            # Parse bowler
            bowlers = []
            for b in current.get("bowlers", []):
                bowlers.append({
                    "name": b.get("name", ""),
                    "overs": b.get("overs", "0"),
                    "maidens": b.get("maidens", 0),
                    "runs": b.get("runs_conceded", 0),
                    "wickets": b.get("wickets", 0)
                })

            return {
                "batting_team": batting_team,
                "score": score,
                "runs": runs,
                "wickets": wickets,
                "overs": overs,
                "run_rate": current.get("runrate", "0.00"),
                "batsmen": batsmen,
                "bowlers": bowlers,
                "recent_balls": current.get("recent_balls", ""),
                "innings_count": len(innings),
                "all_innings": [
                    {
                        "batting_team": inn.get("batting_team", ""),
                        "score": inn.get("score", "0/0"),
                        "overs": inn.get("overs", "0.0")
                    }
                    for inn in innings
                ]
            }
        except Exception as e:
            logger.warning(f"Error parsing live score: {e}")
            return None

    @property
    def is_connected(self) -> bool:
        return self._connected


# Singleton instance
cricket_data_service = CricketDataService()
