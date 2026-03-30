"""
Bharat 11 — Push Notification Endpoints
Subscribe/unsubscribe to web push + get VAPID public key
"""
import os
import logging
from dotenv import load_dotenv
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase
from core.dependencies import get_db, CurrentUser
from models.schemas import utc_now, generate_id

load_dotenv()

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class PushSubscriptionData(BaseModel):
    subscription: dict  # {endpoint, keys: {p256dh, auth}}


@router.get("/vapid-public-key")
async def get_vapid_public_key():
    """Return the VAPID public key for push subscription."""
    key = os.environ.get("VAPID_PUBLIC_KEY", "")
    return {"public_key": key}


@router.post("/subscribe")
async def subscribe_push(
    data: PushSubscriptionData,
    current_user: CurrentUser,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Subscribe to push notifications."""
    endpoint = data.subscription.get("endpoint", "")
    if not endpoint:
        return {"error": "Invalid subscription - no endpoint"}

    # Upsert: if this endpoint exists, update; else insert
    existing = await db.push_subscriptions.find_one(
        {"user_id": current_user.id, "subscription.endpoint": endpoint}
    )

    if existing:
        return {"status": "already_subscribed"}

    await db.push_subscriptions.insert_one({
        "id": generate_id(),
        "user_id": current_user.id,
        "subscription": data.subscription,
        "created_at": utc_now().isoformat(),
    })

    logger.info(f"Push subscription added for user {current_user.id}")
    return {"status": "subscribed"}


@router.post("/unsubscribe")
async def unsubscribe_push(
    data: PushSubscriptionData,
    current_user: CurrentUser,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Unsubscribe from push notifications."""
    endpoint = data.subscription.get("endpoint", "")
    result = await db.push_subscriptions.delete_many({
        "user_id": current_user.id,
        "subscription.endpoint": endpoint,
    })
    return {"status": "unsubscribed", "deleted": result.deleted_count}
