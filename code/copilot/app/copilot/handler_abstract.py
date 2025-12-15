from abc import ABC, abstractmethod
from typing import Tuple

from app.models.agents import UserStateStoreItem
from microsoft_agents.hosting.core import TurnContext


class AbstractHandler(ABC):
    """
    Abstract base class for handling different types of messages and events.
    """

    @staticmethod
    @abstractmethod
    async def handle_attachments(
        context: TurnContext, user_state_store_item: UserStateStoreItem
    ) -> UserStateStoreItem:
        pass

    @staticmethod
    @abstractmethod
    async def handle_agent_response(
        context: TurnContext, user_state_store_item: UserStateStoreItem
    ) -> Tuple[UserStateStoreItem, str]:
        pass

    @staticmethod
    @abstractmethod
    async def handle_default_response(context: TurnContext) -> UserStateStoreItem:
        pass

    @staticmethod
    @abstractmethod
    async def handle_error_response(context: TurnContext, error: Exception) -> None:
        pass

    @staticmethod
    @abstractmethod
    async def handle_commands(context: TurnContext, user_state_store_item: UserStateStoreItem) -> Tuple[UserStateStoreItem, bool]:
        pass
