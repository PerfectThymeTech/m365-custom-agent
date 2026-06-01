from typing import Any, List, cast

from agents.items import TResponseInputItem
from agents.memory.session import SessionABC
from app.logs import setup_logging, setup_tracing
from openai import AsyncOpenAI

logger = setup_logging(__name__)
tracer = setup_tracing(__name__)


class AgentSession(SessionABC):
    """Custom session implementation following the Session protocol."""

    def __init__(self, session_id: str, openai_client: AsyncOpenAI):
        self.session_id = session_id
        self.conversation_history: List[TResponseInputItem] = []
        self.openai_client = openai_client

    async def get_items(self, limit: int | None = None) -> List[TResponseInputItem]:
        """Retrieve conversation history for this session.

        :param limit: Optional limit on the number of items to retrieve. If None, retrieves all items.
        :type limit: int or None
        :return: List of conversation history items, up to the specified limit if provided.
        :rtype: List[TResponseInputItem]
        """
        if limit is None:
            return self.conversation_history
        return self.conversation_history[:limit]

    async def add_items(self, items: List[TResponseInputItem]) -> None:
        """Store new items for this session.

        :param items: List of items to add to the conversation history.
        :type items: List[TResponseInputItem]
        :return: None
        :rtype: None
        """
        self.conversation_history.extend(items)

    async def pop_item(self) -> TResponseInputItem | None:
        """Remove and return the most recent item from this session.

        :return: The most recent item, or None if the session is empty.
        :rtype: TResponseInputItem or None
        """
        if self.conversation_history:
            return self.conversation_history.pop()
        return None

    async def clear_session(self) -> None:
        """Clear all items for this session.

        :return: None
        :rtype: None
        """
        self.conversation_history.clear()

    async def remove_developer_items(self) -> None:
        """Remove all items with the role 'developer' from this session.

        :return: None
        :rtype: None
        """
        for i in range(len(self.conversation_history) - 1, -1, -1):
            if self.conversation_history[i].get("role", None) == "developer":
                print(f"Removing developer item: {self.conversation_history[i]}")
                del self.conversation_history[i]

    async def compact_history(self, model_name: str) -> None:
        """Run compaction for this session.

        :param model_name: The name of the model to use for compaction.
        :type model_name: str
        :return: None
        :rtype: None
        """
        # Implement your compaction logic here, e.g., call the OpenAI compaction endpoint
        print("Running compaction for session:", self.session_id)
        # Example: Call the OpenAI compaction endpoint with the current conversation history
        compacted_response = await self.openai_client.responses.compact(
            model=model_name,
            input=self.conversation_history,
        )
        print(
            "Compaction complete. Updating conversation history with compacted output."
        )

        # Update conversation history with compacted response
        output_items: list[TResponseInputItem] = []
        for item in compacted_response.output:
            if isinstance(item, dict):
                output_item = item
            else:
                # Suppress Pydantic literal warnings: responses.compact can return
                # user-style input_text content inside ResponseOutputMessage.
                output_item = item.model_dump(exclude_unset=True, warnings=False)

            if (
                isinstance(output_item, dict)
                and output_item.get("type") == "message"
                and output_item.get("role") == "user"
            ):
                output_items.append(
                    self._normalize_compaction_user_message(output_item)
                )
                continue

            output_items.append(cast(TResponseInputItem, output_item))

        # Update the session's conversation history with the compacted output items
        print(f"Compacted output items: {len(output_items)} items after compaction.")
        self.conversation_history = output_items

    def _normalize_compaction_user_message(
        self, item: dict[str, Any]
    ) -> TResponseInputItem:
        """Normalize compacted user message content before it is reused as input.

        :param item: The compacted user message item to normalize.
        :type item: dict[str, Any]
        :return: The normalized user message item, ready for reuse as input.
        :rtype: TResponseInputItem
        """
        content = item.get("content")
        if not isinstance(content, list):
            return cast(TResponseInputItem, item)

        normalized_content: list[Any] = []
        for content_item in content:
            if not isinstance(content_item, dict):
                normalized_content.append(content_item)
                continue

            content_type = content_item.get("type")
            if content_type == "input_image":
                normalized_content.append(
                    self._normalize_compaction_input_image(content_item)
                )
            elif content_type == "input_file":
                normalized_content.append(
                    self._normalize_compaction_input_file(content_item)
                )
            else:
                normalized_content.append(content_item)

        normalized_item = dict(item)
        normalized_item["content"] = normalized_content
        return cast(TResponseInputItem, normalized_item)

    def _normalize_compaction_input_image(
        self, content_item: dict[str, Any]
    ) -> dict[str, Any]:
        """Return a valid replay shape for a compacted Responses image input.

        :param content_item: The compacted input_image content item to normalize.
        :type content_item: dict[str, Any]
        :return: The normalized input_image content item, ready for reuse as input.
        :rtype: dict[str, Any]
        """
        normalized = {"type": "input_image"}

        image_url = content_item.get("image_url")
        file_id = content_item.get("file_id")
        if isinstance(image_url, str) and image_url:
            normalized["image_url"] = image_url
        elif isinstance(file_id, str) and file_id:
            normalized["file_id"] = file_id
        else:
            raise ValueError(
                "Compaction input_image item missing image_url or file_id."
            )

        detail = content_item.get("detail")
        if isinstance(detail, str) and detail:
            normalized["detail"] = detail

        return normalized

    def _normalize_compaction_input_file(
        self, content_item: dict[str, Any]
    ) -> dict[str, Any]:
        """Return a valid replay shape for a compacted Responses file input.

        :param content_item: The compacted input_file content item to normalize.
        :type content_item: dict[str, Any]
        :return: The normalized input_file content item, ready for reuse as input.
        :rtype: dict[str, Any]
        """
        normalized = {"type": "input_file"}

        file_data = content_item.get("file_data")
        file_url = content_item.get("file_url")
        file_id = content_item.get("file_id")
        if isinstance(file_data, str) and file_data:
            normalized["file_data"] = file_data
        elif isinstance(file_url, str) and file_url:
            normalized["file_url"] = file_url
        elif isinstance(file_id, str) and file_id:
            normalized["file_id"] = file_id
        else:
            raise ValueError(
                "Compaction input_file item missing file_data, file_url, or file_id."
            )

        filename = content_item.get("filename")
        if isinstance(filename, str) and filename:
            normalized["filename"] = filename

        detail = content_item.get("detail")
        if isinstance(detail, str) and detail:
            normalized["detail"] = detail

        return normalized

    def _normalize_compaction_user_message(
        self, item: dict[str, Any]
    ) -> TResponseInputItem:
        """Normalize compacted user message content before it is reused as input.

        :param item: The compacted user message content item to normalize.
        :type item: dict[str, Any]
        :return: The normalized user message content item, ready for reuse as input.
        :rtype: TResponseInputItem
        """
        content = item.get("content")
        if not isinstance(content, list):
            return cast(TResponseInputItem, item)

        normalized_content: list[Any] = []
        for content_item in content:
            if not isinstance(content_item, dict):
                normalized_content.append(content_item)
                continue

            content_type = content_item.get("type")
            if content_type == "input_image":
                normalized_content.append(
                    self._normalize_compaction_input_image(content_item)
                )
            elif content_type == "input_file":
                normalized_content.append(
                    self._normalize_compaction_input_file(content_item)
                )
            else:
                normalized_content.append(content_item)

        normalized_item = dict(item)
        normalized_item["content"] = normalized_content
        return cast(TResponseInputItem, normalized_item)
