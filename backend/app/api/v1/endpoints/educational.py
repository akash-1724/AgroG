import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, or_, func

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_user_optional, RoleChecker
from app.models.user import User
from app.models.educational import EducationalArticle
from app.schemas.educational import ArticleCreate, ArticleUpdate, ArticleResponse

router = APIRouter()

# Admin guard for write operations
admin_guard = RoleChecker(allowed_roles=["admin"])

@router.get("/", response_model=List[ArticleResponse])
async def read_articles(
    category: Optional[str] = Query(None, description="Filter by category"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    crop_tag: Optional[str] = Query(None, description="Filter by crop tag"),
    language: Optional[str] = Query(None, description="Filter by language"),
    search: Optional[str] = Query(None, description="Search in title or content"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve educational articles (public access, draft visible only to admin)."""
    query = select(EducationalArticle)
    
    # Hide drafts from non-admins
    if not current_user or current_user.role != "admin":
        query = query.where(EducationalArticle.status == "published")
        
    if category:
        query = query.where(EducationalArticle.category == category)
        
    if language:
        query = query.where(EducationalArticle.language == language)
        
    if tag:
        # PostgreSQL JSONB array check or SQLite simple check
        # We can use func.json_each (SQLite) or cast, but a clean way is:
        # query = query.where(EducationalArticle.tags.contains(tag))
        # Let's write a database-agnostic check or fallback to simple JSON contains:
        query = query.where(EducationalArticle.tags.contains([tag]))

    if crop_tag:
        query = query.where(EducationalArticle.crop_tags.contains([crop_tag]))

    if search:
        search_expr = f"%{search}%"
        query = query.where(
            or_(
                EducationalArticle.title.ilike(search_expr),
                EducationalArticle.content.ilike(search_expr),
                EducationalArticle.summary.ilike(search_expr)
            )
        )
        
    query = query.offset(offset).limit(limit).order_by(EducationalArticle.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_article(
    payload: ArticleCreate,
    current_user: User = Depends(admin_guard),
    db: AsyncSession = Depends(get_db)
):
    """Publish a new educational article (Admin only)."""
    # Check if slug is unique
    existing_slug = await db.execute(
        select(EducationalArticle).where(EducationalArticle.slug == payload.slug)
    )
    if existing_slug.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An educational article with this slug already exists."
        )

    new_article = EducationalArticle(
        author_id=current_user.id,
        title=payload.title,
        slug=payload.slug,
        summary=payload.summary,
        content=payload.content,
        category=payload.category,
        tags=payload.tags,
        crop_tags=payload.crop_tags,
        media_url=payload.media_url,
        language=payload.language,
        status=payload.status
    )
    db.add(new_article)
    await db.commit()
    await db.refresh(new_article)
    return new_article

@router.get("/{id_or_slug}", response_model=ArticleResponse)
async def read_article(
    id_or_slug: str, 
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve a single educational article by ID or slug."""
    try:
        uuid_val = uuid.UUID(id_or_slug)
        result = await db.execute(select(EducationalArticle).where(EducationalArticle.id == uuid_val))
    except ValueError:
        result = await db.execute(select(EducationalArticle).where(EducationalArticle.slug == id_or_slug))
        
    article = result.scalars().first()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found."
        )
        
    # Hide drafts from non-admins
    if article.status == "draft" and (not current_user or current_user.role != "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to draft resources is restricted to administrators."
        )
        
    return article

@router.patch("/{id}", response_model=ArticleResponse)
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
    
    if "slug" in update_data and update_data["slug"] != article.slug:
        existing_slug = await db.execute(
            select(EducationalArticle).where(EducationalArticle.slug == update_data["slug"])
        )
        if existing_slug.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An educational article with this slug already exists."
            )

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
