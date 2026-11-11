"""
API Router for Example SPARQL Queries.

Provides endpoints for listing, creating, and deleting user-contributed queries.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_token
from app.models.example_query import ExampleQuery
from app.models.user import User, UserStatus, UserRole


router = APIRouter(prefix=f"{settings.DEPLOY_PATH}/example-queries", tags=["example-queries"])
security = HTTPBearer(auto_error=False)


# Pydantic schemas
class ExampleQueryCreate(BaseModel):
    """Schema for creating a new example query."""
    name: str = Field(..., min_length=3, max_length=100, description="Query display name")
    description: Optional[str] = Field(None, max_length=500, description="Query description")
    query: str = Field(..., min_length=10, description="SPARQL query text")
    category: str = Field(default="custom", max_length=50, description="Query category")


class ExampleQueryResponse(BaseModel):
    """Schema for example query responses."""
    id: int
    name: str
    description: Optional[str]
    query: str
    category: str
    user_id: int
    username: str
    created_at: str
    
    class Config:
        from_attributes = True


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials],
    db: Session
) -> Optional[User]:
    """Extract and validate the current user from JWT token."""
    if not credentials:
        return None
    
    payload = decode_token(credentials.credentials)
    if not payload:
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or user.status != UserStatus.ACTIVE:
        return None
    
    return user


@router.get("", response_model=List[ExampleQueryResponse])
async def list_example_queries(
    db: Session = Depends(get_db),
    category: Optional[str] = None
):
    """
    List all approved example queries.
    
    Public endpoint - no authentication required.
    Optionally filter by category.
    """
    query = db.query(ExampleQuery, User.username).join(
        User, ExampleQuery.user_id == User.id
    ).filter(ExampleQuery.is_approved == True)
    
    if category:
        query = query.filter(ExampleQuery.category == category)
    
    results = query.order_by(ExampleQuery.created_at.desc()).all()
    
    return [
        ExampleQueryResponse(
            id=eq.id,
            name=eq.name,
            description=eq.description,
            query=eq.query,
            category=eq.category,
            user_id=eq.user_id,
            username=username,
            created_at=eq.created_at.isoformat()
        )
        for eq, username in results
    ]


@router.post("", response_model=ExampleQueryResponse, status_code=status.HTTP_201_CREATED)
async def create_example_query(
    query_data: ExampleQueryCreate,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Create a new example query.
    
    Requires authentication. Only active users can create queries.
    """
    user = get_current_user(credentials, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to save example queries"
        )
    
    # Check for duplicate name by same user
    existing = db.query(ExampleQuery).filter(
        ExampleQuery.name == query_data.name,
        ExampleQuery.user_id == user.id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a query with this name"
        )
    
    # Create the query
    new_query = ExampleQuery(
        name=query_data.name,
        description=query_data.description,
        query=query_data.query,
        category=query_data.category,
        user_id=user.id,
        is_approved=True  # Auto-approve for now
    )
    
    db.add(new_query)
    db.commit()
    db.refresh(new_query)
    
    return ExampleQueryResponse(
        id=new_query.id,
        name=new_query.name,
        description=new_query.description,
        query=new_query.query,
        category=new_query.category,
        user_id=new_query.user_id,
        username=user.username,
        created_at=new_query.created_at.isoformat()
    )


@router.delete("/{query_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_example_query(
    query_id: int,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Delete an example query.
    
    Requires authentication. Users can only delete their own queries.
    Admins can delete any query.
    """
    user = get_current_user(credentials, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    example_query = db.query(ExampleQuery).filter(ExampleQuery.id == query_id).first()
    
    if not example_query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found"
        )
    
    # Check ownership or admin role
    if example_query.user_id != user.id and user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own queries"
        )
    
    db.delete(example_query)
    db.commit()
    
    return None
