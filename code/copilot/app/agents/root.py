from typing import Tuple

from agents import Agent, OpenAIResponsesModel, Runner, OpenAIConversationsSession
from agents.model_settings import ModelSettings
from agents.usage import Usage
from app.core.globals import BACKGROUND_TASKS_DICT
from app.eval.evaluation import Evaluator
from app.logs import setup_logging, setup_tracing
from app.models.attachments import DocumentExtractionResults
from app.models.copilot import AgentTurnContext
from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider
from microsoft_agents.hosting.core import TurnContext
from microsoft_agents.hosting.core.app.typing_indicator import TypingIndicator
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

        self.openai_client = AsyncOpenAI(
            api_key=api_key,
            base_url=f"{endpoint}openai/v1/",
        )
        self.agent = self._create_agent(
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
        model_name: str,
        agent_name: str,
        instructions: str,
        reasoning_effort: str = "none",
        output_guardrails: list[callable] = [],
    ):
        """
        Create and configure the agent.

        :param model_name: The name of the model to use.
        :type model_name: str
        :param agent_name: The name of the agent.
        :type agent_name: str
        :param instructions: The instructions for the agent.
        :type instructions: str
        :param reasoning_effort: The level of reasoning effort for the agent.
        :type reasoning_effort: str
        :param output_guardrails: The output guardrails of the agent.
        :type output_guardrails: list[callable]
        :return: Configured Agent instance.
        :rtype: Agent
        """
        # Define the model
        model = OpenAIResponsesModel(
            model=model_name,
            openai_client=self.openai_client,
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
        logger.info(
            f"Agent usage: Total tokens: {usage.total_tokens}, Input tokens: {usage.input_tokens}, Input token details: {usage.input_tokens_details}, Output tokens: {usage.output_tokens}, Output token details: {usage.output_tokens_details}",
            extra={
                "code": "AGENT_USAGE_TOKENS",
                "total_tokens": usage.total_tokens,
                "input_tokens": usage.input_tokens,
                "input_tokens_details": usage.input_tokens_details,
                "output_tokens": usage.output_tokens,
                "output_tokens_details": usage.output_tokens_details,
            },
        )

    @staticmethod
    async def _check_streaming_has_ended(
        context: TurnContext,
        typing_indicator: TypingIndicator,
        previously_detected_streaming_ended: bool = False,
    ):
        """
        Check if the streaming response has ended.

        :param context: The TurnContext for the current turn.
        :type context: TurnContext
        :param typing_indicator: The TypingIndicator for the current turn.
        :type typing_indicator: TypingIndicator
        :param previously_detected_streaming_ended: Whether streaming end was previously detected.
        :type previously_detected_streaming_ended: bool
        """
        streaming_response_ended = (
            context.streaming_response._ended or context.streaming_response._cancelled
        )
        if streaming_response_ended and not previously_detected_streaming_ended:
            logger.warning(
                "The streaming response has already ended or was cancelled.",
                extra={
                    "code": "STREAMING_RESPONSE_ENDED_OR_CANCELLED",
                    "streaming_response_ended": context.streaming_response._ended,
                    "streaming_response_cancelled": context.streaming_response._cancelled,
                },
            )
            await context.send_activity(
                "It was detected that the streaming response has timed out, or was cancelled. We will send the remaining response as a text message once completed."
            )
            typing_indicator.start()
        return streaming_response_ended or previously_detected_streaming_ended

    # TODO: https://cookbook.openai.com/examples/how_to_handle_rate_limits
    async def stream_response(
        self,
        input: str,
        context: TurnContext,
        document_extraction_results: DocumentExtractionResults = DocumentExtractionResults(),
        conversation_id: str | None = None,
    ) -> Tuple[str, str, int]:
        """
        Stream the agent's response based on the input.

        :param input: The user input to process.
        :type input: str
        :param context: The TurnContext for the current turn.
        :type context: TurnContext
        :param document_extraction_results: The results of document extraction for the current turn.
        :type document_extraction_results: DocumentExtractionResults
        :param conversation_id: The ID of the conversation for context continuity.
        :type conversation_id: str | None
        :return: A tuple containing the last response ID, the full response text, and the total token count.
        :rtype: Tuple[str, str, int]
        """
        with tracer.start_as_current_span("agent_session[openai.agents]"):
            # Create messages
            messages = []
            for document in document_extraction_results.documents:
                messages.append(
                    {
                        "role": "developer",
                        "content": f"""
                        # Context
                        ## Document Extraction
                        ### {document.title}
                        """
                        + "\n\n"
                        + document.data,
                    }
                )
            messages.append(
                {
                    "role": "user",
                    "content": input,
                }
            )

            # Create turn context
            agent_turn_context = AgentTurnContext(
                query=input,
            )

            if not conversation_id:
                conversation  = self.openai_client.conversations.create()
                conversation_id = conversation.id

            # Generate agent response
            result = self.runner.run_streamed(
                starting_agent=self.agent,
                input=messages,
                conversation_id=conversation_id,
                context=agent_turn_context,
            )

            # Check if the streaming response has ended
            streaming_response_ended = False
            typing_indicator = TypingIndicator(context, interval_seconds=0.1)

            # Return the streamed response
            response = ""
            response_remaining = ""
            try:
                async for event in result.stream_events():
                    if event.type == "raw_response_event" and isinstance(
                        event.data, ResponseTextDeltaEvent
                    ):
                        streaming_response_ended = await self._check_streaming_has_ended(
                            context=context,
                            typing_indicator=typing_indicator,
                            previously_detected_streaming_ended=streaming_response_ended,
                        )
                        if not streaming_response_ended:
                            context.streaming_response.queue_text_chunk(
                                event.data.delta
                            )
                        else:
                            response_remaining += event.data.delta
                        response += event.data.delta
            except Exception as e:
                logger.error(
                    f"Error streaming agent response: {e}",
                    exc_info=True,
                    extra={"code": "AGENT_RESPONSE_STREAMING_ERROR"},
                )
                raise e

        # Stop the typing indicator if it was started
        if streaming_response_ended:
            typing_indicator.stop()
            if response_remaining:
                await context.send_activity(response_remaining)

        # Track consumed tokens
        usage = result.context_wrapper.usage
        self._track_token_usage(usage)

        # Remove developer messages from the conversation history to avoid sending them back to the model in future turns, while keeping them in the agent turn context for evaluation and logging purposes
        conversation_items = await self.openai_client.conversations.items.list(
            conversation_id=conversation_id
        )
        for item in conversation_items.data:
            if item.role == "developer":
                await self.openai_client.conversations.items.delete(
                    conversation_id=conversation_id, item_id=item.id
                )

        # Create background task to evaluate agent response
        BACKGROUND_TASKS_DICT[context.activity.id].add_task(
            Evaluator(agent_name=self.agent.name).evaluate_all_metrics,
            query=input,
            response=response,
            system_message=self.agent.instructions,
            tool_definitions=self.agent.tools,
            tool_calls=[],
        )

        # Return last response id, the full response, and the total token count
        return conversation_id, response, usage.total_tokens

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
        with tracer.start_as_current_span("agent_session[openai.agents]"):
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
