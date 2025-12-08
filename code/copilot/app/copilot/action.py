from app.logs import setup_logging
from microsoft_agents.activity import ActionTypes, Activity, ActivityTypes, CardAction
from microsoft_agents.activity.suggested_actions import SuggestedActions
from microsoft_agents.hosting.core import TurnContext

logger = setup_logging(__name__)


class SuggestedActionHandler:
    def __init__(self, to: list[str]):
        self.activity = Activity(
            type=ActivityTypes.message,
            text="Choose a suggested action or ask any other question which you want me to help with.",
            suggested_actions=SuggestedActions(
                to=to,
                actions=[],
            ),
        )
        self.add_suggested_actions: dict[str, str] = {}

    def add_suggested_action(
        self, title: str, prompt: str, type: str = ActionTypes.im_back
    ) -> None:
        """
        Add a suggested action to the activity.

        :param title: The title of the suggested action.
        :type title: str
        :param prompt: The prompt of the suggested action.
        :type prompt: str
        :param type: The type of the suggested action.
        :type type: str
        :return: None
        """
        logger.info(
            f"Adding suggested action with title: '{title}', prompt: '{prompt}', type: '{type}'"
        )

        # Create CardAction and add to activity
        action = CardAction(
            type=type,
            title=title,
            value=title,
            image="https://res.public.onecdn.static.microsoft/midgard/versionless/officestartresources/chat_filled_20.svg",
            display_text=title,
            channel_data=None,
            image_alt_text="Question Icon",
        )
        self.activity.suggested_actions.actions.append(action)

        # Add to internal tracking dictionary
        self.add_suggested_actions[title] = prompt

    def get_suggested_actions(self) -> dict[str, str]:
        """
        Get the dictionary of suggested actions.

        :return: The dictionary of suggested actions.
        :rtype: dict[str, str]
        """
        return self.add_suggested_actions

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
            logger.info(
                f"Sending {len(self.activity.suggested_actions.actions)} suggested actions to the user."
            )
            await context.send_activity(self.activity)
        else:
            logger.info("No suggested actions to send to the user.")
