import os
from typing import Any

from app.copilot.configuration import get_copilot_configuration
from app.core.settings import settings
from app.logs import OpenTelemetryTranscriptLogger, setup_logging
from azure.identity import DefaultAzureCredential
from microsoft_agents.authentication.msal import MsalConnectionManager
from microsoft_agents.hosting.core import (
    AgentApplication,
    Authorization,
    MemoryStorage,
    TurnState,
)
from microsoft_agents.hosting.core.storage import TranscriptLoggerMiddleware
from microsoft_agents.hosting.fastapi import CloudAdapter
from microsoft_agents.storage.cosmos import CosmosDBStorage, CosmosDBStorageConfig

logger = setup_logging(__name__)


def get_copilot_configuration_as_dict() -> dict[str, Any]:
    """
    Create and return the Copilot configuration as dict.

    :return: The configuration used for the copilot app.
    :rtype: dict[str, Any]
    """
    # Load configuration for msal
    logger.info("Loading Copilot configuration")
    config = get_copilot_configuration().model_dump(by_alias=True, exclude_none=True)

    return config


def get_copilot_connection_manager(config: dict[str, Any]) -> MsalConnectionManager:
    """
    Create and return the MsalConnectionManager instance.

    :param config: The configuration dictionary for the connection manager.
    :type config: dict[str, Any]
    :return: The connection manager instance.
    :rtype: MsalConnectionManager
    """
    # Configure connection manager and adapter
    logger.info("Configuring connection manager and adapter for Copilot")
    connection_manager = MsalConnectionManager(**config)

    return connection_manager


def get_copilot_app(
    config: dict[str, Any], connection_manager: MsalConnectionManager
) -> AgentApplication[TurnState]:
    """
    Create and return the AgentApplication instance.

    :param config: The configuration dictionary for the copilot app.
    :type config: dict[str, Any]
    :param connection_manager: The MsalConnectionManager instance.
    :type connection_manager: MsalConnectionManager
    :return: The AgentApplication instance.
    :rtype: AgentApplication[TurnState]
    """
    # Configure storage
    logger.info("Configuring storage for Copilot")
    if settings.AZURE_COSMOS_KEY:
        auth_key = settings.AZURE_COSMOS_KEY
        credential = None
    else:
        auth_key = ""
        credential = DefaultAzureCredential()
    storage = (
        CosmosDBStorage(
            config=CosmosDBStorageConfig(
                cosmos_db_endpoint=settings.AZURE_COSMOS_ENDPOINT,
                auth_key=auth_key,
                database_id=settings.AZURE_COSMOS_DATABASE_ID,
                container_id=settings.AZURE_COSMOS_CONTAINER_ID,
                cosmos_client_options=None,
                container_throughput=0,
                key_suffix="",
                compatibility_mode=False,
                credential=credential,
            )
        )
        if settings.AZURE_COSMOS_ENDPOINT
        else MemoryStorage()
    )

    # Configure connection manager and adapter
    logger.info("Configuring connection manager and adapter for Copilot")
    cloud_adapter = CloudAdapter(
        connection_manager=connection_manager,
    )
    # cloud_adapter.use(middleware=TranscriptLoggerMiddleware(logger=OpenTelemetryTranscriptLogger())) # Not required because of FastAPI instrumentation

    # Configure authorization
    logger.info("Creating authorization for Copilot")
    authorization = Authorization(
        storage=storage,
        connection_manager=connection_manager,
        auth_handlers=None,
        auto_signin=True,
        use_cache=True,
        **config,
    )

    # Create agent application
    logger.info("Creating AgentApplication for Copilot")
    agent_app = AgentApplication[TurnState](
        authorization=authorization,
        adapter=cloud_adapter,
        storage=storage,
        **config,
    )
    return agent_app


def get_copilot_apps(
    config: dict[str, Any], connection_manager: MsalConnectionManager
) -> dict[str, AgentApplication[TurnState]]:
    """
    Get a dictionary of copilot apps for different channels.

    :param config: The configuration dictionary for the copilot apps.
    :type config: dict[str, Any]
    :param connection_manager: The MsalConnectionManager instance.
    :type connection_manager: MsalConnectionManager
    :return: A dictionary mapping channel names to AgentApplication instances.
    :rtype: dict[str, AgentApplication[TurnState]]
    """
    logger.info("Getting Copilot apps for channels")
    teams_copilot_app = get_copilot_app(
        config=config, connection_manager=connection_manager
    )
    default_copilot_app = get_copilot_app(
        config=config, connection_manager=connection_manager
    )

    logger.info("Configured Copilot apps for channels")
    return {
        "msteams": teams_copilot_app,
        "msteams:COPILOT": teams_copilot_app,
        "default": default_copilot_app,
    }


config = get_copilot_configuration_as_dict()
connection_manager = get_copilot_connection_manager(config=config)
copilot_apps = get_copilot_apps(config=config, connection_manager=connection_manager)
