"""
Pydantic schemas for metrics.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel


class MetricCreate(BaseModel):
    """Schema for creating a metric event."""
    event_type: str
    payload: Optional[Dict[str, Any]] = None


class MetricResponse(BaseModel):
    """Schema for metric response."""
    id: int
    user_id: Optional[int]
    event_type: str
    payload: Optional[Dict[str, Any]]
    timestamp: datetime
    
    class Config:
        from_attributes = True


class MetricSummary(BaseModel):
    """Schema for aggregated metric data."""
    event_type: str
    count: int
    details: Optional[Dict[str, Any]] = None


class MetricTimeSeries(BaseModel):
    """Schema for time-series metric data."""
    date: str
    event_type: str
    count: int


class MetricTrend(BaseModel):
    """Schema for metric with trend comparison."""
    event_type: str
    current_count: int
    previous_count: int
    change_percent: float
