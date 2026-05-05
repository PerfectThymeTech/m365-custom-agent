import asyncio
import json
from typing import Tuple

import aiohttp
from app.agents.summarizer import SummarizerAgent
from app.logs import setup_logging
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    AnalysisContent,
    AnalysisResult,
    DocumentContent,
)
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential

logger = setup_logging(__name__)


class FileExtractionClient:
    def __init__(
        self,
        api_key: str,
        endpoint: str,
        managed_identity_client_id: str = None,
    ):
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
        self.content_understanding_client = ContentUnderstandingClient(
            endpoint=endpoint, credential=credential
        )

    async def extract_data(self, file_url: str) -> AnalysisContent | None:
        """
        Extract data from a document at the given URL.

        :param self: The instance of the FileExtractionClient.
        :type self: FileExtractionClient
        :param file_url: The URL of the file to extract data from.
        :type file_url: str
        :return: The extracted data as an AnalysisContent object or None.
        :rtype: AnalysisContent | None
        """
        # Analyze document
        logger.debug(f"Starting data extraction for file URL: {file_url}")
        extract_data_result = await asyncio.create_task(
            self._extract_data(
                file_url,
            )
        )

        return extract_data_result

    async def _extract_data(
        self,
        file_url: str,
    ) -> AnalysisContent | None:
        """
        Extract data from a document at the given URL using specified features.

        :param self: The instance of the FileExtractionClient.
        :type self: FileExtractionClient
        :param file_url: The URL of the file to extract data from.
        :type file_url: str
        :return: The extracted data as an AnalysisContent object or None.
        :rtype: AnalysisContent | None
        """
        try:
            # Download file content
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as response:
                    file_content = await response.read()

            # Analyze document
            poller = self.content_understanding_client.begin_analyze_binary(
                analyzer_id="prebuilt-layout",
                binary_input=file_content,
                content_range=None,
                content_type="application/octet-stream",
                processing_location="global",
            )

            # Get result
            result: AnalysisResult = poller.result()  # Wait for analysis to complete
            result_content = (
                result.contents[0]
                if result.contents and len(result.contents) > 0
                else None
            )

            # Debug log the result content
            logger.debug(
                f"Data extraction completed for file URL: {file_url}, result: {result_content.as_dict() if result_content else None}"
            )

        except Exception as e:
            logger.error(f"Error during document analysis: {e}")
            raise e

        return result_content

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
        data: AnalysisContent | None,
        keep_paragraphs: bool,
        keep_tables: bool,
        keep_figures: bool,
        keep_hyperlinks: bool,
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
        :type data: AnalysisContent | None
        :param keep_paragraphs: Whether to keep paragraphs in the cleaned data.
        :type keep_paragraphs: bool
        :param keep_tables: Whether to keep tables in the cleaned data.
        :type keep_tables: bool
        :param keep_figures: Whether to keep figures in the cleaned data.
        :type keep_figures: bool
        :param keep_hyperlinks: Whether to keep hyperlinks in the cleaned data.
        :type keep_hyperlinks: bool
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

        if data is None:
            logger.warning("No data to clean, returning empty result.")
            return json.dumps(cleaned_data), table_collection

        # Add markdown content
        cleaned_data["markdown"] = data.markdown if data.markdown else ""

        # Process paragraphs
        if isinstance(data, DocumentContent) and keep_paragraphs and data.paragraphs:
            paragraphs = []

            for paragraph in data.paragraphs:
                item = {
                    "content": paragraph.content,
                    "role": paragraph.role,
                }
                paragraphs.append(item)

            cleaned_data["paragraphs"] = paragraphs

        # Process figures
        if isinstance(data, DocumentContent) and keep_figures and data.figures:
            figures = []

            for figure in data.figures:
                item = {
                    "caption": figure.caption,
                    "role": figure.role,
                    "description": figure.description,
                    "kind": figure.kind,
                    "footnotes": [],
                }

                for footnote in figure.footnotes:
                    item_footnote = {
                        "content": footnote.content,
                        "elements": footnote.elements,
                    }
                    item["footnotes"].append(item_footnote)

            cleaned_data["figures"] = figures

        # Process hyperlinks
        if isinstance(data, DocumentContent) and keep_hyperlinks and data.hyperlinks:
            hyperlinks = []

            for hyperlink in data.hyperlinks:
                item = {
                    "content": hyperlink.content,
                    "url": hyperlink.url,
                }
                hyperlinks.append(item)

        # Process tables
        if isinstance(data, DocumentContent) and keep_tables and data.tables:
            tables = []

            for table in data.tables:
                item = {
                    "caption": table.caption,
                    "column_count": table.column_count,
                    "row_count": table.row_count,
                    "role": table.role,
                    "cells": [],
                    "footnotes": [],
                }

                for cell in table.cells:
                    item_cell = {
                        "content": cell.content,
                        "column_index": cell.column_index,
                        "row_index": cell.row_index,
                        "kind": cell.kind,
                    }
                    item["cells"].append(item_cell)

                for footnote in table.footnotes:
                    item_footnote = {
                        "content": footnote.content,
                        "elements": footnote.elements,
                    }
                    item["footnotes"].append(item_footnote)

                tables.append(item)

            cleaned_data["tables"] = tables

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
