from typing import Tuple

from agents import Agent, OpenAIResponsesModel, Runner
from agents.items import TResponseInputItem
from agents.model_settings import ModelSettings
from agents.usage import Usage
from app.agents.session import AgentSession
from app.logs import setup_logging
from app.models.attachments import DocumentExtractionResults
from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider
from microsoft_agents.hosting.core import TurnContext
from microsoft_agents.hosting.core.app.typing_indicator import TypingIndicator
from openai import AsyncOpenAI
from openai.types.responses import ResponseTextDeltaEvent
from openai.types.shared.reasoning import Reasoning

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
        agent_name: str,
        instructions: str,
        managed_identity_client_id: str = None,
        reasoning_effort: str = "none",
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

        # Define the model and client
        self.openai_client = AsyncOpenAI(
            api_key=api_key,
            base_url=f"{endpoint}openai/v1/",
        )

        # Create agent
        self.agent = self._create_agent(
            model_name=model_name,
            agent_name=agent_name,
            instructions=instructions,
            reasoning_effort=reasoning_effort,
        )
        self.model_name = model_name
        self.runner = Runner()

    def _create_agent(
        self,
        model_name: str,
        agent_name: str,
        instructions: str,
        reasoning_effort: str = "none",
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
            store=False,
            extra_body={"include": ["reasoning.encrypted_content"]},
        )

        # Define the agent
        agent = Agent(
            name=agent_name,
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
        logger.info(f"Agent usage. Total tokens: {usage.total_tokens}")
        logger.info(
            f"Agent usage. Input tokens: {usage.input_tokens}, Input token details: {usage.input_tokens_details}"
        )
        logger.info(
            f"Agent usage. Output tokens: {usage.output_tokens}, Output token details: {usage.output_tokens_details}"
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
        conversation_history: list[TResponseInputItem] = [],
        document_extraction_results: DocumentExtractionResults = DocumentExtractionResults(),
        compaction_threshold: int = 8000000,
    ) -> Tuple[str, str, list[TResponseInputItem]]:
        """
        Stream the agent's response based on the input.

        :param input: The user input to process.
        :type input: str
        :param context: The TurnContext for the current turn.
        :type context: TurnContext
        :param document_extraction_results: The results of document extraction for the current turn.
        :type document_extraction_results: DocumentExtractionResults
        :param conversation_history: The conversation history for the agent.
        :type conversation_history: list[TResponseInputItem]
        :param compaction_threshold: The token count threshold to trigger compaction.
        :type compaction_threshold: int
        :return: A tuple containing the full response text and the updated conversation history.
        :rtype: Tuple[str, list[TResponseInputItem]]
        """
        messages = []
        for document in document_extraction_results.documents:
            logger.info(
                f"Appending document '{document.title}' to agent context.",
                extra={
                    "code": "AGENT_RESPONSE_STREAMING_APPENDING_DOCUMENT_TO_CONTEXT",
                    "document_title": document.title,
                },
            )
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
        logger.info(
            f"Number of messages for agent: {len(messages)}",
            extra={
                "code": "AGENT_RESPONSE_STREAMING_CONSTRUCTED_MESSAGES",
                "num_messages": len(messages),
            },
        )

        # Create session with conversation history for context continuity in streaming
        session = AgentSession(
            session_id=context.activity.id,
            openai_client=self.openai_client,
        )
        session.add_items(items=conversation_history)
        # Generate agent response
        result = self.runner.run_streamed(
            starting_agent=self.agent,
            input=messages,
            session=session,
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
                        context.streaming_response.queue_text_chunk(event.data.delta)
                    else:
                        response_remaining += event.data.delta
                    response += event.data.delta
        except Exception as e:
            logger.error(f"Error streaming agent response: {e}", exc_info=True)
            raise e

        # Stop the typing indicator if it was started
        if streaming_response_ended:
            typing_indicator.stop()
            if response_remaining:
                await context.send_activity(response_remaining)

        # Track consumed tokens
        usage = result.context_wrapper.usage
        self._track_token_usage(usage)

        # Clean up history
        await session.remove_developer_items()
        if usage.total_tokens > compaction_threshold:
            logger.warning(
                f"Compaction threshold exceeded: {usage.total_tokens} tokens used.",
                extra={
                    "code": "AGENT_RESPONSE_STREAMING_COMPACTION_THRESHOLD_EXCEEDED",
                    "total_tokens": usage.total_tokens,
                    "compaction_threshold": compaction_threshold,
                },
            )
            await session.compact_history(model_name=self.model_name)
        history = await session.get_items()

        # Return last response id and the full response
        return (response, history)

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
