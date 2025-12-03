from app.core.settings import settings
from app.models.copilot import (
    CopilotConfiguration,
    CopilotConnections,
    CopilotServiceConnection,
    CopilotSettings,
)
from app.models.core import AuthorizationTypes


def get_copilot_configuration() -> CopilotConfiguration:
    """
    Get the copilot configuration.

    RETURNS (CopilotConfiguration): The copilot configuration.
    """
    copilot_settings = None

    match settings.AUTH_TYPE:
        case AuthorizationTypes.CLIENT_SECRET:
            copilot_settings = CopilotSettings(
                auth_type=settings.AUTH_TYPE,
                tenant_id=settings.TENANT_ID,
                client_id=settings.CLIENT_ID,
                client_secret=settings.CLIENT_SECRET,
                authority_endpoint=f"https://login.microsoftonline.com/{settings.TENANT_ID}",
                scopes=settings.SCOPES,
            )

        case AuthorizationTypes.USER_MANAGED_IDENTITY:
            copilot_settings = CopilotSettings(
                auth_type=settings.AUTH_TYPE,
                tenant_id=settings.TENANT_ID,
                scopes=settings.SCOPES,
            )

        case AuthorizationTypes.SYSTEM_MANAGED_IDENTITY:
            copilot_settings = CopilotSettings(
                auth_type=settings.AUTH_TYPE,
                scopes=settings.SCOPES,
            )

        case AuthorizationTypes.FEDERATED_CREDENTIALS:
            copilot_settings = CopilotSettings(
                auth_type=settings.AUTH_TYPE,
                tenant_id=settings.TENANT_ID,
                client_id=settings.CLIENT_ID,
                authority_endpoint=f"https://login.microsoftonline.com/{settings.TENANT_ID}",
                federated_client_id=settings.FEDERATED_CLIENT_ID,
                scopes=settings.SCOPES,
            )

        case AuthorizationTypes.WORKLOAD_IDENTITY:
            copilot_settings = CopilotSettings(
                auth_type=settings.AUTH_TYPE,
                tenant_id=settings.TENANT_ID,
                client_id=settings.CLIENT_ID,
                authority_endpoint=f"https://login.microsoftonline.com/{settings.TENANT_ID}",
                federated_token_file=settings.FEDERATED_TOKEN_FILE,
                scopes=settings.SCOPES,
            )

        case _:
            raise ValueError(f"Unsupported AUTH_TYPE: {settings.AUTH_TYPE}")

    return CopilotConfiguration(
        agent_application={},
        connections_map={},
        connections=CopilotConnections(
            service_connection=CopilotServiceConnection(settings=copilot_settings)
        ),
    )
