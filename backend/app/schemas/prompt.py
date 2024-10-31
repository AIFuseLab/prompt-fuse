from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class PromptCreate(BaseModel):
    name: Optional[str] = None
    prompt: Optional[str] = None
    notes: Optional[str] = None
    version: Optional[float] = 0.0
    llm_id: Optional[UUID] = None
    prompt_template_id: Optional[UUID] = None

class PromptUpdate(BaseModel):
    name: Optional[str] = None
    prompt: Optional[str] = None
    notes: Optional[str] = None
    version: Optional[float] = None
    llm_id: Optional[UUID] = None
    prompt_template_id: Optional[UUID] = None

class PromptResponse(BaseModel):
    id: UUID
    name: Optional[str] = None
    prompt: Optional[str] = None
    notes: Optional[str] = None
    creation_date: datetime
    version: Optional[float] = None
    llm_id: Optional[UUID] = None
    llm_model_name: Optional[str] = None
    prompt_template_id: Optional[UUID] = None

    class Config:
        from_attributes = True

