from pydantic import BaseModel, Field


class AttachmentContent(BaseModel):
    download_url: str = Field(..., alias="downloadUrl")
    unique_id: str = Field(..., serialization_alias="uniqueId")
    file_type: str = Field(..., serialization_alias="fileType")


class DocumentExtractionResult(BaseModel):
    title: str = Field(..., serialization_alias="title")
    data: str = Field(..., serialization_alias="data")
    appended_to_context: bool = Field(
        default=False, serialization_alias="appendedToContext"
    )


class DocumentExtractionResults(BaseModel):
    documents: list[DocumentExtractionResult] = Field(
        default=[], serialization_alias="documents"
    )
