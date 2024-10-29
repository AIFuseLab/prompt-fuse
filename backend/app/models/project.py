from sqlalchemy import Column, String, DateTime, Text, Integer
from sqlalchemy import func
from ..db.database import Base
import uuid
from fastapi import HTTPException
from ..exceptions.error_messages import ErrorMessages
from sqlalchemy.orm import relationship

class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=uuid.uuid4())
    name = Column(String(255), unique=True, nullable=False, index=True)
    creation_date = Column(DateTime, default=func.now())
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())
    description = Column(Text)
    
    prompt_templates = relationship("PromptTemplate", back_populates="project")
    # llm_tools = relationship("LLMTool", back_populates="project")

class ProjectException(HTTPException):
    def __init__(self, status_code: int, error_key: str, detail: str = None):
        detail = getattr(ErrorMessages, error_key, ErrorMessages.UNEXPECTED_ERROR)
        if detail is not None:
            detail = f"{detail}: {detail}"
        super().__init__(status_code=status_code, detail=detail)
