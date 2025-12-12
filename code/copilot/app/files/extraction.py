import asyncio
import base64
import json
from typing import Optional

import aiohttp
import logging
# from app.logs import setup_logging
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import (
    AnalyzeDocumentRequest,
    DocumentAnalysisFeature,
)
from azure.core.credentials import AzureKeyCredential

logger = logging.getLogger(__name__)


class FileExtractionClient:
    def __init__(self, api_key: str, endpoint: str):
        self.document_intelligence_client = DocumentIntelligenceClient(
            endpoint=endpoint, credential=AzureKeyCredential(key=api_key)
        )

    async def extract_data(self, file_url: str) -> dict:
        # Analyze document
        logger.debug(f"Starting data extraction for file URL: {file_url}")
        extract_data_result = await asyncio.create_task(
            self._extract_data(
                file_url, features=[DocumentAnalysisFeature.OCR_HIGH_RESOLUTION]
            )
        )

        return extract_data_result

    async def _extract_data(
        self, file_url: str, features: list[DocumentAnalysisFeature]
    ) -> dict:
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
            )
            result = poller.result()
            result_dict = result.as_dict()
        except Exception as e:
            logger.error(f"Error during document analysis: {e}")
            raise e

        return result_dict

    def clean_extracted_data(self, data: dict) -> str:
        # Implement any cleaning logic here
        cleaned_data = {}

        # Process content
        data_content = data.get("content", "")
        cleaned_data["content"] = data_content

        # Process tables
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

        # Process paragraphs
        data_paragraphs = data.get("paragraphs", [])
        for paragraph in data_paragraphs:
            if "spans" in paragraph:
                del paragraph["spans"]
            if "boundingRegions" in paragraph:
                paragraph["pageNumber"] = paragraph["boundingRegions"][0]["pageNumber"]
                del paragraph["boundingRegions"]
        cleaned_data["paragraphs"] = data_paragraphs

        # Minify JSON structure by removing unnecessary whitespace
        cleaned_data_minified = json.dumps(cleaned_data, separators=(",", ":"))

        return cleaned_data_minified


class ContentUnderstandingClient:
    def __init__(self, api_key: str, endpoint: str, api_version: str = "2025-11-01", analyzer_id: str = "prebuilt-layout"):
        self.api_key = api_key
        self.endpoint = endpoint
        self.analyzer_id = analyzer_id
        self.api_version = api_version
        self.header = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": self.api_key,
        }

    async def extract_data(self, file_url: str, range: str = "1-") -> dict:
        # Analyze document
        logger.debug(f"Starting data extraction for file URL: {file_url}")
        extract_data_result = await asyncio.create_task(
            self._extract_data(
                file_url, features=[] #[DocumentAnalysisFeature.OCR_HIGH_RESOLUTION]
            )
        )

        return extract_data_result

    async def _extract_data(
        self, file_url: str, features: list[DocumentAnalysisFeature]
    ) -> dict:
        try:
            # Download file content
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as response:
                    file_content = await response.read()
            
            ########################
            # Prepare for analysis #
            ########################
            # Configure endpoint
            endpoint = f"{self.endpoint}/contentunderstanding/defaults?api-version={self.api_version}"

            # Create body
            body = {
                "modelDeployments": {
                    "gpt-5.1": "gpt-5.1",
                    "text-embedding-3-large": "text-embedding-3-large"
                }
            }

            # Send preparation request
            async with aiohttp.ClientSession() as session:
                async with session.patch(url=endpoint, json=body, headers=self.header) as response:
                    prep_result_json = await response.json()
                    prep_result_dict = dict(prep_result_json)
            
            # print(f"Preparation Result: {prep_result_dict}")
            
            ########################
            # Analyze the document #
            ########################
            # Configure options
            string_encoding = "utf-8"
            processing_location = "global"
            range = None

            # Configure endpoint
            endpoint = f"{self.endpoint}/contentunderstanding/analyzers/{self.analyzer_id}:analyzeBinary?api-version={self.api_version}&stringEncoding={string_encoding}&processingLocation={processing_location}&range={range if range else '1-'}"

            # Create body with byte content encoded according to string encoding
            body = file_content

            # Send analysis request
            async with aiohttp.ClientSession() as session:
                async with session.post(url=endpoint, data=body, headers=self.header) as response:
                    result_json = await response.json()
                    result_dict = dict(result_json)
                    operation_location = response.headers.get("Operation-Location", "")
            
            # print("Operation Location:", operation_location)
            # print("Initial Result Dict:", result_dict)
            ################
            # Check status #
            ################
            # Conigure options
            status = result_dict.get("status", "")

            # Configure endpoint
            endpoint = operation_location

            # Poll for result until completed
            while str.lower(status) in ["running", "notstarted"]:
                await asyncio.sleep(1)  # Wait before polling again
                async with aiohttp.ClientSession() as session:
                    async with session.get(url=endpoint, headers=self.header) as response:
                        result_json = await response.json()
                        result_dict = dict(result_json)
                        status = result_dict.get("status", "")
            
            # print("Polled Result Dict:", result_dict)

        except Exception as e:
            logger.error(f"Error during document analysis: {e}")
            raise e

        return result_dict

    def clean_extracted_data(self, data: dict) -> str:
        # Implement any cleaning logic here
        cleaned_data = {}

        # Process content
        data_content = data.get("content", "")
        cleaned_data["content"] = data_content

        # Process tables
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

        # Process paragraphs
        data_paragraphs = data.get("paragraphs", [])
        for paragraph in data_paragraphs:
            if "spans" in paragraph:
                del paragraph["spans"]
            if "boundingRegions" in paragraph:
                paragraph["pageNumber"] = paragraph["boundingRegions"][0]["pageNumber"]
                del paragraph["boundingRegions"]
        cleaned_data["paragraphs"] = data_paragraphs

        # Minify JSON structure by removing unnecessary whitespace
        cleaned_data_minified = json.dumps(cleaned_data, separators=(",", ":"))

        return cleaned_data_minified
