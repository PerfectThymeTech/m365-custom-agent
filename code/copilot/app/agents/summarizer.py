from app.logs import setup_logging
from app.agents.root import RootAgent
from app.models.agents import TableSummaryAgentResponse
from pydantic import ValidationError

logger = setup_logging(__name__)


class SummarizerAgent(RootAgent):
    
    async def get_table_summary(
        self, table: str, last_response_id: str | None = None
    ) -> TableSummaryAgentResponse | None:
        # Generate table summary
        logger.info("Generating table summary from agent.")
        model_input = f"# Table Definition\n{table}"
        result = await self._get_response(
            input=model_input, last_response_id=last_response_id
        )

        # Parse the response into SuggestedActionsAgentResponse
        try:
            logger.info("Parsing table summary response from agent.")
            table_summary_response = (
                TableSummaryAgentResponse.model_validate_json(result)
            )
        except ValidationError as e:
            logger.error(f"Error parsing table summary response: {e}")
            table_summary_response = None

        return table_summary_response
