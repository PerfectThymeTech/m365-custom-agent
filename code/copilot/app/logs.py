import logging
import os

from app.core.settings import settings
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
from azure.identity import DefaultAzureCredential


def setup_logging(module) -> logging.Logger:
    """Setup logging and event handler.

    RETURNS (Logger): The logger object to log activities.
    """
    logger = logging.getLogger(module)
    logger.setLevel(settings.LOGGING_LEVEL)

    # Create stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(settings.LOGGING_FORMAT))
    logger.addHandler(stream_handler)
    return logger


def setup_opentelemetry():
    """
    Setup OpenTelemetry for Azure Monitor integration.

    RETURNS: None
    """
    # Configure basic logging configuration
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(settings.LOGGING_FORMAT))
    logging.basicConfig(
        format=settings.LOGGING_FORMAT,
        handlers=[stream_handler],
        level=settings.LOGGING_LEVEL,
    )

    if settings.APPLICATIONINSIGHTS_CONNECTION_STRING:
        credential = None
        connection_string = settings.APPLICATIONINSIGHTS_CONNECTION_STRING
    else:
        credential = DefaultAzureCredential()
        connection_string = None

    # Configure azure monitor
    configure_azure_monitor(
        credential=credential,
        connection_string=connection_string,
        enable_live_metrics=True,
        enable_performance_counters=True,
        enable_trace_based_sampling_for_logs=False,
        instrumentation_options={
            "azure_sdk": {
                "enabled": True
            },
            "django": {
                "enabled": False
            },
            "fastapi": {
                "enabled": True
            },
            "flask": {
                "enabled": False
            },
            "psycopg2": {
                "enabled": False
            },
            "requests": {
                "enabled": False
            },
            "urllib": {
                "enabled": False
            },
            "urllib3": {
                "enabled": False
            },
        },
        storage_directory=os.path.join(settings.HOME_DIRECTORY, "azure_monitor"),
    )

    # Add additional instrumentations and configurations
    AioHttpClientInstrumentor().instrument()
