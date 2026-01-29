from typing import Tuple

from agents import Agent, OpenAIResponsesModel, Runner
from agents.model_settings import ModelSettings
from agents.usage import Usage
from app.logs import setup_logging, setup_tracing
from app.models.copilot import AgentTurnContext
from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider
from microsoft_agents.hosting.core import TurnContext
from openai import AsyncOpenAI
from openai.types.responses import ResponseTextDeltaEvent
from openai.types.shared.reasoning import Reasoning

logger = setup_logging(__name__)
tracer = setup_tracing(__name__)


class RootAgent:
    """
    Root base class for different types of agents.
    """

    def __init__(
        self,
        api_key: str,
        endpoint: str,
        model_name: str,
        agent_name: str,
        instructions: str,
        managed_identity_client_id: str = None,
        reasoning_effort: str = "none",
        output_guardrails: list[callable] = [],
    ):
        self.agent = self._create_agent(
            api_key,
            endpoint,
            model_name=model_name,
            agent_name=agent_name,
            instructions=instructions,
            managed_identity_client_id=managed_identity_client_id,
            reasoning_effort=reasoning_effort,
            output_guardrails=output_guardrails,
        )
        self.runner = Runner()

    def _create_agent(
        self,
        api_key: str,
        endpoint: str,
        model_name: str,
        agent_name: str,
        instructions: str,
        managed_identity_client_id: str = None,
        reasoning_effort: str = "none",
        output_guardrails: list[callable] = [],
    ):
        """
        Create and configure the agent.

        :param api_key: The API key for authentication.
        :type api_key: str
        :param endpoint: The API endpoint URL.
        :type endpoint: str
        :param model_name: The name of the model to use.
        :type model_name: str
        :param agent_name: The name of the agent.
        :type agent_name: str
        :param instructions: The instructions for the agent.
        :type instructions: str
        :param managed_identity_client_id: The client id of the managed identity.
        :type managed_identity_client_id: str
        :param reasoning_effort: The level of reasoning effort for the agent.
        :type reasoning_effort: str
        :param output_guardrails: The output guardrails of the agent.
        :type output_guardrails: list[callable]
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
                ),
                "https://cognitiveservices.azure.com/.default",
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
            name=agent_name,
            tools=[],
            mcp_servers=[],
            instructions=instructions,
            model=model,
            model_settings=model_settings,
            output_guardrails=output_guardrails,
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

    # TODO: https://cookbook.openai.com/examples/how_to_handle_rate_limits
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
        # Create turn context
        agent_turn_context = AgentTurnContext(
            query=input,
        )

        # with tracer.start_as_current_span("RootAgent.stream_response"):
        # Generate agent response
        result = self.runner.run_streamed(
            starting_agent=self.agent,
            input=input,
            previous_response_id=last_response_id,
            context=agent_turn_context,
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

    # TODO: https://cookbook.openai.com/examples/how_to_handle_rate_limits
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
        # Create turn context
        agent_turn_context = AgentTurnContext(
            query=input,
        )

        # with tracer.start_as_current_span("RootAgent._get_response"):
        # Generate agent response
        result = await self.runner.run(
            starting_agent=self.agent,
            input=input,
            previous_response_id=last_response_id,
            context=agent_turn_context,
        )

        # Track token usage
        self._track_token_usage(result.context_wrapper.usage)

        # Return the full response text
        return result.final_output
