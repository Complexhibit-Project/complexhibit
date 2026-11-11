"""
Example Query model for storing user-contributed SPARQL queries.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class ExampleQuery(Base):
    """
    Example SPARQL query model for the example queries feature.
    
    Allows authenticated users to save and share their SPARQL queries.
    
    Attributes:
        id: Primary key
        name: Query display name (e.g., "Exhibitions by Decade")
        description: Brief description of what the query does
        query: The SPARQL query text
        category: Query category for grouping
        user_id: FK to the user who created this query
        is_approved: Whether the query is visible to all users
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "example_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(String(500), nullable=True)
    query = Column(Text, nullable=False)
    category = Column(String(50), default="custom", nullable=False)
    
    # Foreign key to users table
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Approval status (auto-approve for now, can add moderation later)
    is_approved = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship to user
    user = relationship("User", backref="example_queries")
    
    def __repr__(self):
        return f"<ExampleQuery(id={self.id}, name={self.name}, user_id={self.user_id})>"
