from pydantic import BaseModel
from datetime import datetime
from typing import Optional
class ProjectCreate(BaseModel):
    name: str
    description: str


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str
    creation_date: datetime
    last_updated: datetime

    class Config:
        from_attributes = True