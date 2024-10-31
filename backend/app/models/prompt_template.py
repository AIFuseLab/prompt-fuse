from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..db.database import Base
import uuid
from datetime import datetime

class PromptTemplate(Base):
    __tablename__ = "prompt_template"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    creation_date = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    number_of_prompts = Column(Integer, default=0)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'))

    project = relationship("Project", back_populates="prompt_templates")
    prompts = relationship("Prompt", back_populates="prompt_template")

class PromptTemplateException(Exception):
    def __init__(self, status_code: int, error_key: str, detail: str = None):
        self.status_code = status_code
        self.error_key = error_key
        self.detail = detail

