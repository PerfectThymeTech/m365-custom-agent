from pydantic import BaseModel, Field


class AttachmentContent(BaseModel):
    download_url: str = Field(..., alias="downloadUrl")
    unique_id: str = Field(..., alias="uniqueId")
    file_type: str = Field(..., alias="fileType")


class DataExtractionResult(BaseModel):
    title: str = Field(..., alias="title")
    data: str = Field(..., alias="data")


class DataExtractionResults(BaseModel):
    documents: list[DataExtractionResult] = Field(..., alias="documents")
