from sqlalchemy import Column, String, Text, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..db.database import Base
import uuid

class LLM(Base):
    __tablename__ = "llm"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    access_key = Column(String(255))
    secret_access_key = Column(String(255))
    llm_model_id = Column(String(255))
    aws_region = Column(String(100))
    prompts = relationship("Prompt", back_populates="llm")

class LLMException(Exception):
    def __init__(self, status_code: int, error_key: str, detail: str = None):
        self.status_code = status_code
        self.error_key = error_key
        self.detail = detail