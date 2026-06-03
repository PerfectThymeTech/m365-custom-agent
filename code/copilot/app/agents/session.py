from typing import Any, List, cast

from agents.items import TResponseInputItem
from agents.memory.openai_responses_compaction_session import (
    _normalize_compaction_output_items,
)
from agents.memory.session import SessionABC
from app.logs import setup_logging
from openai import AsyncOpenAI

logger = setup_logging(__name__)


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
                logger.info(
                    f"Removing developer item at index {i} from session.",
                    extra={
                        "code": "AGENT_SESSION_REMOVE_DEVELOPER_ITEM",
                        "session_id": self.session_id,
                        "index": i,
                    },
                )
                del self.conversation_history[i]

    async def compact_history(self, model_name: str) -> None:
        """Run compaction for this session.

        :param model_name: The name of the model to use for compaction.
        :type model_name: str
        :return: None
        :rtype: None
        """
        # Implement your compaction logic here, e.g., call the OpenAI compaction endpoint
        logger.info(
            f"Running compaction for session: {self.session_id}",
            extra={
                "code": "AGENT_SESSION_COMPACT_HISTORY",
                "session_id": self.session_id,
            },
        )
        compacted_response = await self.openai_client.responses.compact(
            model=model_name,
            input=self.conversation_history,
        )
        logger.info(
            "Compaction complete. Updating conversation history with compacted output.",
            extra={
                "code": "AGENT_SESSION_COMPACT_HISTORY_COMPLETED",
                "session_id": self.session_id,
            },
        )

        # Convert output to list[TResponseInputItem]
        output_items = _normalize_compaction_output_items(compacted_response.output)

        # Update the session's conversation history with the compacted output items
        logger.debug(
            f"Compacted output items: {len(output_items)} items after compaction.",
            extra={
                "code": "AGENT_SESSION_COMPACT_HISTORY_CONVERTED_OUTPUT",
                "session_id": self.session_id,
            },
        )
        self.conversation_history = output_items
