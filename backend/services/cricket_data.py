"""
Bharat 11 - Unified Cricket Data Service
PRIMARY: Cricbuzz HTML scraping (unlimited, no key)
FALLBACK: CricketData.org REST API (100 calls/day, free key)

Provides: match list, live scores, match status
Auto-pipeline: fetch → create matches → create contests → update scores
"""
import asyncio
import logging
import re
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# ==================== TEAM MAPPINGS ====================

IPL_TEAMS = {
    "Mumbai Indians": "MI", "Chennai Super Kings": "CSK",
    "Royal Challengers Bangalore": "RCB", "Royal Challengers Bengaluru": "RCB",
    "Kolkata Knight Riders": "KKR", "Delhi Capitals": "DC",
    "Punjab Kings": "PBKS", "Rajasthan Royals": "RR",
    "Sunrisers Hyderabad": "SRH", "Gujarat Titans": "GT",
    "Lucknow Super Giants": "LSG",
    "MI": "MI", "CSK": "CSK", "RCB": "RCB", "KKR": "KKR",
    "DC": "DC", "PBKS": "PBKS", "RR": "RR", "SRH": "SRH",
    "GT": "GT", "LSG": "LSG",
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/120.0'
}


def _get_short_name(name: str) -> str:
    """Get IPL short name or first 3 chars."""
    name = name.strip()
    if name in IPL_TEAMS:
        return IPL_TEAMS[name]
    for full, short in IPL_TEAMS.items():
        if full.lower() in name.lower() or name.lower() in full.lower():
            return short
    return name[:3].upper()


def _parse_match_status(status_text: str) -> str:
    """Convert status text to our status enum."""
    s = status_text.lower().strip()
    if any(w in s for w in ['won', 'drawn', 'tied', 'no result', 'abandoned']):
        return 'completed'
    if any(w in s for w in ['live', 'batting', 'bowling', 'break', 'innings']):
        return 'live'
    if any(w in s for w in ['preview', 'upcoming', 'starts', 'toss']):
        return 'upcoming'
    return 'upcoming'


# ==================== CRICBUZZ SCRAPER ====================

class CricbuzzScraper:
    """Scrapes Cricbuzz for live match data. No API key needed."""

    BASE_URL = "https://www.cricbuzz.com"

    def fetch_matches(self) -> List[Dict[str, Any]]:
        """Fetch current matches from Cricbuzz live scores page."""
        try:
            r = requests.get(
                f"{self.BASE_URL}/cricket-match/live-scores",
                headers=HEADERS, timeout=10
            )
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            
            links = soup.find_all('a', href=lambda x: x and '/live-cricket-scores/' in str(x))
            
            matches = []
            seen_ids = set()
            
            for link in links:
                href = link.get('href', '')
                text = link.text.strip()
                parts = href.split('/')
                cb_id = parts[2] if len(parts) > 2 else ''
                
                if cb_id in seen_ids or not cb_id:
                    continue
                seen_ids.add(cb_id)
                
                # Parse teams and status
                text_parts = text.split(' - ')
                teams_part = text_parts[0]
                status_text = text_parts[1].strip() if len(text_parts) > 1 else 'Preview'
                
                team_split = re.split(r'\s+vs\s+', teams_part, maxsplit=1)
                team_a_name = team_split[0].strip()
                team_b_raw = team_split[1].strip() if len(team_split) > 1 else ''
                
                # Clean team_b (remove "2nd Match" etc)
                team_b_name = re.sub(r'\d+\w*\s+Match.*$', '', team_b_raw).strip()
                if not team_b_name:
                    team_b_name = team_b_raw
                
                is_ipl = 'indian-premier-league' in href or 'ipl' in href.lower()
                
                matches.append({
                    'source': 'cricbuzz',
                    'source_id': cb_id,
                    'team_a': {'name': team_a_name, 'short_name': _get_short_name(team_a_name)},
                    'team_b': {'name': team_b_name, 'short_name': _get_short_name(team_b_name)},
                    'status': _parse_match_status(status_text),
                    'status_text': status_text,
                    'is_ipl': is_ipl,
                    'slug': href,
                    'url': f"{self.BASE_URL}{href}",
                })
            
            logger.info(f"Cricbuzz: fetched {len(matches)} matches")
            return matches
            
        except Exception as e:
            logger.error(f"Cricbuzz fetch failed: {e}")
            return []

    def fetch_match_score(self, slug: str) -> Optional[Dict[str, Any]]:
        """Fetch detailed score for a specific match."""
        try:
            url = f"{self.BASE_URL}{slug}" if not slug.startswith('http') else slug
            r = requests.get(url, headers=HEADERS, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Extract score from meta description or page content
            meta = soup.find('meta', attrs={'name': 'description'})
            desc = meta.get('content', '') if meta else ''
            
            # Extract title for match info
            title = soup.find('title')
            title_text = title.text if title else ''
            
            return {
                'source': 'cricbuzz',
                'description': desc[:200],
                'title': title_text[:100],
                'raw_html_size': len(r.text)
            }
        except Exception as e:
            logger.error(f"Cricbuzz score fetch failed: {e}")
            return None


# ==================== CRICKETDATA.ORG API ====================

class CricketDataAPI:
    """CricketData.org REST API. Premium tier (500 calls/day)."""

    BASE_URL = "https://api.cricapi.com/v1"

    def __init__(self):
        self.api_key = None
        self._hits_today = 0
        self._hits_limit = 500

    def _get_key(self):
        if self.api_key is None:
            from config.settings import settings
            self.api_key = settings.CRICKET_API_KEY or os.environ.get("CRICKET_API_KEY", "")
        return self.api_key

    def _call(self, endpoint: str, params: dict = None) -> Optional[dict]:
        """Make API call with key."""
        key = self._get_key()
        if not key:
            logger.warning("CRICKET_API_KEY not set")
            return None
        try:
            p = {"apikey": key, **(params or {})}
            r = requests.get(f"{self.BASE_URL}/{endpoint}", params=p, timeout=15)
            r.raise_for_status()
            data = r.json()
            # Track API usage
            info = data.get("info", {})
            self._hits_today = info.get("hitsToday", self._hits_today)
            self._hits_limit = info.get("hitsLimit", self._hits_limit)
            if data.get("status") != "success":
                error_info = info if info else data
                logger.error(f"CricketData API error: status={data.get('status')}, info={error_info}")
                # Check if rate limited
                if self._hits_today >= self._hits_limit:
                    logger.warning(f"API rate limit reached: {self._hits_today}/{self._hits_limit}")
                return None
            return data
        except Exception as e:
            logger.error(f"CricketData API failed: {e}")
            return None

    def fetch_matches(self) -> List[Dict[str, Any]]:
        """Fetch current matches."""
        data = self._call("currentMatches")
        if not data:
            return []

        matches = []
        for m in data.get("data", []):
            team_info = m.get("teamInfo", [])
            if len(team_info) < 2:
                continue

            t1_name = team_info[0].get("name", "?")
            t1_short = team_info[0].get("shortname", _get_short_name(t1_name))
            t2_name = team_info[1].get("name", "?")
            t2_short = team_info[1].get("shortname", _get_short_name(t2_name))

            status_text = m.get("status", "")
            match_started = m.get("matchStarted", False)
            match_ended = m.get("matchEnded", False)

            if match_ended:
                match_status = "completed"
            elif match_started:
                match_status = "live"
            else:
                match_status = "upcoming"

            scores = []
            for s in m.get("score", []):
                scores.append({
                    "inning": s.get("inning", ""),
                    "runs": s.get("r", 0),
                    "wickets": s.get("w", 0),
                    "overs": s.get("o", 0)
                })

            name_str = m.get("name", "")
            is_ipl = any(k in name_str.lower() for k in ['ipl', 'indian premier league'])
            # Also check team names against IPL teams
            if not is_ipl:
                is_ipl = (
                    any(t1_name.lower() in k.lower() or k.lower() in t1_name.lower() for k in IPL_TEAMS)
                    and any(t2_name.lower() in k.lower() or k.lower() in t2_name.lower() for k in IPL_TEAMS)
                )

            match_status = "completed" if match_ended else ("live" if match_started else "upcoming")

            matches.append({
                'source': 'cricketdata',
                'source_id': m.get("id", ""),
                'team_a': {'name': t1_name, 'short_name': t1_short},
                'team_b': {'name': t2_name, 'short_name': t2_short},
                'status': match_status,
                'status_text': status_text,
                'is_ipl': is_ipl,
                'scores': scores,
                'venue': m.get("venue", ""),
                'date': m.get("dateTimeGMT", ""),
                'match_type': m.get("matchType", ""),
            })

        logger.info(f"CricketData: fetched {len(matches)} matches (API call used)")
        return matches

    def fetch_scorecard(self, cricapi_match_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch detailed scorecard for a match. PREMIUM API.
        Returns full batting/bowling/catching/extras per innings.
        """
        data = self._call("match_scorecard", {"id": cricapi_match_id})
        if not data:
            return None
        return data.get("data")

    def fetch_squad(self, cricapi_match_id: str) -> Optional[Dict[str, Any]]:
        """Fetch squad/player list for a match. PREMIUM API."""
        data = self._call("match_squad", {"id": cricapi_match_id})
        if not data:
            return None
        return data.get("data")

    def fetch_match_info(self, cricapi_match_id: str) -> Optional[Dict[str, Any]]:
        """Fetch detailed match info (toss, winner, series_id). LOT2 API 5."""
        data = self._call("match_info", {"id": cricapi_match_id})
        if not data:
            return None
        return data.get("data")

    def fetch_match_points(self, cricapi_match_id: str) -> Optional[Dict[str, Any]]:
        """Fetch fantasy points per player per innings. LOT3 API 2. SLOW ~2s."""
        data = self._call("match_points", {"id": cricapi_match_id, "ruleset": "0"})
        if not data:
            return None
        return data.get("data")

    def fetch_series_points(self, series_id: str) -> Optional[list]:
        """Fetch series point table (team standings). LOT3 API 3."""
        data = self._call("series_points", {"id": series_id})
        if not data:
            return None
        return data.get("data")

    def fetch_series_info(self, series_id: str) -> Optional[Dict[str, Any]]:
        """Fetch full series info + match list. LOT2 API 4."""
        data = self._call("series_info", {"id": series_id})
        if not data:
            return None
        return data.get("data")

    def fetch_cric_score(self) -> Optional[list]:
        """Lightweight live score feed. LOT1 API 2. ms: fixture/result/live."""
        data = self._call("cricScore")
        if not data:
            return None
        return data.get("data")

    def fetch_player_info(self, player_id: str) -> Optional[Dict[str, Any]]:
        """Fetch player profile + career stats. LOT5 API 1."""
        data = self._call("players_info", {"id": player_id})
        if not data:
            return None
        return data.get("data")

    def fetch_match_bbb(self, cricapi_match_id: str) -> Optional[Dict[str, Any]]:
        """Fetch ball-by-ball data (extras/penalties). LOT4 API 1. IN TESTING."""
        data = self._call("match_bbb", {"id": cricapi_match_id})
        if not data:
            return None
        return data.get("data")

    def fetch_series_squad(self, series_id: str) -> Optional[list]:
        """Fetch all team squads for entire series. LOT5 API 3. ~53KB response."""
        data = self._call("series_squad", {"id": series_id})
        if not data:
            return None
        return data.get("data")

    def get_api_info(self) -> dict:
        """Get API usage info without wasting a call."""
        return {
            "hits_today": self._hits_today,
            "hits_limit": self._hits_limit,
            "remaining": self._hits_limit - self._hits_today,
        }


# ==================== UNIFIED SERVICE ====================

class UnifiedCricketService:
    """
    Unified cricket data service.
    PRIMARY: Cricbuzz (unlimited, scraping)
    FALLBACK: CricketData.org (100/day, REST API)
    
    Cache: In-memory with TTL to minimize calls.
    """

    def __init__(self):
        self.cricbuzz = CricbuzzScraper()
        self.cricketdata = CricketDataAPI()
        self._cache: Dict[str, Any] = {}
        self._cache_time: Dict[str, float] = {}
        self._cache_ttl = 60  # 60 seconds cache
        self._last_source = "none"

    def _is_cached(self, key: str) -> bool:
        return key in self._cache and \
            (datetime.now(timezone.utc).timestamp() - self._cache_time.get(key, 0)) < self._cache_ttl

    def _set_cache(self, key: str, value: Any):
        self._cache[key] = value
        self._cache_time[key] = datetime.now(timezone.utc).timestamp()
        # Evict old entries
        if len(self._cache) > 50:
            oldest = min(self._cache_time, key=self._cache_time.get)
            self._cache.pop(oldest, None)
            self._cache_time.pop(oldest, None)

    async def get_live_matches(self, ipl_only: bool = False) -> Dict[str, Any]:
        """
        Get current matches. Tries Cricbuzz first, falls back to CricketData.
        Returns: {matches: [], source: str, cached: bool}
        """
        cache_key = f"matches_ipl_{ipl_only}"
        if self._is_cached(cache_key):
            return {**self._cache[cache_key], "cached": True}

        # Try Cricbuzz first (unlimited)
        loop = asyncio.get_running_loop()
        matches = await loop.run_in_executor(None, self.cricbuzz.fetch_matches)

        if matches:
            self._last_source = "cricbuzz"
            if ipl_only:
                matches = [m for m in matches if m.get('is_ipl')]
            result = {"matches": matches, "source": "cricbuzz", "cached": False, "count": len(matches)}
            self._set_cache(cache_key, result)
            return result

        # Fallback to CricketData.org
        logger.info("Cricbuzz failed, falling back to CricketData.org")
        matches = await loop.run_in_executor(None, self.cricketdata.fetch_matches)

        if matches:
            self._last_source = "cricketdata"
            if ipl_only:
                matches = [m for m in matches if m.get('is_ipl')]
            result = {"matches": matches, "source": "cricketdata", "cached": False, "count": len(matches)}
            self._set_cache(cache_key, result)
            return result

        # Both failed
        self._last_source = "none"
        return {"matches": [], "source": "none", "cached": False, "count": 0, "error": "Both sources failed"}

    async def get_match_score(self, slug: str) -> Optional[Dict]:
        """Get detailed score for a Cricbuzz match."""
        cache_key = f"score_{slug}"
        if self._is_cached(cache_key):
            return self._cache[cache_key]

        loop = asyncio.get_running_loop()
        score = await loop.run_in_executor(None, self.cricbuzz.fetch_match_score, slug)
        if score:
            self._set_cache(cache_key, score)
        return score

    async def get_scorecard(self, cricapi_match_id: str) -> Optional[Dict]:
        """Get detailed scorecard from CricketData.org Premium API."""
        cache_key = f"scorecard_{cricapi_match_id}"
        if self._is_cached(cache_key):
            return self._cache[cache_key]

        loop = asyncio.get_running_loop()
        data = await loop.run_in_executor(None, self.cricketdata.fetch_scorecard, cricapi_match_id)
        if data:
            self._set_cache(cache_key, data)
        return data

    async def get_squad(self, cricapi_match_id: str) -> Optional[Dict]:
        """Get squad data from CricketData.org Premium API."""
        cache_key = f"squad_{cricapi_match_id}"
        if self._is_cached(cache_key):
            return self._cache[cache_key]

        loop = asyncio.get_running_loop()
        data = await loop.run_in_executor(None, self.cricketdata.fetch_squad, cricapi_match_id)
        if data:
            self._set_cache(cache_key, data)
        return data

    async def get_match_info(self, cricapi_match_id: str) -> Optional[Dict]:
        """Get detailed match info (toss, winner) from CricketData.org."""
        cache_key = f"match_info_{cricapi_match_id}"
        if self._is_cached(cache_key):
            return self._cache[cache_key]
        loop = asyncio.get_running_loop()
        data = await loop.run_in_executor(None, self.cricketdata.fetch_match_info, cricapi_match_id)
        if data:
            self._set_cache(cache_key, data)
        return data

    async def get_match_points(self, cricapi_match_id: str) -> Optional[Dict]:
        """Get fantasy points per player. SLOW API (~2s) — cache heavily."""
        cache_key = f"match_points_{cricapi_match_id}"
        if self._is_cached(cache_key):
            return self._cache[cache_key]
        loop = asyncio.get_running_loop()
        data = await loop.run_in_executor(None, self.cricketdata.fetch_match_points, cricapi_match_id)
        if data:
            # Cache for 5 min (fantasy points don't change fast)
            self._cache[cache_key] = data
            self._cache_time[cache_key] = datetime.now(timezone.utc).timestamp() + 240  # extra 4 min
        return data

    async def get_series_points(self, series_id: str) -> Optional[list]:
        """Get series point table (team standings)."""
        cache_key = f"series_points_{series_id}"
        if self._is_cached(cache_key):
            return self._cache[cache_key]
        loop = asyncio.get_running_loop()
        data = await loop.run_in_executor(None, self.cricketdata.fetch_series_points, series_id)
        if data:
            # Cache 30 min
            self._cache[cache_key] = data
            self._cache_time[cache_key] = datetime.now(timezone.utc).timestamp() + 1740
        return data

    async def get_series_info(self, series_id: str) -> Optional[Dict]:
        """Get full series info + match schedule."""
        cache_key = f"series_info_{series_id}"
        if self._is_cached(cache_key):
            return self._cache[cache_key]
        loop = asyncio.get_running_loop()
        data = await loop.run_in_executor(None, self.cricketdata.fetch_series_info, series_id)
        if data:
            # Cache 1 hour
            self._cache[cache_key] = data
            self._cache_time[cache_key] = datetime.now(timezone.utc).timestamp() + 3540
        return data

    async def get_cric_score(self) -> Optional[list]:
        """Get lightweight live score feed."""
        cache_key = "cric_score_all"
        if self._is_cached(cache_key):
            return self._cache[cache_key]
        loop = asyncio.get_running_loop()
        data = await loop.run_in_executor(None, self.cricketdata.fetch_cric_score)
        if data:
            self._set_cache(cache_key, data)
        return data

    async def get_player_info(self, player_id: str) -> Optional[Dict]:
        """Get player profile with career stats."""
        cache_key = f"player_{player_id}"
        if self._is_cached(cache_key):
            return self._cache[cache_key]
        loop = asyncio.get_running_loop()
        data = await loop.run_in_executor(None, self.cricketdata.fetch_player_info, player_id)
        if data:
            # Cache 1 hour
            self._cache[cache_key] = data
            self._cache_time[cache_key] = datetime.now(timezone.utc).timestamp() + 3540
        return data

    async def get_series_squad(self, series_id: str) -> Optional[list]:
        """Get all team squads for entire series."""
        cache_key = f"series_squad_{series_id}"
        if self._is_cached(cache_key):
            return self._cache[cache_key]
        loop = asyncio.get_running_loop()
        data = await loop.run_in_executor(None, self.cricketdata.fetch_series_squad, series_id)
        if data:
            # Cache 1 hour (53KB response)
            self._cache[cache_key] = data
            self._cache_time[cache_key] = datetime.now(timezone.utc).timestamp() + 3540
        return data

    async def get_match_bbb(self, cricapi_match_id: str) -> Optional[Dict]:
        """Get ball-by-ball extras/penalty data (LOT4)."""
        cache_key = f"bbb_{cricapi_match_id}"
        if self._is_cached(cache_key):
            return self._cache[cache_key]
        loop = asyncio.get_running_loop()
        data = await loop.run_in_executor(None, self.cricketdata.fetch_match_bbb, cricapi_match_id)
        if data:
            self._set_cache(cache_key, data)
        return data


    @property
    def is_connected(self) -> bool:
        return self._last_source != "none"

    @property
    def last_source(self) -> str:
        return self._last_source

    def get_status(self) -> dict:
        api_info = self.cricketdata.get_api_info()
        return {
            "connected": self.is_connected,
            "last_source": self._last_source,
            "cache_size": len(self._cache),
            "cricketdata_key_set": bool(self.cricketdata._get_key()),
            "api_hits_today": api_info.get("hits_today", 0),
            "api_hits_limit": api_info.get("hits_limit", 500),
            "api_hits_remaining": api_info.get("remaining", 0),
        }


# Singleton
cricket_service = UnifiedCricketService()
