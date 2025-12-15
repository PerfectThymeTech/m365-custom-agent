from app.core.settings import settings
from app.models.copilot import (
    CopilotAgentApplication,
    CopilotConfiguration,
    CopilotConnections,
    CopilotHandler,
    CopilotHandlerSettings,
    CopilotServiceConnection,
    CopilotServiceConnectionSettings,
    CopilotUserAuthorization,
)
from app.models.core import AuthorizationTypes


def get_copilot_configuration() -> CopilotConfiguration:
    """
    Get the copilot configuration.

    RETURNS (CopilotConfiguration): The copilot configuration.
    """
    copilot_service_connection_settings = None

    match settings.AUTH_TYPE:
        case AuthorizationTypes.CLIENT_SECRET:
            copilot_service_connection_settings = CopilotServiceConnectionSettings(
                auth_type=settings.AUTH_TYPE,
                tenant_id=settings.TENANT_ID,
                client_id=settings.CLIENT_ID,
                client_secret=settings.CLIENT_SECRET,
                authority_endpoint=f"https://login.microsoftonline.com/{settings.TENANT_ID}",
                scopes=settings.SCOPES,
            )

        case AuthorizationTypes.USER_MANAGED_IDENTITY:
            copilot_service_connection_settings = CopilotServiceConnectionSettings(
                auth_type=settings.AUTH_TYPE,
                tenant_id=settings.TENANT_ID,
                client_id=settings.CLIENT_ID,
                scopes=settings.SCOPES,
            )

        case AuthorizationTypes.SYSTEM_MANAGED_IDENTITY:
            copilot_service_connection_settings = CopilotServiceConnectionSettings(
                auth_type=settings.AUTH_TYPE,
                scopes=settings.SCOPES,
            )

        case AuthorizationTypes.FEDERATED_CREDENTIALS:
            copilot_service_connection_settings = CopilotServiceConnectionSettings(
                auth_type=settings.AUTH_TYPE,
                tenant_id=settings.TENANT_ID,
                client_id=settings.CLIENT_ID,
                authority_endpoint=f"https://login.microsoftonline.com/{settings.TENANT_ID}",
                federated_client_id=settings.FEDERATED_CLIENT_ID,
                scopes=settings.SCOPES,
            )

        case AuthorizationTypes.WORKLOAD_IDENTITY:
            copilot_service_connection_settings = CopilotServiceConnectionSettings(
                auth_type=settings.AUTH_TYPE,
                tenant_id=settings.TENANT_ID,
                client_id=settings.CLIENT_ID,
                authority_endpoint=f"https://login.microsoftonline.com/{settings.TENANT_ID}",
                federated_token_file=settings.FEDERATED_TOKEN_FILE,
                scopes=settings.SCOPES,
            )

        case _:
            raise ValueError(f"Unsupported AUTH_TYPE: {settings.AUTH_TYPE}")

    # Configure user authorization
    copilot_user_authorization = CopilotUserAuthorization(
        handlers={
            "GRAPH": CopilotHandler(
                settings=CopilotHandlerSettings(
                    azure_bot_oauth_connection_name=settings.USER_AUTHORIZATION_GRAPH_OAUTH_CONNECTION_NAME
                )
            )
        }
    )

    return CopilotConfiguration(
        agent_application=CopilotAgentApplication(
            user_authorization=copilot_user_authorization,
        ),
        connections_map={},
        connections=CopilotConnections(
            service_connection=CopilotServiceConnection(
                settings=copilot_service_connection_settings
            )
        ),
    )
