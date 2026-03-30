"""
Bharat 11 — AI Cricket Commentary Service
Generates exciting ball-by-ball commentary from scorecard data using GPT-5.2.
"""
import os
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


async def generate_ai_commentary(scorecard_data: dict, match_info: dict = None) -> list:
    """
    Generate AI-powered exciting cricket commentary from scorecard data.
    Returns list of commentary items with type, text, and styling info.
    """
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage

        api_key = os.environ.get("EMERGENT_LLM_KEY", "")
        if not api_key:
            return _generate_fallback_commentary(scorecard_data)

        scorecard = scorecard_data.get("scorecard", [])
        if not scorecard:
            return []

        # Build compact summary for AI
        summary_parts = []
        match_name = match_info.get("name", "") if match_info else ""
        venue = match_info.get("venue", "") if match_info else ""
        if match_name:
            summary_parts.append(f"Match: {match_name}")
        if venue:
            summary_parts.append(f"Venue: {venue}")

        for idx, inn in enumerate(scorecard):
            inning_name = inn.get("inning", f"Innings {idx+1}")
            batting = inn.get("batting", [])
            bowling = inn.get("bowling", [])

            # Batting summary
            bat_lines = []
            for b in batting[:8]:
                runs = b.get("r", 0)
                balls = b.get("b", 0)
                fours = b.get("4s", 0)
                sixes = b.get("6s", 0)
                dismissal = b.get("dismissal", "not out")
                bat_lines.append(f"{b.get('batsman','?')} {runs}({balls}) 4s:{fours} 6s:{sixes} [{dismissal}]")

            # Bowling summary
            bowl_lines = []
            for bw in bowling[:5]:
                bowl_lines.append(f"{bw.get('bowler','?')} {bw.get('o','0')}ov {bw.get('w',0)}/{bw.get('r',0)} eco:{bw.get('eco','0')}")

            summary_parts.append(f"\n--- {inning_name} ---")
            summary_parts.append("Batting: " + " | ".join(bat_lines))
            summary_parts.append("Bowling: " + " | ".join(bowl_lines))

        scorecard_summary = "\n".join(summary_parts)

        chat = LlmChat(
            api_key=api_key,
            session_id=f"commentary_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M')}",
            system_message="""You are an ELECTRIC IPL cricket commentator like Harsha Bhogle and Ravi Shastri combined. Generate EXCITING ball-by-ball style commentary for this match. 

Rules:
- Output EXACTLY 12-15 lines of commentary
- Each line starts with an emoji: 🔥 for sixes, 💥 for fours, ❌ for wickets, ⭐ for milestones, 🏏 for general, 🎯 for bowling, 🏆 for match result
- Make it DRAMATIC: "WHAT A SHOT!", "GONE! Clean bowled!", "SIX! That's MASSIVE!"
- Include player names and actual stats from the scorecard
- Mix Hindi with English naturally (like "Kya shot hai!", "Dhamaka!")
- Cover: key wickets, big scores, bowling spells, match turning points, final result
- Each line should be max 80 chars
- NO introduction text, just pure commentary lines"""
        ).with_model("openai", "gpt-5.2")

        user_msg = UserMessage(text=f"Generate exciting IPL commentary for:\n{scorecard_summary}")
        response = await chat.send_message(user_msg)

        if not response:
            return _generate_fallback_commentary(scorecard_data)

        # Parse response into commentary items
        lines = [l.strip() for l in response.strip().split("\n") if l.strip()]
        items = []
        for line in lines:
            item_type = "general"
            if "🔥" in line or "SIX" in line.upper():
                item_type = "six"
            elif "💥" in line or "FOUR" in line.upper():
                item_type = "four"
            elif "❌" in line or "WICKET" in line.upper() or "GONE" in line.upper() or "OUT" in line.upper():
                item_type = "wicket"
            elif "⭐" in line or "50" in line or "100" in line or "FIFTY" in line.upper() or "CENTURY" in line.upper():
                item_type = "milestone"
            elif "🎯" in line:
                item_type = "bowling"
            elif "🏆" in line or "WON" in line.upper() or "WIN" in line.upper():
                item_type = "result"

            items.append({"type": item_type, "text": line, "timestamp": datetime.now(timezone.utc).isoformat()})

        return items

    except Exception as e:
        logger.error(f"AI commentary error: {e}")
        return _generate_fallback_commentary(scorecard_data)


def _generate_fallback_commentary(scorecard_data: dict) -> list:
    """Fallback: generate commentary from raw scorecard without AI."""
    items = []
    scorecard = scorecard_data.get("scorecard", [])

    for idx, inn in enumerate(scorecard):
        inning_name = inn.get("inning", f"Innings {idx+1}")
        batting = inn.get("batting", [])
        bowling = inn.get("bowling", [])

        items.append({"type": "header", "text": f"🏏 {inning_name}", "timestamp": ""})

        for b in batting:
            runs = int(b.get("r", 0))
            balls = int(b.get("b", 0))
            fours = int(b.get("4s", 0))
            sixes = int(b.get("6s", 0))
            dismissal = b.get("dismissal", "not out")
            name = b.get("batsman", "?")

            if runs >= 100:
                items.append({"type": "milestone", "text": f"💯 CENTURY! {name} smashes {runs} off {balls} balls! ({fours}x4, {sixes}x6)", "timestamp": ""})
            elif runs >= 50:
                items.append({"type": "milestone", "text": f"⭐ FIFTY! {name} scores {runs}({balls}) with {fours} fours and {sixes} sixes!", "timestamp": ""})

            if sixes >= 3:
                items.append({"type": "six", "text": f"🔥 {name} hammers {sixes} SIXES in his innings of {runs}!", "timestamp": ""})

            if dismissal and dismissal != "not out":
                items.append({"type": "wicket", "text": f"❌ OUT! {name} {runs}({balls}) — {dismissal}", "timestamp": ""})

        for bw in bowling:
            wickets = int(bw.get("w", 0))
            if wickets >= 3:
                items.append({"type": "bowling", "text": f"🎯 {bw.get('bowler','?')} picks up {wickets}/{bw.get('r','?')} in {bw.get('o','?')} overs! Eco: {bw.get('eco','?')}", "timestamp": ""})

    return items
