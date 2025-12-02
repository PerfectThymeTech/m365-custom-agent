import logging
from typing import Optional

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.models.core import AuthorizationTypes


class Settings(BaseSettings):
    # General settings
    PROJECT_NAME: str = "CustomCopilot"
    SERVER_NAME: str = "CustomCopilot"
    APP_VERSION: str = "v0.1.0"
    API_V1_STR: str = "/api/v1"

    # Deployment settings
    WEBSITE_NAME: str = Field(default="test", alias="WEBSITE_SITE_NAME")
    WEBSITE_INSTANCE_ID: str = Field(default="0", alias="WEBSITE_INSTANCE_ID")
    HOME_DIRECTORY: str = Field(default="", alias="HOME")
    BASE_URL: str = Field(..., alias=AliasChoices("BASE_URL", "CONTAINER_APP_HOSTNAME", "WEBSITE_HOSTNAME"))

    # Logging settings
    DEBUG: bool = False
    LOGGING_LEVEL: int = logging.INFO
    LOGGING_SAMPLING_RATIO: float = 1.0
    LOGGING_SCHEDULE_DELAY: int = 5000
    LOGGING_FORMAT: str = "[%(asctime)s] [%(levelname)s] [%(module)-8.8s] %(message)s"
    APPLICATIONINSIGHTS_CONNECTION_STRING: str = None

    # Agent SDK settings
    AUTH_TYPE: AuthorizationTypes = AuthorizationTypes.CLIENT_SECRET
    TENANT_ID: Optional[str] = None
    CLIENT_ID: Optional[str] = None
    CLIENT_SECRET: Optional[str] = None
    FEDERATED_CLIENT_ID: Optional[str] = None
    FEDERATED_TOKEN_FILE: Optional[str] = None
    SCOPES: list[str] = ["https://api.botframework.com/.default"]

    # Azure Document Intelligence settings
    AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT: str
    AZURE_DOCUMENT_INTELLIGENCE_API_KEY: str

    # Cosmos DB settings
    AZURE_COSMOS_ENDPOINT: str
    AZURE_COSMOS_KEY: str
    AZURE_COSMOS_DATABASE_ID: str
    AZURE_COSMOS_CONTAINER_ID: str = "user-state"

    # Open AI settings
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_MODEL_NAME: str = Field(
        default="gpt-5.1",
        alias=AliasChoices("AZURE_OPENAI_MODEL_NAME", "AZURE_OPENAI_DEPLOYMENT_NAME"),
    )

    # Instruction settings
    INSTRUCTIONS_DOCUMENT_AGENT: str = """
    # Objective
    You are a helpful assistant that extracts relevant information from PDF documents based on user queries.

    # Input
    You have access to the following input:
    - Document Extraction: A JSON structure containing all the information of the respective document the user refers to.

    # Instructions
    - Analyze the provided content to find the information needed to answer the user's question.
    - Use the JSON data to assist in extracting the required information.
    - Assume the JSON data is accurate and complete.
    - Validate the extracted data for accuracy and completeness by cross-referencing with the provided JSON.

    # Response Format
    - Provide all responses in markdown format.
    - Provide structured answers with headers and bullet points.
    - Provide clear, short and concise answers, citing specific sections or pages from the PDF when relevant.
    - Always suggest follow-up activities at the end.

    # Context

    ## Document Extraction
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")


settings = Settings()
