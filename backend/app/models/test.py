from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Table, LargeBinary, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..db.database import Base
import uuid
from datetime import datetime

test_prompt_association = Table('test_prompt_association', Base.metadata,
    Column('test_id', UUID(as_uuid=True), ForeignKey('tests.id')),
    Column('prompt_id', UUID(as_uuid=True), ForeignKey('prompts.id')),
    Column('llm_response', Text),
    Column('input_tokens', Integer),
    Column('output_tokens', Integer),
    Column('total_tokens', Integer),
    Column('latency_ms', Integer),
    Column('prompt_tokens', Integer),
    Column('user_input_tokens', Integer)
)

class Test(Base):
    __tablename__ = "tests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    test_name = Column(String(255), nullable=False)
    user_input = Column(Text, nullable=False)
    image = Column(LargeBinary, nullable=True)
    creation_date = Column(DateTime, default=datetime.utcnow)

    prompts = relationship("Prompt", secondary=test_prompt_association, back_populates="tests")

class TestException(Exception):
    def __init__(self, status_code: int, error_key: str, detail: str = None):
        self.status_code = status_code
        self.error_key = error_key
        self.detail = detail

