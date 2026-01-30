from typing import Any

from app.copilot.activities_msteams import on_message  # noqa: F401
from app.copilot.copilot import copilot_apps
from app.core.globals import BACKGROUND_TASKS_DICT
from app.logs import setup_logging
from fastapi import APIRouter, BackgroundTasks, Request
from microsoft_agents.hosting.fastapi import start_agent_process

logger = setup_logging(__name__)

router = APIRouter()


@router.post(
    "/message",
    response_model=Any,
    name="message",
)
async def post_message(request: Request, background_tasks: BackgroundTasks) -> Any:
    """
    Heartbeat endpoint to verify service is alive.
    """
    logger.info(f"Received message")

    # Get payload
    payload = await request.json()
    logger.debug(f"Message payload: {payload}")

    # Add background tasks to global dict
    activity_id = payload.get("id", id(request))
    BACKGROUND_TASKS_DICT[activity_id] = background_tasks

    # Start agent process
    result = await start_agent_process(
        request=request,
        agent_application=copilot_apps["msteams"],
        adapter=copilot_apps["msteams"].adapter,
    )

    # Remove background tasks from global dict
    _ = BACKGROUND_TASKS_DICT.pop(activity_id, None)

    return result
