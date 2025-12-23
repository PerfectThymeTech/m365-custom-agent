import asyncio
import base64
import json
import zlib
from typing import Tuple

import aiohttp
from app.agents.summarizer import SummarizerAgent
from app.logs import setup_logging
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import (
    AnalyzeDocumentRequest,
    DocumentAnalysisFeature,
    DocumentContentFormat,
)
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential

logger = setup_logging(__name__)


class FileExtractionClient:
    def __init__(self, api_key: str, endpoint: str, managed_identity_client_id: str = None,):
        """
        Initialize the FileExtractionClient with Azure Document Intelligence credentials.

        :param self: The instance of the FileExtractionClient.
        :type self: FileExtractionClient
        :param api_key: The API key for Azure Document Intelligence.
        :type api_key: str
        :param endpoint: The endpoint URL for Azure Document Intelligence.
        :type endpoint: str
        :param managed_identity_client_id: The client id of the managed identity.
        :type managed_identity_client_id: str
        """
        if api_key:
            credential = AzureKeyCredential(key=api_key)
        else:
            credential = DefaultAzureCredential(
                managed_identity_client_id=managed_identity_client_id,
            )
        self.document_intelligence_client = DocumentIntelligenceClient(
            endpoint=endpoint, credential=credential
        )

    async def extract_data(self, file_url: str) -> dict:
        """
        Extract data from a document at the given URL.

        :param self: The instance of the FileExtractionClient.
        :type self: FileExtractionClient
        :param file_url: The URL of the file to extract data from.
        :type file_url: str
        :return: The extracted data as a dictionary.
        :rtype: dict
        """
        # Analyze document
        logger.debug(f"Starting data extraction for file URL: {file_url}")
        extract_data_result = await asyncio.create_task(
            self._extract_data(
                file_url,
                features=[],  # [DocumentAnalysisFeature.OCR_HIGH_RESOLUTION],
                content_format=DocumentContentFormat.MARKDOWN,
            )
        )

        return extract_data_result

    async def _extract_data(
        self,
        file_url: str,
        features: list[DocumentAnalysisFeature],
        content_format: DocumentContentFormat,
    ) -> dict:
        """
        Extract data from a document at the given URL using specified features.

        :param self: The instance of the FileExtractionClient.
        :type self: FileExtractionClient
        :param file_url: The URL of the file to extract data from.
        :type file_url: str
        :param features: The features to use for document analysis.
        :type features: list[DocumentAnalysisFeature]
        :return: The extracted data as a dictionary.
        :rtype: dict
        """
        try:
            # Download file content
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as response:
                    file_content = await response.read()

            # Create body for analysis
            body = AnalyzeDocumentRequest(bytes_source=file_content)

            # Analyze document
            poller = self.document_intelligence_client.begin_analyze_document(
                model_id="prebuilt-layout",
                body=body,
                features=features,
                output_content_format=content_format,
            )
            result = poller.result()
            result_dict = result.as_dict()
        except Exception as e:
            logger.error(f"Error during document analysis: {e}")
            raise e

        return result_dict

    async def _summarize_tables(
        self,
        tables: list[dict],
        api_key: str,
        endpoint: str,
        model_name: str,
        instructions: str,
        managed_identity_client_id: str = None,
        reasoning_effort: str = "minimal",
    ) -> Tuple[dict, dict]:
        """
        Summarize tables using the SummarizerAgent.

        :param self: The instance of the FileExtractionClient.
        :type self: FileExtractionClient
        :param tables: The list of tables to summarize.
        :type tables: list[dict]
        :param api_key: The API key for the agent.
        :type api_key: str
        :param endpoint: The endpoint URL for the agent.
        :type endpoint: str
        :param model_name: The name of the model to use.
        :type model_name: str
        :param instructions: The instructions for the agent.
        :type instructions: str
        :param managed_identity_client_id: The client id of the managed identity.
        :type managed_identity_client_id: str
        :param reasoning_effort: The level of reasoning effort for the agent.
        :type reasoning_effort: str
        :return: A tuple containing the table summaries and the table collection.
        :rtype: Tuple[dict, dict]
        """
        # Create table collection
        table_summaries = {}
        table_collection = {}

        # Define summarizer agent
        summarizer_agent = SummarizerAgent(
            api_key=api_key,
            endpoint=endpoint,
            model_name=model_name,
            instructions=instructions,
            managed_identity_client_id=managed_identity_client_id,
            reasoning_effort=reasoning_effort,
        )

        # Define task list
        tasks = []

        for table in tables:
            # Summarize each table
            table_content = json.dumps(table)

            # Create task
            task = asyncio.create_task(
                await summarizer_agent.get_table_summary(
                    table=table_content,
                    last_response_id=None,
                )
            )
            tasks.append((task, table_content))

        # Gather results
        results = await asyncio.gather(*(t[0] for t in tasks))

        for table_summary_response, table_content in zip(
            results, (t[1] for t in tasks)
        ):
            if table_summary_response:
                # Add table summary to collections
                table_collection[table_summary_response.table_key] = table_content
                table_summaries[table_summary_response.table_key] = (
                    table_summary_response.summary
                )
            else:
                logger.error("Table summary response is None, skipping.")

        return table_summaries, table_collection

    async def clean_extracted_data(
        self,
        data: dict,
        keep_paragraphs: bool,
        keep_tables: bool,
        summarize_tables: bool,
        api_key: str,
        endpoint: str,
        model_name: str,
        instructions: str,
        reasoning_effort: str = "minimal",
    ) -> Tuple[str, dict]:
        """
        Clean and minify the extracted data.

        :param self: The instance of the FileExtractionClient.
        :type self: FileExtractionClient
        :param data: The data to clean.
        :type data: dict
        :param keep_paragraphs: Whether to keep paragraphs in the cleaned data.
        :type keep_paragraphs: bool
        :param keep_tables: Whether to keep tables in the cleaned data.
        :type keep_tables: bool
        :param summarize_tables: Whether to summarize tables in the cleaned data.
        :type summarize_tables: bool
        :param api_key: The API key for the agent.
        :type api_key: str
        :param endpoint: The endpoint URL for the agent.
        :type endpoint: str
        :param model_name: The name of the model to use.
        :type model_name: str
        :param instructions: The instructions for the agent.
        :type instructions: str
        :param reasoning_effort: The level of reasoning effort for the agent.
        :type reasoning_effort: str
        :return: A tuple containing the cleaned and minified data as a JSON string and the table collection.
        :rtype: Tuple[str, dict]
        """
        # Implement any cleaning logic here
        cleaned_data = {}
        table_collection = {}

        # Process content
        data_content = data.get("content", "")
        cleaned_data["content"] = data_content

        # Process paragraphs
        if keep_paragraphs:
            data_paragraphs = data.get("paragraphs", [])
            for paragraph in data_paragraphs:
                if "spans" in paragraph:
                    del paragraph["spans"]
                if "boundingRegions" in paragraph:
                    paragraph["pageNumber"] = paragraph["boundingRegions"][0][
                        "pageNumber"
                    ]
                    del paragraph["boundingRegions"]
            cleaned_data["paragraphs"] = data_paragraphs

        # Process tables
        if keep_tables:
            data_tables = data.get("tables", [])
            for table in data_tables:
                if "boundingRegions" in table:
                    table["pageNumber"] = table["boundingRegions"][0]["pageNumber"]
                    del table["boundingRegions"]
                if "spans" in table:
                    del table["spans"]
                if "caption" in table:
                    del table["caption"]["spans"]
                    del table["caption"]["elements"]

                for cell in table.get("cells", []):
                    if "spans" in cell:
                        del cell["spans"]
                    if "elements" in cell:
                        del cell["elements"]
                    if "boundingRegions" in cell:
                        del cell["boundingRegions"]

            cleaned_data["tables"] = data_tables

            # Summarize tables
            if summarize_tables:
                table_summaries, table_collection = await self._summarize_tables(
                    tables=cleaned_data["tables"],
                    api_key=api_key,
                    endpoint=endpoint,
                    model_name=model_name,
                    instructions=instructions,
                    reasoning_effort=reasoning_effort,
                )
            cleaned_data["tables"] = table_summaries

        # Minify JSON structure by removing unnecessary whitespace
        cleaned_data_minified = json.dumps(cleaned_data, separators=(",", ":"))

        return cleaned_data_minified, table_collection

    @staticmethod
    def compress_string(input_string: str) -> str:
        """
        Compress a string using zlib and encode it with base64.

        :param input_string: The string to compress.
        :type input_string: str
        :return: The compressed and base64-encoded string.
        :rtype: str
        """
        compressed = zlib.compress(input_string.encode("utf-8"), level=9)
        return base64.b64encode(compressed).decode("utf-8")

    @staticmethod
    def decompress_string(compressed_string: str) -> str:
        """
        Decompress a base64-encoded zlib-compressed string.

        :param compressed_string: The compressed string to decompress.
        :type compressed_string: str
        :return: The decompressed string.
        :rtype: str
        """
        compressed_bytes = base64.b64decode(compressed_string.encode("utf-8"))
        decompressed = zlib.decompress(compressed_bytes)
        return decompressed.decode("utf-8")
