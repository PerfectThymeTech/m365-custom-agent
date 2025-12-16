from app.logs import setup_logging
from app.agents.root import RootAgent
from app.models.agents import SuggestedActionsAgentResponse
from pydantic import ValidationError

logger = setup_logging(__name__)


class SuggestedActionsAgent(RootAgent):

    async def get_suggested_actions(
        self, input: str, last_response_id: str | None = None
    ) -> SuggestedActionsAgentResponse:
        """
        Get suggested actions from the agent based on the input.
        
        param input: The user input to process.
        type input: str
        param last_response_id: The ID of the last response for context continuity.
        type last_response_id: str | None
        return: SuggestedActionsAgentResponse containing the suggested actions.
        rtype: SuggestedActionsAgentResponse
        """
        # Generate agent response
        logger.info("Generating suggested actions from agent.")
        result = await self._get_response(
            input=input, last_response_id=last_response_id
        )

        # Parse the response into SuggestedActionsAgentResponse
        try:
            logger.info("Parsing suggested actions response from agent.")
            suggested_actions_response = (
                SuggestedActionsAgentResponse.model_validate_json(result)
            )
        except ValidationError as e:
            logger.error(f"Error parsing suggested actions response: {e}")
            suggested_actions_response = SuggestedActionsAgentResponse(
                suggested_actions=[]
            )

        return suggested_actions_response
