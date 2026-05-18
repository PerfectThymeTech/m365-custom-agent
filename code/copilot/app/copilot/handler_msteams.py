from typing import Tuple

from agents.exceptions import ModelBehaviorError
from app.agents.document import DocumentAgent
from app.copilot.common import (
    filter_attachments_by_type,
    get_html_from_attachment,
    stream_string_in_chunks,
)
from app.copilot.handler_abstract import AbstractHandler
from app.core.settings import settings
from app.files.extraction import FileExtractionClient
from app.logs import setup_logging
from app.models.agents import UserStateStoreItem
from app.models.attachments import (
    AttachmentContent,
    DocumentExtractionResult,
    DocumentExtractionResults,
)
from microsoft_agents.hosting.core import TurnContext
from openai import APIError, BadRequestError

logger = setup_logging(__name__)


SUPPORTED_CONTENT_TYPES = [
    "application/vnd.microsoft.teams.file.download.info",
]
SUPPORTED_FILE_TYPES = [
    "pdf",
    "xlsx",
    "pptx",
    "docx",
    "png",
    "jpg",
    "jpeg",
    "bmp",
    "tiff",
]
IGNORED_CONTENT_TYPES = [
    "text/html",
]


class MSTeamsHandler(AbstractHandler):
    """
    Handler for Microsoft Teams specific message and event handling.
    """

    @staticmethod
    async def handle_commands(
        context: TurnContext, user_state_store_item: UserStateStoreItem
    ):
        """
        Handle default commands.

        :param context: The TurnContext object for the current turn.
        :type context: TurnContext
        :param user_state_store_item: The UserStateStoreItem object for the current user.
        :type user_state_store_item: UserStateStoreItem
        :return: The updated UserStateStoreItem object after processing the agent response and a string specifying whether a pre-defined command was processed.
        :rtype: Tuple[UserStateStoreItem, bool]
        """
        # Define variable
        command = False

        # Define user prompt
        user_prompt = (
            context.activity.text
            if context.activity.text
            else get_html_from_attachment(attachments=context.activity.attachments)
        )

        match user_prompt.lower().strip():
            case "/restart":
                logger.info(
                    "Restart ('/restart') command detected.",
                    extra={
                        "code": "HANDLE_COMMAND_DETECTED_RESTART",
                        "channel_id": "msteams",
                    },
                )

                # Send informative update to user
                context.streaming_response.queue_informative_update(
                    "Restarting conversation and resetting context... "
                )

                # Reset user state
                user_state_store_item.file_uploaded = False
                user_state_store_item.document_extraction_results = (
                    DocumentExtractionResults()
                )
                user_state_store_item.last_response_id = None
                user_state_store_item.last_response_token_count = 0
                user_state_store_item.suggested_actions = {}

                # Update user that we have
                await stream_string_in_chunks(
                    context=context,
                    text=f"Your conversation has been reset. You can start fresh now! Please upload a new file when you are ready to reason over the file. Supported file types are: {', '.join(SUPPORTED_FILE_TYPES)}. ",
                )

                # Update command variable
                command = True
            case _:
                logger.info(
                    "No command detected.",
                    extra={
                        "code": "HANDLE_COMMAND_DETECTED_NONE",
                        "channel_id": "msteams",
                    },
                )

                # Update command variable
                command = False

        return (user_state_store_item, command)

    @staticmethod
    async def handle_attachments(
        context: TurnContext, user_state_store_item: UserStateStoreItem
    ) -> UserStateStoreItem:
        """
        Handle attachments in the TurnContext for document processing.

        :param context: The TurnContext object for the current turn.
        :type context: TurnContext
        :param user_state_store_item: The UserStateStoreItem object for the current user.
        :type user_state_store_item: UserStateStoreItem
        :return: The updated UserStateStoreItem object after processing attachments.
        :rtype: UserStateStoreItem
        """
        # Update user that we detected a file attachment
        await stream_string_in_chunks(
            context=context,
            text="I see that you just uploaded new files. Let me process them... ",
        )

        # Filter attachments for document processing
        logger.info(
            "Filtering attachments for document processing.",
            extra={
                "code": "HANDLE_ATTACHMENTS_FILTERING_STARTED",
                "channel_id": "msteams",
            },
        )
        supported_attachments, unsupported_attachments = filter_attachments_by_type(
            attachments=context.activity.attachments or [],
            supported_content_types=SUPPORTED_CONTENT_TYPES,
            supported_file_types=SUPPORTED_FILE_TYPES,
            ignored_content_types=IGNORED_CONTENT_TYPES,
            validate_file_types=True,
        )

        # Handle supported documents
        if len(supported_attachments) > 0:
            logger.info(
                f"Supported attachments detected. Count: {len(supported_attachments)}",
                extra={
                    "code": "HANDLE_ATTACHMENTS_SUPPORTED_DETECTED",
                    "channel_id": "msteams",
                    "num_supported_attachments": len(supported_attachments),
                },
            )

            # Initialize variables
            document_extraction_results = (
                user_state_store_item.document_extraction_results
            )
            processed_attachment_names = [
                document.title for document in document_extraction_results.documents
            ]

            # Create file extraction client
            file_extraction_client = FileExtractionClient(
                api_key=settings.AZURE_DOCUMENT_INTELLIGENCE_API_KEY,
                endpoint=settings.AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT,
                managed_identity_client_id=settings.MANAGED_IDENTITY_CLIENT_ID,
            )

            # Process each supported attachment
            for attachment in supported_attachments:
                logger.info(
                    f"Processing attachment: {attachment.name}",
                    extra={
                        "code": "HANDLE_ATTACHMENTS_PROCESSING_STARTED",
                        "channel_id": "msteams",
                        "attachment_name": attachment.name,
                    },
                )

                # Update user about processing of each file
                await stream_string_in_chunks(
                    context=context,
                    text=f"\n\nProcessing file `{attachment.name}` ... ",
                )
                await stream_string_in_chunks(
                    context=context, text="\n(  0%) Loading file ... "
                )

                # Loading file content
                attachment_content = AttachmentContent.model_validate(
                    attachment.content
                )

                # Extract text from file using FileExtractionClient
                await stream_string_in_chunks(
                    context=context, text="\n(  5%) Extracting text from file ... "
                )
                extracted_data = await file_extraction_client.extract_data(
                    file_url=attachment_content.download_url
                )
                logger.debug(
                    f"Extracted Data from file {attachment.name}: {extracted_data}",
                    extra={
                        "code": "HANDLE_ATTACHMENTS_EXTRACTION_COMPLETED",
                        "channel_id": "msteams",
                        "attachment_name": attachment.name,
                    },
                )

                # TODO: Check for harmful content in extracted data which could impact the agent response.

                # Clean extracted data
                await stream_string_in_chunks(
                    context=context, text="\n( 80%) Cleaning extracted data ... "
                )
                cleaned_data, _ = await file_extraction_client.clean_extracted_data(
                    data=extracted_data,
                    keep_paragraphs=False,
                    keep_tables=False,
                    summarize_tables=False,
                    api_key=settings.AZURE_OPENAI_API_KEY,
                    endpoint=settings.AZURE_OPENAI_ENDPOINT,
                    model_name=settings.AZURE_OPENAI_MODEL_SLM_NAME,
                    instructions=settings.INSTRUCTIONS_TABLE_SUMMARY_AGENT,
                    reasoning_effort="minimal",
                )
                logger.debug(
                    f"Cleaned Data from file {attachment.name}: {cleaned_data}",
                    extra={
                        "code": "HANDLE_ATTACHMENTS_CLEANING_COMPLETED",
                        "channel_id": "msteams",
                        "attachment_name": attachment.name,
                    },
                )

                # Update user about completion of file processing
                logger.info(
                    f"Attachment '{attachment.name}' processed successfully.",
                    extra={
                        "code": "HANDLE_ATTACHMENTS_PROCESSING_COMPLETED",
                        "channel_id": "msteams",
                        "attachment_name": attachment.name,
                    },
                )
                await stream_string_in_chunks(
                    context=context, text="\n(100%) File processing completed.\n"
                )

                # Append the data to the extracted data list
                document_extraction_results.documents.append(
                    DocumentExtractionResult(
                        title=attachment.name,
                        data=cleaned_data,
                    )
                )
                processed_attachment_names.append(f"`{attachment.name}`")

            # Add info about files in context
            logger.info(
                f"Updating user about added files to context. Files in context: {processed_attachment_names}",
                extra={
                    "code": "HANDLE_ATTACHMENTS_CONTEXT_UPDATE",
                    "channel_id": "msteams",
                    "attachment_names": processed_attachment_names,
                },
            )
            await stream_string_in_chunks(
                context=context,
                text=f"\n\nNote: The following files are added to the context: {processed_attachment_names}. If you want to reset the context, then please send the following command to the agent: `/restart`. This will remove all files from the context and allow you to start with a fresh context. \n\n",
            )

            # Update store item
            user_state_store_item.file_uploaded = True
            user_state_store_item.document_extraction_results = (
                document_extraction_results
            )
        else:
            logger.info(
                "No supported attachments detected.",
                extra={
                    "code": "HANDLE_ATTACHMENTS_NO_SUPPORTED_DETECTED",
                    "channel_id": "msteams",
                },
            )

        if len(unsupported_attachments) > 0:
            logger.info(
                f"Unsupported attachments detected. Count: {len(unsupported_attachments)}",
                extra={
                    "code": "HANDLE_ATTACHMENTS_UNSUPPORTED_DETECTED",
                    "channel_id": "msteams",
                    "num_unsupported_attachments": len(unsupported_attachments),
                },
            )

            # Update user about unprocessed and unsupported attachments
            unsupported_attachments_names = [
                attachment.name for attachment in unsupported_attachments
            ]
            if len(unsupported_attachments) > 0:
                await stream_string_in_chunks(
                    context=context,
                    text=f"\nNOTE: The following files you uploaded are not supported and have been ignored: {unsupported_attachments_names}. Please upload only supported file types: {', '.join(SUPPORTED_FILE_TYPES)}. \n\n",
                )

        return user_state_store_item

    @staticmethod
    async def handle_agent_response(
        context: TurnContext, user_state_store_item: UserStateStoreItem
    ) -> Tuple[UserStateStoreItem, str]:
        """
        Handle agent response based on user prompt and previous state.

        :param context: The TurnContext object for the current turn.
        :type context: TurnContext
        :param user_state_store_item: The UserStateStoreItem object for the current user.
        :type user_state_store_item: UserStateStoreItem
        :return: The updated UserStateStoreItem object after processing the agent response and the string response.
        :rtype: Tuple[UserStateStoreItem, string]
        """
        # Send informative update to user
        context.streaming_response.queue_informative_update(
            "Let me think about that... "
        )

        # Define instructions before creating the agent
        file_names = [document.title for document in user_state_store_item.document_extraction_results.documents]
        instructions = (
            settings.INSTRUCTIONS_DOCUMENT_AGENT
            + "\n\n"
            + "### Files in context",
            + "\n"
            + "["
            + ", ".join(file_names)
            + "]"
        )

        # Create agent
        agent = DocumentAgent(
            api_key=settings.AZURE_OPENAI_API_KEY,
            endpoint=settings.AZURE_OPENAI_ENDPOINT,
            model_name=settings.AZURE_OPENAI_MODEL_NAME,
            agent_name="Document Reasoning Agent",
            instructions=instructions,
            output_guardrails=[],
            managed_identity_client_id=settings.MANAGED_IDENTITY_CLIENT_ID,
            reasoning_effort="none",
        )

        # Define user prompt
        user_prompt = (
            context.activity.text
            if context.activity.text
            else get_html_from_attachment(attachments=context.activity.attachments)
        )

        # Check for suggested action prompt scenarios
        logger.info(
            "Checking for suggested action prompt scenarios.",
            extra={
                "code": "HANDLE_AGENT_RESPONSE_SUGGESTED_ACTION_PROMPT_CHECK_STARTED",
                "channel_id": "msteams",
            },
        )
        if user_prompt in user_state_store_item.suggested_actions.keys():
            user_prompt = user_state_store_item.suggested_actions[user_prompt]
            logger.info(
                f"User prompt matches a suggested action. Using corresponding prompt.",
                extra={
                    "code": "HANDLE_AGENT_RESPONSE_SUGGESTED_ACTION_PROMPT_MATCHED",
                    "channel_id": "msteams",
                    "suggested_action_prompt": user_prompt,
                },
            )
        else:
            logger.info(
                f"User prompt does not match any suggested action. Proceeding with default instructions.",
                extra={
                    "code": "HANDLE_AGENT_RESPONSE_SUGGESTED_ACTION_PROMPT_NOT_MATCHED",
                    "channel_id": "msteams",
                    "user_prompt": user_prompt,
                },
            )

        # Check for pre-defined prompt scenario
        logger.info(
            "Checking for pre-defined prompt scenario.",
            extra={
                "code": "HANDLE_AGENT_RESPONSE_CHECK_PREDEFINED_PROMPT_SCENARIOS",
                "channel_id": "msteams",
            },
        )
        for scenario in settings.SCENARIO_DEFINITIONS.scenarios:
            if user_prompt == scenario.title:
                user_prompt = scenario.prompt
                logger.info(
                    f"User prompt matches predefined scenario '{scenario.title}'. Using corresponding prompt.",
                    extra={
                        "code": "HANDLE_AGENT_RESPONSE_PREDEFINED_PROMPT_SCENARIO_MATCHED",
                        "channel_id": "msteams",
                        "scenario_title": scenario.title,
                    },
                )
                break

        # Stream agent response
        logger.info(
            f"Streaming agent response with previous response id '{user_state_store_item.last_response_id}'.",
            extra={
                "code": "HANDLE_AGENT_RESPONSE_STREAMING_STARTED",
                "channel_id": "msteams",
            },
        )
        last_response_id, response, total_token_count = await agent.stream_response(
            input=user_prompt,
            context=context,
            document_extraction_results=user_state_store_item.document_extraction_results,
            last_response_id=user_state_store_item.last_response_id,
        )

        # Update store item
        user_state_store_item.last_response_id = last_response_id
        user_state_store_item.last_response_token_count = total_token_count

        return user_state_store_item, response

    @staticmethod
    async def handle_default_response(context: TurnContext) -> None:
        """
        Handle default response when no file has been uploaded.

        :param context: The TurnContext object for the current turn.
        :type context: TurnContext
        :return: None
        :rtype: None
        """
        await stream_string_in_chunks(
            context, "Please upload a PDF file before we proceed. \n\n"
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
                "channel_id": "msteams",
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
                        "channel_id": "msteams",
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
                        "channel_id": "msteams",
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
                        "channel_id": "msteams",
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
                        "channel_id": "msteams",
                        "conversation_id": context.activity.conversation.id,
                        "activity_id": context.activity.id,
                    },
                )

                await stream_string_in_chunks(
                    context,
                    "I'm sorry, but something went wrong while processing your request. Please try again later. If the issue persists, `/restart` the conversation and reupload the document again.",
                )
