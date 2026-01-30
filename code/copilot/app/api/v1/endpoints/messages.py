from typing import Any

from app.copilot.activities_msteams import on_message  # noqa: F401
from app.copilot.copilot import copilot_apps
from app.logs import setup_logging
from fastapi import APIRouter, Request, BackgroundTasks
from microsoft_agents.hosting.fastapi import start_agent_process
# from app.core.collections import BACKGROUND_TASKS_DICT

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
    logger.info(f"Message payload: {payload}")

    # Add background tasks to global dict
    # BACKGROUND_TASKS_DICT[id(request)] = background_tasks

    # Start agent process
    result = await start_agent_process(
        request=request,
        agent_application=copilot_apps["msteams"],
        adapter=copilot_apps["msteams"].adapter,
    )

    # Remove background tasks from global dict
    # BACKGROUND_TASKS_DICT.pop(id(request), None)

    return result
