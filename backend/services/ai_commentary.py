"""
Bharat 11 — AI Cricket Commentary Service (ELITE Edition)
Generates structured, dramatic, Cricbuzz-beating commentary from scorecard data.
Output: Structured sections (Match Pulse, Key Moments, Star Performer, Turning Point, Verdict)
"""
import os
import json
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


async def generate_ai_commentary(scorecard_data: dict, match_info: dict = None) -> dict:
    """
    Generate STRUCTURED AI commentary. Returns dict with sections, not just a flat list.
    {
      "match_pulse": { ... },
      "key_moments": [ ... ],
      "star_performers": [ ... ],
      "turning_point": { ... },
      "verdict": { ... },
      "raw_commentary": [ ... ]
    }
    """
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage

        api_key = os.environ.get("EMERGENT_LLM_KEY", "")
        if not api_key:
            return _generate_fallback_structured(scorecard_data, match_info)

        scorecard = scorecard_data.get("scorecard", [])
        if not scorecard:
            return {"match_pulse": None, "key_moments": [], "star_performers": [], "turning_point": None, "verdict": None, "raw_commentary": []}

        # Build rich match summary
        summary_parts = []
        match_name = match_info.get("name", "") if match_info else ""
        venue = match_info.get("venue", "") if match_info else ""
        status = match_info.get("status", "") if match_info else ""
        toss_winner = match_info.get("toss_winner", "") if match_info else ""
        toss_choice = match_info.get("toss_choice", "") if match_info else ""

        if match_name:
            summary_parts.append(f"Match: {match_name}")
        if venue:
            summary_parts.append(f"Venue: {venue}")
        if status:
            summary_parts.append(f"Result: {status}")
        if toss_winner:
            summary_parts.append(f"Toss: {toss_winner} won toss, chose to {toss_choice}")

        for idx, inn in enumerate(scorecard):
            inning_name = inn.get("inning", f"Innings {idx+1}")
            batting = inn.get("batting", [])
            bowling = inn.get("bowling", [])
            extras = inn.get("extras", {})
            totals = inn.get("totals", {})
            _ = extras  # used for future expansion

            bat_lines = []
            for b in batting:
                runs = b.get("r", 0)
                balls = b.get("b", 0)
                fours = b.get("4s", 0)
                sixes = b.get("6s", 0)
                sr = b.get("sr", "0")
                dismissal = b.get("dismissal", "not out")
                bat_lines.append(f"{b.get('batsman','?')} {runs}({balls}) 4s:{fours} 6s:{sixes} SR:{sr} [{dismissal}]")

            bowl_lines = []
            for bw in bowling:
                bowl_lines.append(f"{bw.get('bowler','?')} {bw.get('o','0')}ov {bw.get('m',0)}m {bw.get('w',0)}/{bw.get('r',0)} eco:{bw.get('eco','0')}")

            total_str = ""
            if totals:
                total_str = f"Total: {totals.get('R', '?')}/{totals.get('W', '?')} in {totals.get('O', '?')} overs"

            summary_parts.append(f"\n=== {inning_name} ===")
            if total_str:
                summary_parts.append(total_str)
            summary_parts.append("Batting:\n" + "\n".join(bat_lines))
            summary_parts.append("Bowling:\n" + "\n".join(bowl_lines))

        scorecard_summary = "\n".join(summary_parts)

        chat = LlmChat(
            api_key=api_key,
            session_id=f"bharat11_comm_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            system_message="""You are the GREATEST IPL commentator ever — a fusion of Harsha Bhogle's poetry, Ravi Shastri's energy, and Navjot Singh Sidhu's wit. You generate STRUCTURED commentary that reads like a thriller novel.

CRITICAL: You MUST return ONLY valid JSON. No text before or after. The JSON structure:
{
  "match_pulse": {
    "headline": "One-line dramatic headline (max 60 chars)",
    "sub": "2-line match summary with key stat",
    "team_a_score": "185/4 (20 ov)",
    "team_b_score": "178/8 (20 ov)",
    "winner_short": "CSK"
  },
  "key_moments": [
    {
      "over": "6.4",
      "event_type": "six|four|wicket|milestone|bowling|dramatic",
      "title": "Short dramatic title (max 30 chars)",
      "description": "One vivid line mixing Hindi+English naturally. Use phrases like 'Kya shot hai!', 'Dhamakedar!', 'Gone! Gaya!', 'Zabardast!'. Max 80 chars.",
      "player": "Player Name",
      "impact": "high|medium|low"
    }
  ],
  "star_performers": [
    {
      "name": "Player Name",
      "role": "batting|bowling|allround",
      "headline": "Dramatic one-liner about performance",
      "stats": "71(36) | 4x4 6x6 | SR 197.2",
      "rating": 9.5
    }
  ],
  "turning_point": {
    "over": "14.3",
    "title": "The Moment That Changed Everything",
    "description": "2-3 lines describing THE moment that swung the match. Be dramatic, use Hindi phrases.",
    "player": "Player Name"
  },
  "verdict": {
    "headline": "Epic one-line match verdict",
    "description": "3-4 lines of dramatic match conclusion. Like a movie climax narration. Mix Hindi naturally. End with something quotable.",
    "mood": "thriller|domination|upset|classic|heartbreak"
  }
}

RULES:
- key_moments MUST have 10-15 items covering BOTH innings
- star_performers MUST have 3-5 players
- Use ACTUAL player names and REAL stats from scorecard
- Hindi mixing should feel natural: "What a knock yaar!", "Paaji ne toh tod diya!", "GONE! Ekdum clean bold!"
- Every description must be vivid and visual — make readers SEE the shot/wicket
- Overs should be accurate based on batting order (early=1-6, middle=7-15, death=16-20)
- event_type must be exactly one of: six, four, wicket, milestone, bowling, dramatic
- rating must be float between 1.0 and 10.0
- mood must be exactly one of: thriller, domination, upset, classic, heartbreak
- DO NOT include any text outside the JSON object"""
        ).with_model("openai", "gpt-5.2")

        user_msg = UserMessage(text=f"Generate STRUCTURED IPL commentary JSON for this match:\n\n{scorecard_summary}")
        response = await chat.send_message(user_msg)

        if not response:
            return _generate_fallback_structured(scorecard_data, match_info)

        # Parse JSON response
        try:
            # Clean any markdown wrapping
            clean = response.strip()
            if clean.startswith("```"):
                clean = clean.split("\n", 1)[1] if "\n" in clean else clean[3:]
                if clean.endswith("```"):
                    clean = clean[:-3]
                clean = clean.strip()
            if clean.startswith("json"):
                clean = clean[4:].strip()

            result = json.loads(clean)

            # Also generate flat raw_commentary for backwards compat
            raw = []
            for moment in result.get("key_moments", []):
                raw.append({
                    "type": moment.get("event_type", "general"),
                    "text": f"[{moment.get('over', '')}] {moment.get('title', '')} — {moment.get('description', '')}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            result["raw_commentary"] = raw
            return result

        except json.JSONDecodeError:
            logger.warning("AI returned non-JSON, falling back to line parsing")
            # Fallback: parse as lines (old behavior)
            lines = [ln.strip() for ln in response.strip().split("\n") if ln.strip()]
            items = []
            for line in lines:
                item_type = "general"
                if any(w in line.upper() for w in ["SIX", "MASSIVE"]):
                    item_type = "six"
                elif "FOUR" in line.upper() or "BOUNDARY" in line.upper():
                    item_type = "four"
                elif any(w in line.upper() for w in ["WICKET", "GONE", "OUT!", "BOWLED", "CAUGHT"]):
                    item_type = "wicket"
                elif any(w in line.upper() for w in ["FIFTY", "CENTURY", "100", "50"]):
                    item_type = "milestone"
                elif any(w in line.upper() for w in ["WON", "WIN", "RESULT", "CHAMPION"]):
                    item_type = "result"
                items.append({"type": item_type, "text": line, "timestamp": datetime.now(timezone.utc).isoformat()})
            return {"match_pulse": None, "key_moments": [], "star_performers": [], "turning_point": None, "verdict": None, "raw_commentary": items}

    except Exception as e:
        logger.error(f"AI commentary error: {e}")
        return _generate_fallback_structured(scorecard_data, match_info)


def _generate_fallback_structured(scorecard_data: dict, match_info: dict = None) -> dict:
    """Fallback: generate structured commentary from raw scorecard without AI."""
    scorecard = scorecard_data.get("scorecard", [])
    status = match_info.get("status", "") if match_info else ""

    key_moments = []
    star_performers = []
    team_scores = []

    for idx, inn in enumerate(scorecard):
        batting = inn.get("batting", [])
        bowling = inn.get("bowling", [])
        totals = inn.get("totals", {})

        if totals:
            team_scores.append(f"{totals.get('R', '?')}/{totals.get('W', '?')} ({totals.get('O', '?')} ov)")

        for b in batting:
            runs = int(b.get("r", 0))
            balls = int(b.get("b", 0))
            fours = int(b.get("4s", 0))
            sixes = int(b.get("6s", 0))
            sr = b.get("sr", "0")
            dismissal = b.get("dismissal", "not out")
            name = b.get("batsman", "?")

            if runs >= 100:
                key_moments.append({
                    "over": "?", "event_type": "milestone",
                    "title": f"CENTURY! {name}",
                    "description": f"Kya innings! {name} ne {runs} runs thoke {balls} balls me! ({fours}x4, {sixes}x6) Zabardast!",
                    "player": name, "impact": "high"
                })
                star_performers.append({
                    "name": name, "role": "batting",
                    "headline": f"Sheer class! {name} smashes a century!",
                    "stats": f"{runs}({balls}) | {fours}x4 {sixes}x6 | SR {sr}",
                    "rating": min(10.0, 8.0 + (runs - 100) * 0.02)
                })
            elif runs >= 50:
                key_moments.append({
                    "over": "?", "event_type": "milestone",
                    "title": f"FIFTY! {name}",
                    "description": f"{name} ne half-century maari! {runs}({balls}) with {fours} fours aur {sixes} sixes!",
                    "player": name, "impact": "high"
                })
                star_performers.append({
                    "name": name, "role": "batting",
                    "headline": f"Outstanding knock by {name}!",
                    "stats": f"{runs}({balls}) | {fours}x4 {sixes}x6 | SR {sr}",
                    "rating": min(9.5, 7.0 + (runs - 50) * 0.04)
                })

            if sixes >= 3:
                key_moments.append({
                    "over": "?", "event_type": "six",
                    "title": f"{name} on FIRE!",
                    "description": f"Dhamakedar! {name} ne {sixes} SIXES lagaye apni {runs} ki innings me! Stadium hilaake rakh diya!",
                    "player": name, "impact": "high"
                })

            if dismissal and dismissal != "not out":
                imp = "high" if runs >= 30 else "medium" if runs >= 15 else "low"
                key_moments.append({
                    "over": "?", "event_type": "wicket",
                    "title": f"OUT! {name} {runs}({balls})",
                    "description": f"Gone! {name} {dismissal}. {runs} runs ki innings khatam!",
                    "player": name, "impact": imp
                })

        for bw in bowling:
            wickets = int(bw.get("w", 0))
            bw_runs = bw.get("r", "?")
            overs = bw.get("o", "?")
            eco = bw.get("eco", "?")
            bowler_name = bw.get("bowler", "?")

            if wickets >= 3:
                key_moments.append({
                    "over": "?", "event_type": "bowling",
                    "title": f"{bowler_name} destroys!",
                    "description": f"Kya bowling! {bowler_name} ne {wickets} wickets jhakke in {overs} overs ({bw_runs} runs, eco {eco})!",
                    "player": bowler_name, "impact": "high"
                })
                star_performers.append({
                    "name": bowler_name, "role": "bowling",
                    "headline": f"Lethal spell by {bowler_name}!",
                    "stats": f"{wickets}/{bw_runs} ({overs} ov) | Eco {eco}",
                    "rating": min(9.5, 7.0 + wickets * 0.5)
                })

    match_pulse = None
    if team_scores:
        match_pulse = {
            "headline": status if status else "Match in progress...",
            "sub": f"A {'thriller' if len(team_scores) >= 2 else 'developing'} IPL encounter!",
            "team_a_score": team_scores[0] if len(team_scores) > 0 else "",
            "team_b_score": team_scores[1] if len(team_scores) > 1 else "",
            "winner_short": ""
        }

    verdict = None
    if status:
        verdict = {
            "headline": status,
            "description": f"What a match! {status}. IPL at its absolute best!",
            "mood": "classic"
        }

    # Build raw_commentary for backwards compatibility
    raw = []
    for m in key_moments:
        raw.append({
            "type": m["event_type"],
            "text": f"{m['title']} — {m['description']}",
            "timestamp": ""
        })

    return {
        "match_pulse": match_pulse,
        "key_moments": key_moments,
        "star_performers": star_performers[:5],
        "turning_point": key_moments[0] if key_moments else None,
        "verdict": verdict,
        "raw_commentary": raw
    }
