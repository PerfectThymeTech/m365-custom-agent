from app.copilot.copilot import auth_handlers, copilot_apps
from app.logs import setup_logging
from microsoft_agents.activity import ActivityTypes, ConversationUpdateTypes
from microsoft_agents.hosting.core import TurnContext, TurnState

logger = setup_logging(__name__)


@copilot_apps["default"].error
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
        extra={"code": "ON_ERROR", "channel_id": "default"},
    )


@copilot_apps["default"].activity(
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
            "channel_id": "default",
            "user_id": context.activity.from_property.id,
            "channel_id": context.activity.channel_id,
            "activity_id": context.activity.id,
            "conversation_id": context.activity.conversation.id,
        },
    )
    await context.send_activity(
        "Welcome to the Large File Processing agent! "
        "You are using an unsupported channel/client."
        "Please use a supported channel/client to interact with this agent. "
    )
    return True


@copilot_apps["default"].activity(
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
    logger.info(
        f"Received message activity from user: '{context.activity.from_property.id}', channel id: '{context.activity.channel_id}', activity id: '{context.activity.id}', conversation id: '{context.activity.conversation.id}'.",
        extra={
            "code": "ON_MESSAGE",
            "channel_id": "default",
            "user_id": context.activity.from_property.id,
            "channel_id": context.activity.channel_id,
            "activity_id": context.activity.id,
            "conversation_id": context.activity.conversation.id,
        },
    )
    await context.send_activity(
        "Welcome to the Large File Processing agent! "
        "You are using an unsupported channel/client."
        "Please use a supported channel/client to interact with this agent. "
    )
    return True


@copilot_apps["default"].on_sign_in_success
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
            "channel_id": "default",
            "user_id": context.activity.from_property.id,
            "handler_id": handler_id,
            "caller_id": context.activity.caller_id,
        },
    )


@copilot_apps["default"].on_turn
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
            "channel_id": "default",
            "activity_type": context.activity.type,
            "user_id": context.activity.from_property.id,
            "channel_id": context.activity.channel_id,
            "activity_id": context.activity.id,
            "conversation_id": context.activity.conversation.id,
        },
    )
