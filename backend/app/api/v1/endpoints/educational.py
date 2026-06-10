import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core.database import get_db
from app.api.deps import get_current_user, RoleChecker
from app.models.user import User
from app.models.educational import EducationalArticle
from app.schemas.educational import ArticleCreate, ArticleUpdate, ArticleResponse

router = APIRouter()

# Admin guard for write operations
admin_guard = RoleChecker(allowed_roles=["admin"])

@router.get("/", response_model=List[ArticleResponse])
async def read_articles(
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve educational articles (public access)."""
    query = select(EducationalArticle)
    if category:
        query = query.where(EducationalArticle.category == category)
        
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_article(
    payload: ArticleCreate,
    current_user: User = Depends(admin_guard),
    db: AsyncSession = Depends(get_db)
):
    """Publish a new educational article (Admin only)."""
    new_article = EducationalArticle(
        author_id=current_user.id,
        title=payload.title,
        content=payload.content,
        category=payload.category,
        tags=payload.tags
    )
    db.add(new_article)
    await db.commit()
    await db.refresh(new_article)
    return new_article

@router.get("/{id}", response_model=ArticleResponse)
async def read_article(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Retrieve a single educational article by ID."""
    result = await db.execute(select(EducationalArticle).where(EducationalArticle.id == id))
    article = result.scalars().first()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found."
        )
    return article

@router.put("/{id}", response_model=ArticleResponse)
async def update_article(
    id: uuid.UUID,
    payload: ArticleUpdate,
    current_user: User = Depends(admin_guard),
    db: AsyncSession = Depends(get_db)
):
    """Update an educational article (Admin only)."""
    result = await db.execute(select(EducationalArticle).where(EducationalArticle.id == id))
    article = result.scalars().first()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found."
        )
        
    update_data = payload.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(article, key, val)
        
    await db.commit()
    await db.refresh(article)
    return article

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    id: uuid.UUID,
    current_user: User = Depends(admin_guard),
    db: AsyncSession = Depends(get_db)
):
    """Delete an educational article (Admin only)."""
    result = await db.execute(select(EducationalArticle).where(EducationalArticle.id == id))
    article = result.scalars().first()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found."
        )
        
    await db.delete(article)
    await db.commit()
    return
