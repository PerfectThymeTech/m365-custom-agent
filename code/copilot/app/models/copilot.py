from typing import Any, Dict, Optional

from pydantic import BaseModel, field_serializer
from pydantic.alias_generators import to_camel
from app.models.core import AuthorizationTypes


class CopilotSettings(BaseModel):
    auth_type: AuthorizationTypes
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    authority_endpoint: Optional[str] = None
    federated_client_id: Optional[str] = None
    federated_token_file: Optional[str] = None
    scopes: list[str]

    @field_serializer("auth_type", "client_id", "client_secret", "authority_endpoint", "federated_client_id", "federated_token_file", "scopes", mode="plain")
    def serialize(self, value: str) -> str:
        return to_camel(value).capitalize()


class CopilotServiceConnection(BaseModel):
    settings: CopilotSettings

    @field_serializer("settings", mode="plain")
    def serialize(self, value: str) -> str:
        return to_camel(value).capitalize()


class CopilotConnections(BaseModel):
    service_connection: CopilotServiceConnection

    @field_serializer("service_connection", mode="plain")
    def serialize(self, value: str) -> str:
        return to_camel(value).capitalize()


class CopilotConfiguration(BaseModel):
    agent_application: Dict[str, Any] = {}
    connections_map: Dict[str, Any] = {}
    connections: CopilotConnections

    @field_serializer("agent_application", "connections_map", "connections", mode="plain")
    def serialize(self, value: str) -> str:
        return to_camel(value).capitalize()
