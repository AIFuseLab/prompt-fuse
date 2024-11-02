from sqlalchemy import Column, String, DateTime, Text, Integer
from sqlalchemy import func
from ..db.database import Base
import uuid
from fastapi import HTTPException
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from ..utils.exceptions.errors import get_error_message

class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False, index=True)
    creation_date = Column(DateTime, default=func.now())
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())
    description = Column(Text)
    
    prompt_templates = relationship("PromptTemplate", back_populates="project")
    # llm_tools = relationship("LLMTool", back_populates="project")

class ProjectException(HTTPException):
    def __init__(self, status_code: int, error_key: str, detail: str = None):
        error_message = get_error_message(error_key)
        content = {
            "error_key": error_key,
            "message": error_message
        }
        if detail is not None:
            content["detail"] = detail
        super().__init__(status_code=status_code, detail=content)
