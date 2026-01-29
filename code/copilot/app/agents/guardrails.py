from agents import Agent, GuardrailFunctionOutput, RunContextWrapper, output_guardrail
from app.eval.metrics import EVALUATION_METRICS
from app.models.agents import MessageOutput


@output_guardrail()
async def relevance_guardrail(
    context: RunContextWrapper, agent: Agent, output: MessageOutput
) -> GuardrailFunctionOutput:
    # Evaluate response
    result = EVALUATION_METRICS.RELEVANCE(
        query=context.context.query,
        response=output.response,
    )

    # Return result
    tripwire_triggered = False  # (result.get("relevance_result", "pass") == "pass")
    return GuardrailFunctionOutput(
        output_info=f"{result}",
        tripwire_triggered=tripwire_triggered,
    )
