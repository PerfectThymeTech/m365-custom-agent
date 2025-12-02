from agents import Agent, Runner, OpenAIResponsesModel
from agents.model_settings import ModelSettings
from openai.types.shared.reasoning import Reasoning
from openai.types.responses import ResponseTextDeltaEvent
from openai import AsyncOpenAI
from microsoft_agents.hosting.core import TurnContext, TurnState


class DocumentAgent:
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
            name="Document Agent",
            tools=[],
            mcp_servers=[],
            instructions=instructions,
            model=model,
            model_settings=model_settings,
        )
        return agent
    
    async def stream_response(self, input: str, last_response_id,  context: TurnContext) -> str:
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