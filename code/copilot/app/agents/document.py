from typing import Tuple

from agents import Agent, OpenAIResponsesModel, Runner
from agents.model_settings import ModelSettings
from app.logs import setup_logging
from microsoft_agents.hosting.core import TurnContext, TurnState
from openai import APIError, AsyncOpenAI, BadRequestError
from openai.types.responses import ResponseTextDeltaEvent
from openai.types.shared.reasoning import Reasoning

logger = setup_logging(__name__)


class DocumentAgent:
    def __init__(
        self,
        api_key: str,
        endpoint: str,
        model_name: str,
        instructions: str,
        reasoning_effort: str = "none",
    ):
        self.agent = self._create_agent(
            api_key,
            endpoint,
            model_name=model_name,
            instructions=instructions,
            reasoning_effort=reasoning_effort,
        )
        self.runner = Runner()

    def _create_agent(
        self,
        api_key: str,
        endpoint: str,
        model_name: str,
        instructions: str,
        reasoning_effort: str = "none",
    ) -> Agent:
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
            reasoning=Reasoning(effort=reasoning_effort),
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

    async def stream_response(
        self, input: str, last_response_id, context: TurnContext
    ) -> Tuple[str, str]:
        # Generate agent response
        result = self.runner.run_streamed(
            starting_agent=self.agent,
            input=input,
            previous_response_id=last_response_id,
        )

        # Return the streamed response
        response = ""
        try:
            async for event in result.stream_events():
                if event.type == "raw_response_event" and isinstance(
                    event.data, ResponseTextDeltaEvent
                ):
                    context.streaming_response.queue_text_chunk(event.data.delta)
                    response += event.data.delta
        except BadRequestError as e:
            logger.error(
                f"Error generating agent response: {e.message}, code: {e.code}"
            )

            if e.code == "string_above_max_length":
                response_error = "[Error]: The document is too large for me to process. Please upload a smaller document."

                # Add message to inform user
                context.streaming_response.queue_text_chunk(response_error)

            raise e
        except APIError as e:
            logger.error(
                f"API Error generating agent response: {e.message}, code: {e.code}"
            )

            if True:  # TODO: Define Code (e.g. e.code == "string_above_max_length")
                response_error = "The request is too large. Please rephrase your question or upload a smaller document."

                # Add message to inform user
                context.streaming_response.queue_text_chunk(response_error)

            raise e

        # Return last response id and the full response
        return result.last_response_id, response
