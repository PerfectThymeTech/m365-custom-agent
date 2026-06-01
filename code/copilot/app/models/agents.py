from app.files.compression import DataCompressionClient
from app.models.attachments import DocumentExtractionResults
from microsoft_agents.hosting.core import StoreItem
from pydantic import BaseModel, Field
from agents.items import TResponseInputItem


class UserConversationStoreItem(StoreItem):
    def __init__(
        self,
        conversation_history: list[TResponseInputItem] = [],
    ):
        self.conversation_history = conversation_history
    
    def store_item_to_json(self) -> dict:
        return {
            "conversation_history": [item.model_dump() for item in self.conversation_history],
        }

    @staticmethod
    def from_json_to_store_item(json_data: dict) -> "UserConversationStoreItem":
        return UserConversationStoreItem(
            conversation_history=[TResponseInputItem.model_validate(item) for item in json_data.get("conversation_history", [])],
        )


class UserStateStoreItem(StoreItem):
    def __init__(
        self,
        file_uploaded: bool = False,
        document_extraction_results: DocumentExtractionResults = DocumentExtractionResults(),
        last_response_id: str = None,
        suggested_actions: dict[str, str] = {},
    ):
        self.file_uploaded = file_uploaded
        self.document_extraction_results = document_extraction_results
        self.last_response_id = last_response_id
        self.suggested_actions = suggested_actions

    def store_item_to_json(self) -> dict:
        # Compress document extraction results
        document_extraction_results_json = (
            self.document_extraction_results.model_dump_json(indent=None)
        )
        document_extraction_results_compressed = DataCompressionClient.compress_string(
            document_extraction_results_json
        )

        return {
            "file_uploaded": self.file_uploaded,
            "document_extraction_results": document_extraction_results_compressed,
            "last_response_id": self.last_response_id,
            "suggested_actions": self.suggested_actions,
        }

    @staticmethod
    def from_json_to_store_item(json_data: dict) -> "UserStateStoreItem":
        # Decompress document extraction results
        if "document_extraction_results" in json_data:
            decompressed_data = DataCompressionClient.decompress_string(
                json_data.get("document_extraction_results")
            )
        else:
            decompressed_data = "{}"

        return UserStateStoreItem(
            file_uploaded=json_data.get("file_uploaded", False),
            document_extraction_results=DocumentExtractionResults.model_validate_json(
                decompressed_data
            ),
            last_response_id=json_data.get("last_response_id", None),
            suggested_actions=json_data.get("suggested_actions", {}),
        )


class SuggestedAction(BaseModel):
    title: str = Field(..., alias="title")
    value: str = Field(..., alias="value")
    prompt: str = Field(..., alias="prompt")


class SuggestedActionsAgentResponse(BaseModel):
    suggested_actions: list[SuggestedAction] = Field(..., alias="suggested_actions")


class TableSummaryAgentResponse(BaseModel):
    table_key: str = Field(..., alias="table_key")
    summary: str = Field(..., alias="summary")
