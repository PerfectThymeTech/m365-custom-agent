from microsoft_agents.activity import ActionTypes, Activity, ActivityTypes, CardAction
from microsoft_agents.activity.suggested_actions import SuggestedActions
from microsoft_agents.hosting.core import TurnContext
from app.logs import setup_logging


logger = setup_logging(__name__)


class SuggestedActionHandler:
    def __init__(self, to: list[str]):
        self.activity = Activity(
            type=ActivityTypes.suggestion,
            text="Choose a suggested action.",
            suggested_actions=SuggestedActions(
                to=to,
                actions=[],
            ),
        )

    def add_suggested_action(self, title: str, value: str, type: str = ActionTypes.im_back) -> None:
        """
        Add a suggested action to the activity.

        :param title: The title of the suggested action.
        :type title: str
        :param value: The value of the suggested action.
        :type value: str
        :param type: The type of the suggested action.
        :type type: str
        :return: None
        """
        action = CardAction(
            type=type,
            title=title,
            value=value,
            image="https://res.public.onecdn.static.microsoft/midgard/versionless/officestartresources/chat_filled_20.svg",
            display_text=title,
            channel_data=None,
            image_alt_text="Question Icon",
        )
        self.activity.suggested_actions.actions.append(action)

    def get_activity(self) -> Activity:
        """
        Get the activity with suggested actions.

        :return: The activity with suggested actions.
        :rtype: Activity
        """
        return self.activity

    async def send(self, context: TurnContext) -> None:
        """
        Send the activity with suggested actions to the user.

        :param context: The TurnContext object for the current turn.
        :type context: TurnContext
        :return: None
        """
        if len(self.activity.suggested_actions.actions) > 0:
            logger.info("Sending suggested actions to the user.")
            await context.send_activity(self.activity)
        else:
            logger.info("No suggested actions to send to the user.")
