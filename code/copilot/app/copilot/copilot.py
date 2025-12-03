import os

from app.core.settings import settings
from microsoft_agents.hosting.fastapi import CloudAdapter
from microsoft_agents.hosting.core import (
    AgentApplication,
    TurnState,
    MemoryStorage,
)
from microsoft_agents.authentication.msal import MsalConnectionManager
from app.copilot.configuration import get_copilot_configuration


def get_copilot_app() -> AgentApplication[TurnState]:
    """
    Create and return the AgentApplication instance.

    RETURNS (AgentApplication): The AgentApplication instance.
    """
    config = get_copilot_configuration().model_dump(by_alias=True, exclude_none=True)
    agent_app = AgentApplication[TurnState](
        adapter=CloudAdapter(
            connection_manager=MsalConnectionManager(**config),
        ),
        storage=MemoryStorage(),
    )
    return agent_app


def get_copilot_apps() -> dict[str, AgentApplication[TurnState]]:
    """
    Get a dictionary of copilot apps for different channels.

    RETURNS (dict): A dictionary mapping channel names to AgentApplication instances.
    """
    teams_copilot_app = get_copilot_app()

    return {
        "msteams": teams_copilot_app,
        "msteams:COPILOT": teams_copilot_app,
    }


copilot_apps = get_copilot_apps()
