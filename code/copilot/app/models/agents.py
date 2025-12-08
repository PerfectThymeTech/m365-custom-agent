from microsoft_agents.hosting.core import StoreItem
from pydantic import BaseModel, Field


class UserStateStoreItem(StoreItem):
    def __init__(
        self,
        file_uploaded: bool = False,
        instructions: str = None,
        last_response_id: str = None,
        suggested_actions: dict[str, str] = {},
    ):
        self.file_uploaded = file_uploaded
        self.instructions = instructions
        self.last_response_id = last_response_id
        self.suggested_actions = suggested_actions

    def store_item_to_json(self) -> dict:
        return {
            "file_uploaded": self.file_uploaded,
            "instructions": self.instructions,
            "last_response_id": self.last_response_id,
            "suggested_actions": self.suggested_actions,
        }

    @staticmethod
    def from_json_to_store_item(json_data: dict) -> "UserStateStoreItem":
        return UserStateStoreItem(
            file_uploaded=json_data.get("file_uploaded", False),
            instructions=json_data.get("instructions", None),
            last_response_id=json_data.get("last_response_id", None),
            suggested_actions=json_data.get("suggested_actions", {}),
        )


class SuggestedAction(BaseModel):
    title: str = Field(..., alias="title")
    value: str = Field(..., alias="value")
    prompt: str = Field(..., alias="prompt")


class SuggestedActionsAgentResponse(BaseModel):
    suggested_actions: list[SuggestedAction] = Field(..., alias="suggested_actions")
