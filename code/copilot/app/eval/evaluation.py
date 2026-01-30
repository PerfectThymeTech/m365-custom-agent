from app.eval.metrics import EVALUATION_METRICS
from app.logs import setup_logging

logger = setup_logging(__name__)


class Evaluator:
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.metrics = EVALUATION_METRICS

    def evaluate_all_metrics(self, query: str, response: str) -> dict:
        results = {
            "relevance": self.evaluate_relevance(query, response),
            "self_harm": self.evaluate_self_harm(query, response),
        }
        return results

    def evaluate_relevance(self, query: str, response: str) -> dict[str, str]:
        result = self.metrics.RELEVANCE(
            query=query,
            response=response,
        )

        # Log results
        logger.info(
            f"Relevance Guardrail Result: {result}, Agent Name: {self.agent_name}"
        )
        return result

    def evaluate_self_harm(self, query: str, response: str) -> dict[str, str]:
        result = self.metrics.SELF_HARM(
            query=query,
            response=response,
        )

        # Log results
        logger.info(
            f"Self-Harm Guardrail Result: {result}, Agent Name: {self.agent_name}"
        )
        return result
