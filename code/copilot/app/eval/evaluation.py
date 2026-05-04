from app.eval.metrics import EVALUATION_METRICS
from app.logs import setup_logging, setup_tracing

logger = setup_logging(__name__)
tracer = setup_tracing(__name__)


class Evaluator:
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.metrics = EVALUATION_METRICS

    def evaluate_all_metrics(
        self,
        query: str,
        response: str,
        system_message: str,
        tool_definitions: list[dict],
        tool_calls: list[dict],
    ) -> dict:
        with tracer.start_as_current_span("evaluate_all_metrics"):
            results = {
                # "relevance": self.evaluate_relevance(query, response),
                "self_harm": self.evaluate_self_harm(query, response),
                "task_adherence": self.evaluate_task_adherence(
                    query, response, system_message, tool_definitions, tool_calls
                ),
            }
            logger.info(results)
            return results

    def evaluate_relevance(self, query: str, response: str) -> dict[str, str]:
        result = self.metrics.RELEVANCE(
            query=query,
            response=response,
        )

        # Log results
        logger.info(
            f"Relevance Guardrail Status: 'completed', Agent Name: '{self.agent_name}'"
        )
        logger.info(result)
        return result

    def evaluate_task_adherence(
        self,
        query: str,
        response: str,
        system_message: str,
        tool_definitions: list[dict],
        tool_calls: list[dict],
    ) -> dict[str, str]:
        result = self.metrics.TASK_ADHERENCE(
            query=query,
            response=response,
            system_message=system_message,
            tool_definitions=tool_definitions,
            tool_calls=tool_calls,
        )

        # Log results
        logger.info(
            f"Task Adherence Guardrail Status: 'completed', Agent Name: '{self.agent_name}'"
        )
        logger.info(result)
        return result

    def evaluate_self_harm(self, query: str, response: str) -> dict[str, str]:
        result = self.metrics.SELF_HARM(
            query=query,
            response=response,
        )

        # Log results
        logger.info(
            f"Self-Harm Guardrail Status: 'completed', Agent Name: '{self.agent_name}'"
        )
        logger.info(result)
        return result
