from pydantic import BaseModel, Field


class ScenarioDefinition(BaseModel):
    title: str = Field(..., alias="title")
    description: str = Field(..., alias="description")
    prompt: str = Field(..., alias="prompt")


class ScenarioDefinitions(BaseModel):
    scenarios: list[ScenarioDefinition] = Field(default=[], alias="scenarios")
