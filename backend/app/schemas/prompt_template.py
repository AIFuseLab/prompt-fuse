from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime

class PromptTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    project_id: Optional[UUID] = None

class PromptTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    project_id: Optional[UUID] = None

class PromptTemplateResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    creation_date: datetime
    updated_at: datetime
    number_of_prompts: int
    project_id: Optional[UUID]

    model_config = ConfigDict(from_attributes=True) 