from app.copilot.action import SuggestedActionHandler
from app.copilot.common import configure_context, get_suggested_actions_from_agent
from app.copilot.copilot import auth_handlers, copilot_apps
from app.copilot.handler_webchat import WebchatHandler
from app.copilot.scenarios import ScenarioHandler
from app.core.settings import settings
from app.logs import setup_logging
from app.models.agents import UserStateStoreItem
from microsoft_agents.activity import ActivityTypes, ConversationUpdateTypes
from microsoft_agents.hosting.core import TurnContext, TurnState

logger = setup_logging(__name__)


@copilot_apps["webchat"].error
async def on_error(context: TurnContext, error: Exception) -> None:
    """
    Handle errors that occur during the bot's operation.

    :param context: The TurnContext object for the current turn.
    :type context: TurnContext
    :param error: The Exception object representing the error that occurred.
    :type error: Exception
    :return: None
    """
    logger.error(
        f"An error occurred: {error}",
        exc_info=True,
        extra={"code": "ON_ERROR", "channel_id": "webchat"},
    )
    await WebchatHandler.handle_error_response(context=context, error=error)

    # End response stream if active
    try:
        await context.streaming_response.end_stream()
    except RuntimeError as e:
        logger.info(
            f"Response stream has already ended: '{e}'",
            extra={
                "code": "ON_ERROR_RESPONSE_STREAM_ALREADY_ENDED",
                "channel_id": "webchat",
            },
        )


@copilot_apps["webchat"].activity(
    ConversationUpdateTypes.MEMBERS_ADDED, auth_handlers=auth_handlers["default"]
)
async def on_members_added(context: TurnContext, state: TurnState) -> None:
    """
    Handle members added activities.

    :param context: The TurnContext object for the current turn.
    :type context: TurnContext
    :param state: The TurnState object for maintaining state across turns.
    :type state: TurnState
    :return: None
    """
    logger.info(
        f"Received members added activity from user: '{context.activity.from_property.id}', channel id: '{context.activity.channel_id}', activity id: '{context.activity.id}', conversation id: '{context.activity.conversation.id}'.",
        extra={
            "code": "ON_MEMBERS_ADDED",
            "channel_id": "webchat",
            "user_id": context.activity.from_property.id,
            "channel_id": context.activity.channel_id,
            "activity_id": context.activity.id,
            "conversation_id": context.activity.conversation.id,
        },
    )
    await context.send_activity(
        "Welcome to the Large File Processing agent! "
        "This agent helps you to reason over large PDF files."
        "Please upload a single PDF file to get started. "
        "Once the file is processed, you can ask questions about its content. "
        "Feel free to ask me anything related to the document you upload! "
    )
    return True


@copilot_apps["webchat"].activity(
    ActivityTypes.message, auth_handlers=auth_handlers["default"]
)
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
        f"Processing message activity with text: '{context.activity.text}', channel id: '{context.activity.channel_id}', activity: '{context.activity.id}', conversation id: '{context.activity.conversation.id}'.",
        extra={
            "code": "ON_MESSAGE",
            "channel_id": "webchat",
            "user_id": context.activity.from_property.id,
            "channel_id": context.activity.channel_id,
            "activity_id": context.activity.id,
            "conversation_id": context.activity.conversation.id,
        },
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

    # Check for pre-defined command
    user_state_store_item, command = await WebchatHandler.handle_commands(
        context=context, user_state_store_item=user_state_store_item
    )

    # Only listen for attachments if more than zero attachments is present
    if not command and len(context.activity.attachments or []) > 0:
        # Handle attachments
        user_state_store_item = await WebchatHandler.handle_attachments(
            context=context, user_state_store_item=user_state_store_item
        )

        # Send default scenario as carousel
        await ScenarioHandler(scenario_definitions=settings.SCENARIO_DEFINITIONS).send(
            context=context
        )

    # Use agent to process user prompt
    if not command:
        # Handle agent response
        user_state_store_item, response = await WebchatHandler.handle_agent_response(
            context=context, user_state_store_item=user_state_store_item
        )

        # Get suggested actions from agent if files have been uploaded
        if (
            user_state_store_item.file_uploaded
            and len(user_state_store_item.document_extraction_results.documents) > 0
        ):
            suggested_actions_response = await get_suggested_actions_from_agent(
                user_input=context.activity.text,
                agent_response=response,
                agent_instructions=settings.INSTRUCTIONS_DOCUMENT_AGENT,
            )
            # Add suggested actions for next steps to suggested action handler
            for suggested_action in suggested_actions_response.suggested_actions:
                logger.info(
                    f"Adding suggested action: '{suggested_action.title}' with value: '{suggested_action.value}'",
                    extra={
                        "code": "ON_MESSAGE_SUGGESTED_ACTION_FROM_AGENT",
                        "channel_id": "webchat",
                        "title": suggested_action.title,
                        "value": suggested_action.value,
                    },
                )
                suggested_action_handler.add_suggested_action(
                    title=suggested_action.title,
                    prompt=suggested_action.prompt,
                )

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
        logger.info(
            f"Response stream has already ended: '{e}'",
            exc_info=True,
            extra={
                "code": "ON_MESSAGE_RESPONSE_STREAM_ALREADY_ENDED",
                "channel_id": "webchat",
            },
        )


@copilot_apps["webchat"].on_sign_in_success
async def on_sign_in_success(
    context: TurnContext, state: TurnState, handler_id: str = None
) -> None:
    """
    Handle sign-in success events.

    :param context: The TurnContext object for the current turn.
    :type context: TurnContext
    :param state: The TurnState object for maintaining state across turns.
    :type state: TurnState
    :param handler_id: The handler ID for the sign-in event.
    :type handler_id: str | None
    :return: None
    """
    logger.info(
        f"Sign-in was successful for user: '{context.activity.from_property.id}', handler ID: '{handler_id}', caller id: '{context.activity.caller_id}'.",
        extra={
            "code": "ON_SIGN_IN_SUCCESS",
            "channel_id": "webchat",
            "user_id": context.activity.from_property.id,
            "handler_id": handler_id,
            "caller_id": context.activity.caller_id,
        },
    )


@copilot_apps["webchat"].on_turn
async def on_turn(context: TurnContext, state: TurnState) -> None:
    """
    Handle all turn activities.

    :param context: The TurnContext object for the current turn.
    :type context: TurnContext
    :param state: The TurnState object for maintaining state across turns.
    :type state: TurnState
    :return: None
    """
    logger.info(
        f"Received activity of type: '{context.activity.type}' from user: '{context.activity.from_property.id}', channel id: '{context.activity.channel_id}', activity id: '{context.activity.id}', conversation id: '{context.activity.conversation.id}'.",
        extra={
            "code": "ON_TURN",
            "channel_id": "webchat",
            "user_id": context.activity.from_property.id,
            "channel_id": context.activity.channel_id,
            "activity_id": context.activity.id,
            "conversation_id": context.activity.conversation.id,
        },
    )
