from typing import List, Optional
from pydantic import BaseModel, Field


class Topic(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    post_count: int = 0
    participant_count: int = 0
    tags: List[str] = Field(default_factory=list)
    last_activity: Optional[str] = None
