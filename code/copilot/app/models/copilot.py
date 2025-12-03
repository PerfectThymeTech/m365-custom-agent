from typing import Any, Dict, Optional

from pydantic import BaseModel, field_serializer, ConfigDict
from pydantic.alias_generators import to_camel
from app.models.core import AuthorizationTypes


def copilot_settings_alias_generator(string: str) -> str:
    return to_camel(string).upper()


def copilot_service_connection_alias_generator(string: str) -> str:
    return to_camel(string).upper()


def copilot_connection_alias_generator(string: str) -> str:
    return string.upper()


def copilot_configuration_alias_generator(string: str) -> str:
    return to_camel(string).upper()


class CopilotSettings(BaseModel):
    auth_type: AuthorizationTypes
    tenant_id: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    authority_endpoint: Optional[str] = None
    federated_client_id: Optional[str] = None
    federated_token_file: Optional[str] = None
    scopes: list[str]

    model_config = ConfigDict(
        alias_generator=copilot_settings_alias_generator,
        populate_by_name=True,
    )


class CopilotServiceConnection(BaseModel):
    settings: CopilotSettings

    model_config = ConfigDict(
        alias_generator=copilot_service_connection_alias_generator,
        from_attributes=True,
        populate_by_name=True,
    )


class CopilotConnections(BaseModel):
    service_connection: CopilotServiceConnection

    model_config = ConfigDict(
        alias_generator=copilot_connection_alias_generator,
        from_attributes=True,
        populate_by_name=True,
    )


class CopilotConfiguration(BaseModel):
    agent_application: Dict[str, Any] = {}
    connections_map: Dict[str, Any] = {}
    connections: CopilotConnections

    model_config = ConfigDict(
        alias_generator=copilot_configuration_alias_generator,
        from_attributes=True,
        populate_by_name=True,
    )
