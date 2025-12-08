from typing import Any

# from app.health.validate_request import verify_health_auth_header
from app.logs import setup_logging
from app.models.heartbeat import HeartbeatResult
from fastapi import APIRouter, Depends

logger = setup_logging(__name__)

router = APIRouter()


@router.get(
    "/heartbeat",
    response_model=HeartbeatResult,
    name="heartbeat",
    # dependencies=[Depends(verify_health_auth_header)],
)
async def get_heartbeat() -> Any:
    """
    Heartbeat endpoint to verify service is alive.
    """
    logger.info("Received Heartbeat Request")
    return HeartbeatResult(isAlive=True)
