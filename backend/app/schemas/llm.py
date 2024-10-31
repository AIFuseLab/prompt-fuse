from pydantic import BaseModel
from typing import Optional, Any
import uuid


class LLMCreate(BaseModel):
    name: str
    description: Optional[str] = None
    access_key: Optional[str] = None
    secret_access_key: Optional[str] = None
    llm_model_id: Optional[str] = None
    aws_region: Optional[str] = None


class LLMUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    access_key: Optional[str] = None
    secret_access_key: Optional[str] = None
    llm_model_id: Optional[str] = None
    aws_region: Optional[str] = None


class LLMResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    llm_model_id: Optional[str]

    class Config:
        from_attributes = True


class ConversationInput(BaseModel):
    llm_id: uuid.UUID
    user_input: str
    prompt: str
    max_tokens: Optional[int] = 2000
    temperature: Optional[float] = 0.9
    top_p: Optional[float] = 0.1


class ImageConversationInput(BaseModel):
    llm_id: uuid.UUID
    image: Any
    prompt: str
    max_tokens: Optional[int] = 2000
    temperature: Optional[float] = 0.9
    top_p: Optional[float] = 0.1