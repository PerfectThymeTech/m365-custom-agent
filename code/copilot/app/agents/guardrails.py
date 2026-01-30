from agents import Agent, GuardrailFunctionOutput, RunContextWrapper, output_guardrail
from app.eval.metrics import EVALUATION_METRICS
from app.logs import setup_logging

logger = setup_logging(__name__)


@output_guardrail()
async def relevance_guardrail(
    context: RunContextWrapper, agent: Agent, output: str
) -> GuardrailFunctionOutput:
    # Evaluate response
    result = EVALUATION_METRICS.RELEVANCE(
        query=context.context.query,
        response=output,
    )

    # Define tripwire condition
    tripwire_triggered = False  # (result.get("relevance_result", "pass") == "pass")

    # Log results
    logger.info(
        f"Relevance Guardrail Result: {result}, Agent Name: {agent.name}, Tripwire Triggered: {tripwire_triggered}"
    )

    return GuardrailFunctionOutput(
        output_info=f"{result}",
        tripwire_triggered=tripwire_triggered,
    )
