from pydantic import ValidationError
from agents import Agent, Runner, OpenAIResponsesModel
from agents.model_settings import ModelSettings
from openai.types.shared.reasoning import Reasoning
from openai.types.responses import ResponseTextDeltaEvent
from openai import AsyncOpenAI
from microsoft_agents.hosting.core import TurnContext
from app.models.agents import SuggestedActionsAgentResponse
from app.logs import setup_logging


logger = setup_logging(__name__)


class SuggestedActionsAgent:
    def __init__(self, api_key: str, endpoint: str, model_name: str, instructions: str, reasoning_effort: str = "none"):
        self.agent = self._create_agent(api_key, endpoint, model_name=model_name, instructions=instructions, reasoning_effort=reasoning_effort)
        self.runner = Runner()
    
    def _create_agent(self, api_key: str, endpoint: str, model_name: str, instructions: str, reasoning_effort: str = "none") -> Agent:
        # Define the model and client
        openai_client = AsyncOpenAI(
            api_key=api_key, 
            base_url=f"{endpoint}openai/v1/",
        )
        model = OpenAIResponsesModel(
            model=model_name,
            openai_client=openai_client,
        )
        model_settings = ModelSettings(
            reasoning=Reasoning(
                effort=reasoning_effort
            ),
        )

        # Define the agent
        agent = Agent(
            name="Suggested Actions Agent",
            tools=[],
            mcp_servers=[],
            instructions=instructions,
            model=model,
            model_settings=model_settings,
        )
        return agent
    
    async def stream_response(self, input: str,  context: TurnContext, last_response_id: str | None = None) -> str:
        # Generate agent response
        result = self.runner.run_streamed(
            starting_agent=self.agent,
            input=input,
            previous_response_id=last_response_id,
        )

        # Return the streamed response
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                context.streaming_response.queue_text_chunk(event.data.delta)
        
        # Return last response id
        return result.last_response_id
    
    async def get_suggested_actions(self, input: str, last_response_id: str | None = None) -> SuggestedActionsAgentResponse:
        # Generate agent response
        logger.info("Generating suggested actions from agent.")
        result = await self._get_response(input=input, last_response_id=last_response_id)

        # Parse the response into SuggestedActionsAgentResponse
        try:
            logger.info("Parsing suggested actions response from agent.")
            suggested_actions_response = SuggestedActionsAgentResponse.model_validate_json(result)
        except ValidationError as e:
            logger.error(f"Error parsing suggested actions response: {e}")
            suggested_actions_response = SuggestedActionsAgentResponse(suggested_actions=[])

        return suggested_actions_response

    async def _get_response(self, input: str, last_response_id: str | None = None) -> str:
        # Generate agent response
        result = await self.runner.run(
            starting_agent=self.agent,
            input=input,
            previous_response_id=last_response_id,
        )

        # Return the full response text
        return result.final_output
