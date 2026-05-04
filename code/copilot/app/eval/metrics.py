from app.core.settings import settings
from azure.ai.evaluation import TaskAdherenceEvaluator, RelevanceEvaluator, SelfHarmEvaluator
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential


def get_model_config(endpoint: str, api_key: str, deployment: str) -> dict:
    """
    Generate model configuration dictionary.

    :param endpoint: The API endpoint URL.
    :type endpoint: str
    :param api_key: The API key for authentication.
    :type api_key: str
    :param deployment: The deployment name of the model.
    :type deployment: str
    :return: Model configuration dictionary.
    :rtype: dict
    """
    model_config = {
        "azure_endpoint": endpoint,
        "azure_deployment": deployment,
    }
    if api_key:
        model_config["api_key"] = api_key
    return model_config


def get_credential(
    api_key: str, managed_identity_client_id: str
) -> DefaultAzureCredential | None:
    """
    Get credential based on the presence of an API key.

    :param api_key: The API key for authentication.
    :type api_key: str
    :param managed_identity_client_id: The client id of the managed identity.
    :type managed_identity_client_id: str
    :return: Credential object or None.
    :rtype: DefaultAzureCredential | None
    """
    if api_key:
        return None
    return ManagedIdentityCredential(
        client_id=managed_identity_client_id,
    )
    # return DefaultAzureCredential(
    #     managed_identity_client_id=managed_identity_client_id,
    # )


MODEL_CONFIG = get_model_config(
    api_key=settings.AZURE_OPENAI_API_KEY,
    endpoint=settings.AZURE_OPENAI_ENDPOINT,
    deployment=settings.AZURE_OPENAI_MODEL_NANO_NAME,
)
CREDENTIAL = get_credential(
    api_key=settings.AZURE_OPENAI_API_KEY,
    managed_identity_client_id=settings.MANAGED_IDENTITY_CLIENT_ID,
)
AZURE_AI_PROJECT = settings.AZURE_AI_FOUNDRY_PROJECT_ENDPOINT


class EvaluationMetrics:
    """
    Evaluation Metrics Singleton.
    """

    RELEVANCE = RelevanceEvaluator(
        model_config=MODEL_CONFIG,
        credential=CREDENTIAL,
        is_reasoning_model=True,
    )
    TASK_ADHERENCE = TaskAdherenceEvaluator(
        model_config=MODEL_CONFIG,
        credential=CREDENTIAL,
        is_reasoning_model=True,
    )
    SELF_HARM = SelfHarmEvaluator(
        azure_ai_project=AZURE_AI_PROJECT,
        credential=CREDENTIAL,
    )


EVALUATION_METRICS = EvaluationMetrics()
