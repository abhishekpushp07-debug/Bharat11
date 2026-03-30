"""
Bharat 11 — Web Push Notification Manager
Sends push notifications to subscribed users.
"""
import os
import json
import logging
from dotenv import load_dotenv
from pywebpush import webpush, WebPushException

load_dotenv()

logger = logging.getLogger(__name__)

VAPID_PUBLIC_KEY = os.environ.get("VAPID_PUBLIC_KEY", "")
VAPID_PRIVATE_KEY = os.environ.get("VAPID_PRIVATE_KEY", "")
VAPID_CLAIMS_EMAIL = os.environ.get("VAPID_CLAIMS_EMAIL", "mailto:admin@bharat11.com")


async def send_push(db, user_id: str, title: str, body: str, data: dict = None, url: str = "/"):
    """Send push notification to a specific user's subscriptions."""
    subs = await db.push_subscriptions.find(
        {"user_id": user_id},
        {"_id": 0, "subscription": 1}
    ).to_list(length=10)

    if not subs:
        return 0

    payload = json.dumps({
        "title": title,
        "body": body,
        "data": {"url": url, **(data or {})},
    })

    sent = 0
    for sub in subs:
        try:
            webpush(
                subscription_info=sub["subscription"],
                data=payload,
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims={"sub": VAPID_CLAIMS_EMAIL},
            )
            sent += 1
        except WebPushException as e:
            if e.response and e.response.status_code in (404, 410):
                # Subscription expired/invalid - remove it
                await db.push_subscriptions.delete_one({"subscription": sub["subscription"]})
                logger.debug(f"Removed expired push subscription for user {user_id}")
            else:
                logger.warning(f"Push failed for user {user_id}: {e}")
        except Exception as e:
            logger.warning(f"Push error: {e}")

    return sent


async def send_push_to_many(db, user_ids: list, title: str, body: str, data: dict = None, url: str = "/"):
    """Send push to multiple users."""
    total = 0
    for uid in user_ids:
        total += await send_push(db, uid, title, body, data, url)
    return total


async def send_push_broadcast(db, title: str, body: str, data: dict = None, url: str = "/"):
    """Send push to ALL subscribed users."""
    all_subs = await db.push_subscriptions.find(
        {},
        {"_id": 0, "user_id": 1, "subscription": 1}
    ).to_list(length=10000)

    payload = json.dumps({
        "title": title,
        "body": body,
        "data": {"url": url, **(data or {})},
    })

    sent = 0
    expired = []
    for sub in all_subs:
        try:
            webpush(
                subscription_info=sub["subscription"],
                data=payload,
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims={"sub": VAPID_CLAIMS_EMAIL},
            )
            sent += 1
        except WebPushException as e:
            if e.response and e.response.status_code in (404, 410):
                expired.append(sub["subscription"])
        except Exception:
            pass

    # Cleanup expired
    if expired:
        await db.push_subscriptions.delete_many({"subscription": {"$in": expired}})

    return sent


# ==================== NOTIFICATION TRIGGERS ====================

async def notify_match_starting(db, match_name: str, match_id: str):
    """Push: Match starting in 1 hour."""
    await send_push_broadcast(
        db,
        title="Match Starting Soon!",
        body=f"{match_name} starts in 1 hour! Predictions lagao abhi!",
        data={"match_id": match_id, "type": "match_starting"},
        url="/"
    )


async def notify_results_ready(db, contest_id: str, match_name: str, user_ids: list):
    """Push: Results are ready for a contest."""
    await send_push_to_many(
        db,
        user_ids,
        title="Results Ready!",
        body=f"{match_name} ke results aa gaye! Check your rank now.",
        data={"contest_id": contest_id, "type": "results_ready"},
        url="/"
    )


async def notify_contest_live(db, contest_name: str, match_id: str):
    """Push: New contest is live."""
    await send_push_broadcast(
        db,
        title="New Contest Live!",
        body=f"{contest_name} is now open! Join and predict.",
        data={"match_id": match_id, "type": "contest_live"},
        url="/"
    )
