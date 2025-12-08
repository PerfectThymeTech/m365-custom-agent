from typing import Any

from app.copilot.activities_msteams import on_message  # noqa: F401
from app.copilot.copilot import copilot_apps
from app.auth import auth_settings
from app.logs import setup_logging
from fastapi import APIRouter, Request, Security
from microsoft_agents.hosting.fastapi import start_agent_process

logger = setup_logging(__name__)

router = APIRouter()


@router.post(
    "/message",
    response_model=Any,
    name="message",
    dependencies=[Security(auth_settings)],
)
async def post_message(request: Request) -> Any:
    """
    Heartbeat endpoint to verify service is alive.
    """
    logger.info(f"Received message")

    # Get payload
    payload = await request.json()
    return await start_agent_process(
        request=request,
        agent_application=copilot_apps["msteams"],
        adapter=copilot_apps["msteams"].adapter,
    )
