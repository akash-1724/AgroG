import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

# Schema for creating an article (resource)
class ArticleCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=255)
    slug: str = Field(..., min_length=3, max_length=255)
    summary: str = Field("", max_length=1000)
    content: str = Field(..., min_length=20, description="Markdown content of the article")
    category: str = Field(..., min_length=2, max_length=100)
    tags: List[str] = Field(default_factory=list)
    crop_tags: List[str] = Field(default_factory=list)
    media_url: Optional[str] = Field(None, max_length=500)
    language: str = Field("en", min_length=2, max_length=10)
    status: str = Field("draft", description="draft or published")

# Schema for updating an article (resource)
class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=255)
    slug: Optional[str] = Field(None, min_length=3, max_length=255)
    summary: Optional[str] = Field(None, max_length=1000)
    content: Optional[str] = Field(None, min_length=20)
    category: Optional[str] = Field(None, min_length=2, max_length=100)
    tags: Optional[List[str]] = None
    crop_tags: Optional[List[str]] = None
    media_url: Optional[str] = Field(None, max_length=500)
    language: Optional[str] = Field(None, min_length=2, max_length=10)
    status: Optional[str] = Field(None, description="draft or published")

# Schema for article response
class ArticleResponse(BaseModel):
    id: uuid.UUID
    author_id: uuid.UUID
    title: str
    slug: str
    summary: str
    content: str
    category: str
    tags: List[str]
    crop_tags: List[str]
    media_url: Optional[str]
    language: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
