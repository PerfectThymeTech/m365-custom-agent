from typing import Tuple

from app.agents.document import DocumentAgent
from app.copilot.common import (
    filter_attachments_by_type,
    get_html_from_attachment,
    stream_string_in_chunks,
)
from app.copilot.handler_abstract import AbstractHandler
from app.copilot.scenarios import DocumentScenarioInstructions, DocumentScenarios
from app.core.settings import settings
from app.files.extraction import FileExtractionClient
from app.logs import setup_logging
from app.models.agents import UserStateStoreItem
from app.models.attachments import AttachmentContent
from microsoft_agents.hosting.core import TurnContext
from openai import APIError, BadRequestError
from pydantic import ValidationError

logger = setup_logging(__name__)


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
                logger.info("Restart ('/restart') command detected.")

                # Send informative update to user
                context.streaming_response.queue_informative_update(
                    "Restarting conversation and resetting context... "
                )

                # Reset user state
                user_state_store_item.file_uploaded = False
                user_state_store_item.instructions = None
                user_state_store_item.last_response_id = None
                user_state_store_item.suggested_actions = {}

                # Update user that we have
                await stream_string_in_chunks(
                    context=context,
                    text="Your conversation has been reset. You can start fresh now! Please upload a new file when you are ready to reason over the file.",
                )

                # Update command variable
                command = True
            case _:
                logger.info("No command detected.")

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
        logger.info("Filtering attachments for document processing.")
        supported_attachments, unsupported_attachments = filter_attachments_by_type(
            attachments=context.activity.attachments or [],
            supported_content_types=[
                "application/vnd.microsoft.teams.file.download.info",
            ],
            supported_file_types=[
                "pdf",
            ],
            ignored_content_types=[
                "text/html",
            ],
        )

        # Handle supported documents
        if len(supported_attachments) > 0:
            logger.info(
                f"Supported attachments detected. Count: {len(supported_attachments)}"
            )

            # Create file extraction client
            file_extraction_client = FileExtractionClient(
                api_key=settings.AZURE_DOCUMENT_INTELLIGENCE_API_KEY,
                endpoint=settings.AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT,
            )

            # Process each supported attachment
            for attachment in supported_attachments:
                logger.info(f"Processing attachment: {attachment.name}")

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
                    f"Extracted Data from file {attachment.name}: {extracted_data}"
                )

                # TODO: Check for harmful content in extracted data which could impact the agent response.

                # Clean extracted data
                await stream_string_in_chunks(
                    context=context, text="\n( 80%) Cleaning extracted data ... "
                )
                cleaned_data = file_extraction_client.clean_extracted_data(
                    data=extracted_data
                )
                logger.debug(
                    f"Cleaned Data from file {attachment.name}: {cleaned_data}"
                )

                # Update user about completion of file processing
                logger.info(f"Attachment '{attachment.name}' processed successfully.")
                await stream_string_in_chunks(
                    context=context, text="\n(100%) File processing completed.\n"
                )

                # Only process the first supported attachment for now
                break

            # Update user about not processed documents
            supported_attachments_names = [
                attachment.name for attachment in supported_attachments
            ]
            if len(supported_attachments) > 1:
                await stream_string_in_chunks(
                    context=context,
                    text=f"\n\nNote: I could see that you uploaded the following supported files: {supported_attachments_names}. However, I only support one document at a time. Only the first item has been added to the context (`{supported_attachments[0].name}`). You can upload a new file at any time to replace it. ",
                )

            # Encode instructions with extracted data
            instructions = settings.INSTRUCTIONS_DOCUMENT_AGENT + f"\n{cleaned_data}"
            compressed_instructions = FileExtractionClient.compress_string(instructions)

            # Update store item
            user_state_store_item.file_uploaded = True
            user_state_store_item.instructions = compressed_instructions
        else:
            logger.info("No supported attachments detected.")
            await stream_string_in_chunks(
                context=context,
                text="I could not find any supported document in the attachments you uploaded. Please upload PDF documents only. ",
            )

        if len(unsupported_attachments) > 0:
            logger.info(
                f"Unsupported attachments detected. Count: {len(unsupported_attachments)}"
            )

            # Update user about unprocessed and unsupported attachments
            unsupported_attachments_names = [
                attachment.name for attachment in unsupported_attachments
            ]
            if len(unsupported_attachments) > 0:
                await stream_string_in_chunks(
                    context=context,
                    text=f"\nNOTE: The following files you uploaded are not supported and have been ignored: {unsupported_attachments_names}. Please upload PDF documents only. ",
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

        # Decompress instructions before creating the agent
        decompressed_instructions = FileExtractionClient.decompress_string(
            user_state_store_item.instructions
        )

        # Create agent
        agent = DocumentAgent(
            api_key=settings.AZURE_OPENAI_API_KEY,
            endpoint=settings.AZURE_OPENAI_ENDPOINT,
            model_name=settings.AZURE_OPENAI_MODEL_NAME,
            instructions=decompressed_instructions,
            reasoning_effort="none",
        )

        # Define user prompt
        user_prompt = (
            context.activity.text
            if context.activity.text
            else get_html_from_attachment(attachments=context.activity.attachments)
        )

        # Check for suggested action prompt scenarios
        logger.info("Checking for suggested action prompt scenarios.")
        if user_prompt in user_state_store_item.suggested_actions.keys():
            user_prompt = user_state_store_item.suggested_actions[user_prompt]
            logger.info(
                f"User prompt matches a suggested action. Using corresponding prompt."
            )
        else:
            logger.info(
                f"User prompt does not match any suggested action. Proceeding with default instructions."
            )

        # try:
        #     document_scenario = DocumentScenarios(user_prompt)
        #     user_prompt = DocumentScenarioInstructions.INSTRUCTIONS[document_scenario]
        #     logger.info(f"User prompt matches predefined scenario '{document_scenario.value}'. Using corresponding instructions.")
        # except ValueError as e:
        #     logger.info(f"User prompt does not match any predefined scenario. Proceeding with default instructions.")
        # except ValidationError as e:
        #     logger.info(f"User prompt does not match any predefined scenario. Proceeding with default instructions.")

        # Stream agent response
        logger.info(
            f"Streaming agent response with previous response id '{user_state_store_item.last_response_id}'."
        )
        last_response_id, response = await agent.stream_response(
            input=user_prompt,
            last_response_id=user_state_store_item.last_response_id,
            context=context,
        )

        # Update store item
        user_state_store_item.last_response_id = last_response_id

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
        )

        match error:
            case APIError() as api_error:
                # Capture OpenAI APIError specifically
                logger.error(f"OpenAI APIError occurred: {api_error}", exc_info=True)

                await stream_string_in_chunks(
                    context,
                    "We are very sorry, but our agent currently experiences issues when processing your request. Please try again later.",
                )

            case BadRequestError() as bad_request_error:
                # Capture OpenAI BadRequestError specifically
                logger.error(
                    f"OpenAI BadRequestError occurred: {bad_request_error}",
                    exc_info=True,
                )

                if bad_request_error.code == "string_above_max_length":
                    await stream_string_in_chunks(
                        context,
                        "The document is too large for me to process. Please upload a smaller document to proceed.",
                    )
                else:
                    await stream_string_in_chunks(
                        context,
                        "We are very sorry, but our agent currently experiences issues when processing your request. Please try again later.",
                    )
            case _:
                # Capture any other unexpected errors
                logger.error(f"An unexpected error occurred: {error}", exc_info=True)

                await stream_string_in_chunks(
                    context,
                    "I'm sorry, but something went wrong while processing your request. Please try again later.",
                )
