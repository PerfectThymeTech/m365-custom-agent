from app.logs import setup_logging
from app.models.scenarios import ScenarioDefinitions
from microsoft_agents.activity import ActionTypes, CardAction
from microsoft_agents.activity.hero_card import HeroCard
from microsoft_agents.hosting.core import MessageFactory, TurnContext
from microsoft_agents.hosting.core.card_factory import CardFactory

logger = setup_logging(__name__)


class ScenarioHandler:
    def __init__(self, scenario_definitions: ScenarioDefinitions) -> None:
        self.activity = MessageFactory.carousel(
            attachments=[],
            text="Here are a few pre-defined scenarios you can select from. Click on a scenario to get started.",
        )
        self._add_scenarios(scenario_definitions=scenario_definitions)

    def _add_scenarios(self, scenario_definitions: ScenarioDefinitions) -> None:
        """
        Add scenario cards to the activity attachments.

        :return: None
        """
        for scenario_definition in scenario_definitions.scenarios:
            # Create card for each scenario
            card = HeroCard(
                title=scenario_definition.title,
                text=scenario_definition.description,
                tap=CardAction(
                    type=ActionTypes.message_back,
                    title=scenario_definition.title,
                    text=scenario_definition.title,
                    display_text=scenario_definition.title,
                ),
                buttons=[
                    CardAction(
                        type=ActionTypes.message_back,
                        title="Select",
                        text=scenario_definition.title,
                        display_text=scenario_definition.title,
                    )
                ],
            )

            # Add the card to the carousel attachments
            self.activity.attachments.append(CardFactory.hero_card(card=card))

    async def send(self, context: TurnContext) -> None:
        """
        Send the scenario selection activity to the user.

        :param context: The TurnContext object for the current turn.
        :type context: TurnContext
        :return: None
        """
        if len(self.activity.attachments) > 0:
            logger.info("Send carousel activity with pre-defined scenarios.")
            await context.send_activity(self.activity)
        else:
            logger.info(
                "Carousel activity has no pre-defined scenarios. Skipping send."
            )
