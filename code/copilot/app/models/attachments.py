from pydantic import BaseModel, Field


class AttachmentContent(BaseModel):
    download_url: str = Field(..., alias="downloadUrl")
    unique_id: str = Field(..., alias="uniqueId")
    file_type: str = Field(..., alias="fileType")


class DocumentExtractionResult(BaseModel):
    title: str = Field(..., alias="title")
    data: str = Field(..., alias="data")
    added_to_context: bool = Field(default=False, alias="addedToContext")


class DocumentExtractionResults(BaseModel):
    documents: list[DocumentExtractionResult] = Field(default=[], alias="documents")
