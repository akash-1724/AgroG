import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

# Schema for creating an article
class ArticleCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=255)
    content: str = Field(..., min_length=20, description="Markdown content of the article")
    category: str = Field(..., min_length=2, max_length=100)
    tags: List[str] = Field(default_factory=list)

# Schema for updating an article
class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=255)
    content: Optional[str] = Field(None, min_length=20)
    category: Optional[str] = Field(None, min_length=2, max_length=100)
    tags: Optional[List[str]] = None

# Schema for article response
class ArticleResponse(BaseModel):
    id: uuid.UUID
    author_id: uuid.UUID
    title: str
    content: str
    category: str
    tags: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
