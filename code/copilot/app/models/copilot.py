from typing import Any, Dict, Optional

from app.models.core import AuthorizationTypes
from pydantic import BaseModel, ConfigDict, field_serializer
from pydantic.alias_generators import to_camel


def copilot_service_connection_settings_alias_generator(string: str) -> str:
    return to_camel(string).upper()


def copilot_service_connection_alias_generator(string: str) -> str:
    return to_camel(string).upper()


def copilot_connection_alias_generator(string: str) -> str:
    return string.upper()


def copilot_configuration_alias_generator(string: str) -> str:
    return to_camel(string).upper()


class CopilotServiceConnectionSettings(BaseModel):
    auth_type: AuthorizationTypes
    tenant_id: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    authority_endpoint: Optional[str] = None
    federated_client_id: Optional[str] = None
    federated_token_file: Optional[str] = None
    scopes: list[str]

    model_config = ConfigDict(
        alias_generator=copilot_service_connection_settings_alias_generator,
        populate_by_name=True,
    )


class CopilotServiceConnection(BaseModel):
    settings: CopilotServiceConnectionSettings

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
