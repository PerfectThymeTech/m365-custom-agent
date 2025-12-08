import asyncio
import json

import aiohttp
from app.logs import setup_logging
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import (
    AnalyzeDocumentRequest,
    DocumentAnalysisFeature,
)
from azure.core.credentials import AzureKeyCredential

logger = setup_logging(__name__)


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
