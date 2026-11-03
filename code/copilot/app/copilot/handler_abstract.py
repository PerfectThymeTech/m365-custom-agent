from abc import ABC, abstractmethod
from typing import Tuple

from agents.exceptions import ModelBehaviorError
from app.copilot.common import stream_string_in_chunks
from app.logs import setup_logging
from app.models.agents import UserStateStoreItem
from microsoft_agents.hosting.core import TurnContext
from openai import APIError, BadRequestError

logger = setup_logging(__name__)


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
    async def handle_default_response(context: TurnContext) -> UserStateStoreItem:
        """
        Handle default response when no file has been uploaded.

        :param context: The TurnContext object for the current turn.
        :type context: TurnContext
        :return: None
        :rtype: None
        """
        await stream_string_in_chunks(
            context, "Please upload a PDF file before we proceed."
        )

    @staticmethod
    async def handle_error_response(context: TurnContext, error: Exception) -> None:
        """
        Handle error response when an exception occurs.

        :param context: The TurnContext object for the current turn.
        :type context: TurnContext
        :param error: The Exception object representing the error that occurred.
        :type error: Exception
        :return: None
        :rtype: None
        """
        logger.error(
            f"Error occurred in conversation: {context.activity.conversation.id}, activity: {context.activity.id}",
            exc_info=True,
            extra={
                "code": "HANDLE_ERROR_RESPONSE",
                "conversation_id": context.activity.conversation.id,
                "activity_id": context.activity.id,
            },
        )

        match error:
            case APIError() as api_error:
                # Capture OpenAI APIError specifically
                logger.error(
                    f"OpenAI APIError occurred: {api_error}",
                    exc_info=True,
                    extra={
                        "code": "HANDLE_ERROR_OPEN_AI_API",
                        "conversation_id": context.activity.conversation.id,
                        "activity_id": context.activity.id,
                    },
                )

                if api_error.code == "string_above_max_length":
                    await stream_string_in_chunks(
                        context,
                        "The document is too large for me to process. Please restart the conversation by sending `/restart` to me.",
                    )
                else:
                    await stream_string_in_chunks(
                        context,
                        "I'm sorry, but I encountered an issue while trying to process your request. Please try again in a few moments.  If the issue persists, `/restart` the conversation and reupload the document again.",
                    )

            case BadRequestError() as bad_request_error:
                # Capture OpenAI BadRequestError specifically
                logger.error(
                    f"OpenAI BadRequestError occurred: {bad_request_error}",
                    exc_info=True,
                    extra={
                        "code": "HANDLE_ERROR_OPEN_AI_BAD_REQUEST",
                        "conversation_id": context.activity.conversation.id,
                        "activity_id": context.activity.id,
                    },
                )

                if bad_request_error.code == "string_above_max_length":
                    await stream_string_in_chunks(
                        context,
                        "The document is too large for me to process. Please restart the conversation by sending `/restart` to me.",
                    )
                else:
                    await stream_string_in_chunks(
                        context,
                        "I'm sorry, but I encountered an issue while trying to process your request. Please try again later.  If the issue persists, `/restart` the conversation and reupload the document again.",
                    )
            case ModelBehaviorError() as model_behavior_error:
                # Capture ModelBehaviorError specifically
                logger.error(
                    f"ModelBehaviorError occurred: {model_behavior_error}",
                    exc_info=True,
                    extra={
                        "code": "HANDLE_ERROR_OPEN_AI_MODEL_BEHAVIOR",
                        "conversation_id": context.activity.conversation.id,
                        "activity_id": context.activity.id,
                    },
                )
                await stream_string_in_chunks(
                    context,
                    "I'm sorry, but I encountered an issue while trying to process your request. Please resend your question. If the issue persists, `/restart` the conversation and reupload the document again.",
                )
            case _:
                # Capture any other unexpected errors
                logger.error(
                    f"An unexpected error occurred: {error}",
                    exc_info=True,
                    extra={
                        "code": "HANDLE_ERROR_UNEXPECTED",
                        "conversation_id": context.activity.conversation.id,
                        "activity_id": context.activity.id,
                    },
                )

                await stream_string_in_chunks(
                    context,
                    "I'm sorry, but something went wrong while processing your request. Please try again later. If the issue persists, `/restart` the conversation and reupload the document again.",
                )

    @staticmethod
    @abstractmethod
    async def handle_commands(
        context: TurnContext, user_state_store_item: UserStateStoreItem
    ) -> Tuple[UserStateStoreItem, bool]:
        pass
