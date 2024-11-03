from sqlalchemy import Column, String, Text, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..db.database import Base
import uuid
from datetime import datetime
from ..utils.exceptions.errors import get_error_message
from .test import test_prompt_association
from fastapi import HTTPException

class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    prompt = Column(Text)
    notes = Column(Text)
    creation_date = Column(DateTime, default=datetime.utcnow)
    version = Column(Numeric(3, 1), default=0.0)
    llm_id = Column(UUID(as_uuid=True), ForeignKey('llm.id'))
    prompt_template_id = Column(UUID(as_uuid=True), ForeignKey('prompt_template.id'))

    llm = relationship("LLM", back_populates="prompts")
    prompt_template = relationship("PromptTemplate", back_populates="prompts")
    tests = relationship("Test", secondary=test_prompt_association, back_populates="prompts")

class PromptException(HTTPException):
    def __init__(self, status_code: int, error_key: str, detail: str = None):
        error_message = get_error_message(error_key)
        content = {
            "error_key": error_key,
            "message": error_message
        }
        if detail is not None:
            content["detail"] = detail
        super().__init__(status_code=status_code, detail=content)

