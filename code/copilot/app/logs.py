import logging
import os

from app.core.settings import settings
from azure.identity import DefaultAzureCredential
from azure.monitor.opentelemetry import configure_azure_monitor
from microsoft_agents.activity import Activity
from microsoft_agents.hosting.core.storage.transcript_logger import TranscriptLogger
from opentelemetry import trace
from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
from opentelemetry.instrumentation.openai_agents import OpenAIAgentsInstrumentor
from opentelemetry.sdk.resources import Resource


def setup_logging(module) -> logging.Logger:
    """Setup logging and event handler.

    :return: The logger object to log activities.
    :rtype: logging.Logger
    """
    logger = logging.getLogger(module)
    logger.setLevel(settings.LOGGING_LEVEL)

    # Create stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(settings.LOGGING_FORMAT))
    logger.addHandler(stream_handler)
    return logger


def setup_tracing(module) -> trace.Tracer:
    """Setup tracing.

    :return: The tracer object to trace activities.
    :rtype: trace.Tracer
    """
    tracer = trace.get_tracer(__name__)
    return tracer


def setup_opentelemetry():
    """
    Setup OpenTelemetry for Azure Monitor integration.

    :return: None
    :rtype: None
    """
    # Configure basic logging configuration
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(settings.LOGGING_FORMAT))
    logging.basicConfig(
        format=settings.LOGGING_FORMAT,
        handlers=[stream_handler],
        level=settings.LOGGING_LEVEL,
    )

    if settings.APPLICATIONINSIGHTS_AUTHENTICATION_STRING:
        credential = DefaultAzureCredential(
            managed_identity_client_id=settings.MANAGED_IDENTITY_CLIENT_ID,
        )
    else:
        credential = None

    # Create OTEL resource
    resource = Resource.create(
        attributes={
            "service.name": settings.WEBSITE_NAME,
            "service.namespace": settings.WEBSITE_NAME,
            "service.instance.id": settings.WEBSITE_INSTANCE_ID,
        }
    )

    # Configure azure monitor
    configure_azure_monitor(
        credential=credential,
        connection_string=settings.APPLICATIONINSIGHTS_CONNECTION_STRING,
        enable_live_metrics=True,
        enable_performance_counters=True,
        enable_trace_based_sampling_for_logs=False,
        instrumentation_options={
            "azure_sdk": {"enabled": True},
            "django": {"enabled": False},
            "fastapi": {"enabled": True},
            "flask": {"enabled": False},
            "psycopg2": {"enabled": False},
            "requests": {"enabled": False},
            "urllib": {"enabled": False},
            "urllib3": {"enabled": False},
        },
        storage_directory=os.path.join(settings.HOME_DIRECTORY, "azure_monitor"),
        resource=resource,
    )

    # Add additional instrumentations and configurations
    AioHttpClientInstrumentor().instrument()
    OpenAIAgentsInstrumentor().instrument(tracer_provider=trace.get_tracer_provider())


class OpenTelemetryTranscriptLogger(TranscriptLogger):
    """
    Docstring for OpenTelemetryTranscriptLogger
    """

    def __init__(self):
        """
        Initialize the OpenTelemetryTranscriptLogger.
        """
        self.logger = setup_logging(__name__)

    async def log_activity(self, activity: Activity):
        """
        Logs the activity using OpenTelemetry.

        :param activity: The Activity object to log.
        :type activity: Activity
        """
        if not activity:
            raise TypeError("Activity is required")

        self.logger.info(activity.model_dump_json())
