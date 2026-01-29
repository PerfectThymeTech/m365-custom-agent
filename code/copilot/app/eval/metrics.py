from azure.ai.evaluation import RelevanceEvaluator
from azure.identity import DefaultAzureCredential
from core.settings import settings
from pydantic import BaseModel


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


def get_credential(api_key: str) -> DefaultAzureCredential | None:
    """
    Get credential based on the presence of an API key.

    :param api_key: The API key for authentication.
    :type api_key: str
    :return: Credential object or None.
    :rtype: DefaultAzureCredential | None
    """
    if api_key:
        return None
    return DefaultAzureCredential()


MODEL_CONFIG = get_model_config(
    api_key=settings.AZURE_OPENAI_API_KEY,
    endpoint=settings.AZURE_OPENAI_ENDPOINT,
    deployment=settings.AZURE_OPENAI_MODEL_NANO_NAME,
)
CREDENTIAL = get_credential(settings.AZURE_OPENAI_API_KEY)


class EvaludationMetrics(BaseModel):
    """
    Evaluation Metrics Singleton.
    """

    RELEVANCE = RelevanceEvaluator(
        model_config=MODEL_CONFIG,
        credential=CREDENTIAL,
    )


EVALUATION_METRICS = EvaludationMetrics()
