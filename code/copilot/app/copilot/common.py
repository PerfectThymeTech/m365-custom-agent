import asyncio

from app.agents.actions import SuggestedActionsAgent
from app.core.settings import settings
from app.logs import setup_logging
from app.models.agents import SuggestedActionsAgentResponse
from app.models.attachments import AttachmentContent
from microsoft_agents.activity.attachment import Attachment
from microsoft_agents.hosting.core import TurnContext
from pydantic import ValidationError

logger = setup_logging(__name__)


def configure_context(context: TurnContext):
    """
    Configure the TurnContext for streaming responses, etc..

    :param context: The TurnContext object for the current turn.
    :type context: TurnContext
    """
    # Configure streaming response
    context.streaming_response.set_feedback_loop(True)
    context.streaming_response.set_generated_by_ai_label(True)


def filter_attachments_by_type(
    attachments: list[Attachment],
    supported_content_types: list[str],
    supported_file_types: list[str],
    ignored_content_types: list[str],
) -> tuple[list[Attachment], list[Attachment]]:
    """
    Filter attachments by content type.

    :param attachments: Specified the list of Attachment objects to be filtered.
    :type attachments: list[Attachment]
    :param supported_content_types: Specifies the content types that are supported.
    :type supported_content_types: list[str]
    :param supported_file_types: Specifies the file types that are supported.
    :type supported_file_types: list[str]
    :return: A tuple containing two lists: supported attachments and unsupported attachments from the provided attachment list.
    :rtype: tuple[list[Attachment], list[Attachment]]
    """
    # Initialize lists for supported and unsupported attachments
    supported_attachments = []
    unsupported_attachments = []

    # Iterate through attachments and filter based on content type
    for attachment in attachments:
        if attachment.content_type in supported_content_types:
            # Supported content type
            logger.info(
                f"Supported attachment '{attachment.name}' with content type '{attachment.content_type}' detected."
            )

            try:
                # Validate attachment content
                attachment_content = AttachmentContent.model_validate(
                    attachment.content
                )

                # Check if file type is supported
                if attachment_content.file_type.lower() in supported_file_types:
                    logger.info(
                        f"Supported attachment '{attachment.name}' with file type '{attachment_content.file_type}' detected."
                    )
                    supported_attachments.append(attachment)
                else:
                    logger.info(
                        f"Unsupported attachment '{attachment.name}' with file type '{attachment_content.file_type}' detected."
                    )
                    unsupported_attachments.append(attachment)

            except ValidationError as e:
                # Unsupported file type
                logger.error(
                    f"Failed to parse attachment content for {attachment.name}: {e}"
                )
                unsupported_attachments.append(attachment)
        elif attachment.content_type in ignored_content_types:
            # Ignored content type
            logger.info(
                f"Ignored attachment '{attachment.name}' with content type '{attachment.content_type}' detected."
            )
        else:
            # Unsupported content type
            logger.info(
                f"Unsupported attachment '{attachment.name}' with content type '{attachment.content_type}' detected."
            )
            unsupported_attachments.append(attachment)

    return supported_attachments, unsupported_attachments


def get_html_from_attachment(attachments: list[Attachment]) -> str:
    # Initialize variable to hold HTML message
    html_message = ""

    # Iterate through attachments and filter based on content type
    for attachment in attachments:
        match attachment.content_type:
            case "text/html":
                if isinstance(attachment.content, str):
                    html_message = attachment.content
                    logger.info(
                        f"HTML attachment '{attachment.name}' processed successfully."
                    )
                    return html_message
                else:
                    logger.error(
                        f"HTML attachment content for {attachment.name} is not a string."
                    )

    return html_message


async def get_suggested_actions_from_agent(
    user_input: str, agent_response: str, agent_instructions: str
) -> SuggestedActionsAgentResponse:
    """
    Get suggested actions from the SuggestedActionsAgent.

    :param input: The input string to be sent to the agent.
    :type input: str
    :param last_response_id: The last response ID from the agent, if any.
    :type last_response_id: str | None
    :return: A list of suggested actions.
    :rtype: list[str]
    """
    logger.info("Generating suggested actions using SuggestedActionsAgent.")

    # Define input for agent
    input = f"""
    # User Input:
    ```
    {user_input}
    ```

    # Agent Response:
    ```
    {agent_response}
    ```

    # Agent Instructions:
    ```
    {agent_instructions}
    ```
    """

    # Initialize SuggestedActionsAgent
    suggested_actions_agent = SuggestedActionsAgent(
        api_key=settings.AZURE_OPENAI_API_KEY,
        endpoint=settings.AZURE_OPENAI_ENDPOINT,
        model_name=settings.AZURE_OPENAI_MODEL_SLM_NAME,
        instructions=settings.INSTRUCTIONS_SUGGESTED_ACTIONS,
        reasoning_effort="minimal",
    )

    # Get suggested actions from agent
    suggested_actions_response = await suggested_actions_agent.get_suggested_actions(
        input=input,
        last_response_id=None,
    )

    logger.info(
        f"Number of suggested actions generated: {len(suggested_actions_response.suggested_actions)}"
    )

    return suggested_actions_response


async def stream_string_in_chunks(context: TurnContext, text: str):
    """
    Stream a string in chunks to the client.

    :param context: The TurnContext object for the current turn.
    :type context: TurnContext
    :param text: The text which must be streamed.
    :type text: str
    """
    # Split string into words
    words = text.split(sep=" ")
    for word in words:
        # Stream each word as a chunk
        context.streaming_response.queue_text_chunk(f"{word} ")

        # Simulate delay for streaming effect
        await asyncio.sleep(0.1)
