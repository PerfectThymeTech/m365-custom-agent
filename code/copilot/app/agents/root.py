from typing import Tuple

from agents import Agent, OpenAIResponsesModel, Runner
from agents.model_settings import ModelSettings
from agents.usage import Usage
from app.logs import setup_logging
from microsoft_agents.hosting.core import TurnContext
from openai import AsyncOpenAI
from openai.types.responses import ResponseTextDeltaEvent
from openai.types.shared.reasoning import Reasoning
from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider

logger = setup_logging(__name__)


class RootAgent:
    """
    Root base class for different types of agents.
    """

    def __init__(
        self,
        api_key: str,
        endpoint: str,
        model_name: str,
        instructions: str,
        managed_identity_client_id: str = None,
        reasoning_effort: str = "none",
    ):
        self.agent = self._create_agent(
            api_key,
            endpoint,
            model_name=model_name,
            instructions=instructions,
            managed_identity_client_id=managed_identity_client_id,
            reasoning_effort=reasoning_effort,
        )
        self.runner = Runner()

    def _create_agent(
        self,
        api_key: str,
        endpoint: str,
        model_name: str,
        instructions: str,
        managed_identity_client_id: str = None,
        reasoning_effort: str = "none",
    ):
        """
        Create and configure the agent.

        :param api_key: The API key for authentication.
        :type api_key: str
        :param endpoint: The API endpoint URL.
        :type endpoint: str
        :param model_name: The name of the model to use.
        :type model_name: str
        :param instructions: The instructions for the agent.
        :type instructions: str
        :param managed_identity_client_id: The client id of the managed identity.
        :type managed_identity_client_id: str
        :param reasoning_effort: The level of reasoning effort for the agent.
        :type reasoning_effort: str
        :return: Configured Agent instance.
        :rtype: Agent
        """
        # Define authentication
        if api_key:
            api_key = api_key
        else:
            api_key = get_bearer_token_provider(
                DefaultAzureCredential(
                    managed_identity_client_id=managed_identity_client_id,
                ), "https://cognitiveservices.azure.com/.default"
            )
        
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
            tool_choice="auto",
            parallel_tool_calls=True,
            truncation="auto",
            max_tokens=128000,
            reasoning=Reasoning(effort=reasoning_effort),
            verbosity="low",
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

    @staticmethod
    def _track_token_usage(
        usage: Usage,
    ):
        """
        Log token usage details for the agent.

        :param usage: The Usage object containing token usage details.
        :type usage: Usage
        """
        logger.info(f"Document Agent usage. Total tokens: {usage.total_tokens}")
        logger.info(
            f"Document Agent usage. Input tokens: {usage.input_tokens}, Input token details: {usage.input_tokens_details}"
        )
        logger.info(
            f"Document Agent usage. Output tokens: {usage.output_tokens}, Output token details: {usage.output_tokens_details}"
        )

    async def stream_response(
        self, input: str, context: TurnContext, last_response_id: str | None = None
    ) -> Tuple[str, str]:
        """
        Stream the agent's response based on the input.

        :param input: The user input to process.
        :type input: str
        :param context: The TurnContext for the current turn.
        :type context: TurnContext
        :param last_response_id: The ID of the last response for context continuity.
        :type last_response_id: str | None
        :return: A tuple containing the last response ID and the full response text.
        :rtype: Tuple[str, str]
        """
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
        except Exception as e:
            logger.error(f"Error streaming agent response: {e}", exc_info=True)
            raise e

        # Track consumed tokens
        usage = result.context_wrapper.usage
        self._track_token_usage(usage)

        # Return last response id and the full response
        return result.last_response_id, response

    async def _get_response(
        self, input: str, last_response_id: str | None = None
    ) -> str:
        """
        Internal method to get the full response from the agent.

        :param input: The user input to process.
        :type input: str
        :param last_response_id: The ID of the last response for context continuity.
        :type last_response_id: str | None
        :return: The final response text from the agent.
        :rtype: str
        """
        # Generate agent response
        result = await self.runner.run(
            starting_agent=self.agent,
            input=input,
            previous_response_id=last_response_id,
        )

        # Track token usage
        self._track_token_usage(result.context_wrapper.usage)

        # Return the full response text
        return result.final_output
