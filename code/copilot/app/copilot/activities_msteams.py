from app.copilot.action import SuggestedActionHandler
from app.copilot.common import configure_context, get_suggested_actions_from_agent
from app.copilot.copilot import copilot_apps
from app.copilot.handler_msteams import (
    handle_agent_response,
    handle_attachments,
    handle_default_response,
)
from app.copilot.scenarios import DocumentScenarios
from app.core.settings import settings
from app.logs import setup_logging
from app.models.agents import UserStateStoreItem
from microsoft_agents.activity import ActivityTypes, ConversationUpdateTypes
from microsoft_agents.hosting.core import TurnContext, TurnState

logger = setup_logging(__name__)


@copilot_apps["msteams"].activity(ConversationUpdateTypes.MEMBERS_ADDED)
async def on_members_added(context: TurnContext, state: TurnState) -> None:
    """
    Handle members added activities.

    :param context: The TurnContext object for the current turn.
    :type context: TurnContext
    :param state: The TurnState object for maintaining state across turns.
    :type state: TurnState
    :return: None
    """
    await context.send_activity(
        "Welcome to the Large File Processing agent! "
        "This agent helps you to reason over large PDF files."
        "Please upload a single PDF file to get started. "
        "Once the file is processed, you can ask questions about its content. "
        "Feel free to ask me anything related to the document you upload! "
    )
    return True


@copilot_apps["msteams"].activity(ActivityTypes.message)
async def on_message(context: TurnContext, state: TurnState) -> None:
    """
    Handle incoming message activities.

    :param context: The TurnContext object for the current turn.
    :type context: TurnContext
    :param state: The TurnState object for maintaining state across turns.
    :type state: TurnState
    :return: None
    """
    # Run some logging
    logger.info(
        f"Processing message activity with text: {context.activity.text} via channel: {context.activity.channel_data} {context.activity.id}",
    )

    # Configure context
    configure_context(context)

    # Initialize activity for suggested actions
    suggested_action_handler = SuggestedActionHandler(
        to=[context.activity.from_property.id]
    )

    # Load user state
    user_state_store_item: UserStateStoreItem = state.get_value(
        name="ConversationState.user_state_store_item",
        default_value_factory=lambda: UserStateStoreItem(),
        target_cls=UserStateStoreItem,
    )

    # Only listen for attachments if more than one attachment is present since Teams sends a text message attachment by default
    if len(context.activity.attachments or []) > 1:
        user_state_store_item = await handle_attachments(
            context=context, user_state_store_item=user_state_store_item
        )

        # Add suggested actions for next steps to suggested action handler
        suggested_action_handler.add_suggested_action(
            title="Legal Descriptions and Discrepancies",
            prompt=DocumentScenarios.LEGAL_DESCRIPTIONS_AND_DISCREPANCIES.value,
        )
        suggested_action_handler.add_suggested_action(
            title="Summarize the Document",
            prompt=DocumentScenarios.SUMMARIZE_DOCUMENT.value,
        )

    # Use agent to process user prompt if file is uploaded and instructions are set
    elif user_state_store_item.file_uploaded and user_state_store_item.instructions:
        # Handle agent response
        user_state_store_item, response = await handle_agent_response(
            context=context, user_state_store_item=user_state_store_item
        )

        # Get suggested actions from agent
        suggested_actions_response = await get_suggested_actions_from_agent(
            user_input=context.activity.text,
            agent_response=response,
            agent_instructions=settings.INSTRUCTIONS_DOCUMENT_AGENT,
        )
        # suggested_action_handler.add_suggested_action(
        #     title="Test 01",
        #     prompt="Test 01", # "This is a big test with lots of characters to see how it works in the aaaaaaaaa.",
        # )
        # suggested_action_handler.add_suggested_action(
        #     title="Test 02",
        #     prompt="Test 02", # "This is a big test with lots of characters to see how it works in the aaaaaaaaa.",
        # )
        # suggested_action_handler.add_suggested_action(
        #     title="Test 03",
        #     prompt="Test 03", # "This is a big test with lots of characters to see how it works in the aaaaaaaaa.",
        # )
        # Add suggested actions for next steps to suggested action handler
        for suggested_action in suggested_actions_response.suggested_actions:
            logger.info(
                f"Adding suggested action: '{suggested_action.title}' with value: '{suggested_action.value}'"
            )
            suggested_action_handler.add_suggested_action(
                title=suggested_action.title,
                prompt=suggested_action.prompt,
            )

    # Use default response if file has not been uploaded yet
    else:
        await handle_default_response(context=context)

    # Send suggested actions if any
    await suggested_action_handler.send(context=context)

    # Save store item back to state
    suggested_actions = suggested_action_handler.get_suggested_actions()
    user_state_store_item.suggested_actions = suggested_actions
    state.set_value(
        path="ConversationState.user_state_store_item", value=user_state_store_item
    )

    # End response stream if active
    try:
        await context.streaming_response.end_stream()
    except RuntimeError as e:
        logger.info(f"Response stream has already ended: '{e}'")
