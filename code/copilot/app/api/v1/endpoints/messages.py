from typing import Any

from app.copilot.activities_msteams import on_message  # noqa: F401
from app.copilot.copilot import copilot_apps
from app.logs import setup_logging
from fastapi import APIRouter, Request
from microsoft_agents.hosting.fastapi import start_agent_process

logger = setup_logging(__name__)

router = APIRouter()


@router.post(
    "/message",
    response_model=Any,
    name="message",
)
async def post_message(request: Request) -> Any:
    """
    Heartbeat endpoint to verify service is alive.
    """
    logger.info(f"Received message")

    # Get payload
    payload = await request.json()
    channel = payload.get("channelId")
    logger.debug(f"Message payload: {payload}")

    # Start agent process
    result = await start_agent_process(
        request=request,
        agent_application=copilot_apps[channel],
        adapter=copilot_apps[channel].adapter,
    )

    return result
