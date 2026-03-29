"""
Health Check Router
System health monitoring endpoints.
"""
from datetime import datetime, timezone

from fastapi import APIRouter

from core.database import db_manager
from config.settings import settings
from models.schemas import HealthStatus

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthStatus)
async def health_check() -> HealthStatus:
    """
    Comprehensive health check endpoint.
    Returns status of all services.
    """
    services = await db_manager.health_check()
    
    # Determine overall status
    all_healthy = all(
        s.get("status") in ["healthy", "disabled"] 
        for s in services.values()
    )
    
    return HealthStatus(
        status="healthy" if all_healthy else "degraded",
        version=settings.APP_VERSION,
        timestamp=datetime.now(timezone.utc),
        services=services
    )


@router.get("/ready")
async def readiness_check():
    """
    Kubernetes readiness probe.
    Returns 200 if app is ready to serve traffic.
    """
    services = await db_manager.health_check()
    
    # MongoDB must be healthy for readiness
    if services.get("mongodb", {}).get("status") != "healthy":
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Database not ready")
    
    return {"status": "ready"}


@router.get("/live")
async def liveness_check():
    """
    Kubernetes liveness probe.
    Returns 200 if app is alive.
    """
    return {"status": "alive"}
