"""
Metric model for analytics.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from app.core.database import Base


class Metric(Base):
    """
    Metric model for tracking user events.
    
    Attributes:
        id: Primary key
        user_id: User who triggered the event (optional)
        event_type: Type of event (download, page_view)
        metadata: JSON data with event details
        timestamp: Event timestamp
    """
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    event_type = Column(String(50), nullable=False, index=True)
    payload = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<Metric(id={self.id}, type={self.event_type}, user={self.user_id})>"
