from pydantic import BaseModel
from typing import List, Optional, Any
from uuid import UUID
from datetime import datetime
from fastapi import UploadFile, File

class TestCreate(BaseModel):
    test_name: str
    user_input: Optional[str] = None
    prompt_ids: List[UUID]
    input_type: Optional[str] = None
    image_input: Optional[Any] = File(None),
    
class TestUpdate(BaseModel):
    test_name: Optional[str] = None
    user_input: Optional[str] = None

class TestResponse(BaseModel):
    id: UUID
    test_name: str
    user_input: Optional[str] = None
    creation_date: datetime
    llm_response: Optional[str] = None
    input_tokens: Optional[str] = None
    output_tokens: Optional[str] = None
    total_tokens: Optional[str] = None
    latency_ms: Optional[str] = None
    prompt_tokens: Optional[str] = None
    user_input_tokens: Optional[str] = None
    image: Any

    class Config:
        from_attributes = True

