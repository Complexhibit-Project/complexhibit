"""
Metrics router.

Handles recording and retrieving analytics data.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from enum import Enum
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
import csv
import io

from app.core.config import settings
from app.core.database import get_db
from app.dependencies import get_current_user_optional, require_admin
from app.models.metric import Metric
from app.models.user import User
from app.schemas.metric import MetricCreate, MetricResponse, MetricSummary, MetricTimeSeries, MetricTrend

router = APIRouter(prefix=f"{settings.DEPLOY_PATH}/metrics", tags=["metrics"])


class TimeRange(str, Enum):
    today = "today"
    week = "week"
    month = "month"
    year = "year"
    all = "all"


def get_date_range(time_range: TimeRange) -> tuple[datetime, datetime]:
    """Get start and end dates for the given time range."""
    now = datetime.utcnow()
    end = now
    
    if time_range == TimeRange.today:
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif time_range == TimeRange.week:
        start = now - timedelta(days=7)
    elif time_range == TimeRange.month:
        start = now - timedelta(days=30)
    elif time_range == TimeRange.year:
        start = now - timedelta(days=365)
    else:  # all
        start = datetime(2000, 1, 1)
    
    return start, end


@router.post("/", response_model=MetricResponse, status_code=status.HTTP_201_CREATED)
async def create_metric(
    metric_data: MetricCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_optional)
):
    """
    Record a new metric event.
    """
    metric = Metric(
        user_id=user.id if user else None,
        event_type=metric_data.event_type,
        payload=metric_data.payload
    )
    
    db.add(metric)
    db.commit()
    db.refresh(metric)
    
    return metric


@router.get("/summary", response_model=List[MetricSummary])
async def get_metrics_summary(
    time_range: TimeRange = Query(TimeRange.all, description="Time range filter"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Get aggregated metrics (admin only).
    """
    start, end = get_date_range(time_range)
    
    # Count by event type within date range
    results = db.query(
        Metric.event_type, 
        func.count(Metric.id)
    ).filter(
        Metric.timestamp >= start,
        Metric.timestamp <= end
    ).group_by(Metric.event_type).all()
    
    summary = []
    for event_type, count in results:
        summary.append(MetricSummary(event_type=event_type, count=count))
        
    return summary


@router.get("/trends", response_model=List[MetricTrend])
async def get_metrics_trends(
    time_range: TimeRange = Query(TimeRange.week, description="Time range for current period"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Get metrics with trend comparison to previous period (admin only).
    """
    current_start, current_end = get_date_range(time_range)
    
    # Calculate previous period with same duration
    duration = current_end - current_start
    previous_start = current_start - duration
    previous_end = current_start
    
    # Current period counts
    current_results = db.query(
        Metric.event_type, 
        func.count(Metric.id)
    ).filter(
        Metric.timestamp >= current_start,
        Metric.timestamp <= current_end
    ).group_by(Metric.event_type).all()
    
    current_counts = {event_type: count for event_type, count in current_results}
    
    # Previous period counts
    previous_results = db.query(
        Metric.event_type, 
        func.count(Metric.id)
    ).filter(
        Metric.timestamp >= previous_start,
        Metric.timestamp < previous_end
    ).group_by(Metric.event_type).all()
    
    previous_counts = {event_type: count for event_type, count in previous_results}
    
    # Combine and calculate trends
    all_types = set(current_counts.keys()) | set(previous_counts.keys())
    trends = []
    
    for event_type in all_types:
        current = current_counts.get(event_type, 0)
        previous = previous_counts.get(event_type, 0)
        
        if previous > 0:
            change = ((current - previous) / previous) * 100
        elif current > 0:
            change = 100.0
        else:
            change = 0.0
            
        trends.append(MetricTrend(
            event_type=event_type,
            current_count=current,
            previous_count=previous,
            change_percent=round(change, 1)
        ))
    
    return sorted(trends, key=lambda x: x.current_count, reverse=True)


@router.get("/timeseries", response_model=List[MetricTimeSeries])
async def get_metrics_timeseries(
    time_range: TimeRange = Query(TimeRange.month, description="Time range filter"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Get time-series metrics data grouped by day (admin only).
    """
    start, end = get_date_range(time_range)
    
    query = db.query(
        cast(Metric.timestamp, Date).label('date'),
        Metric.event_type,
        func.count(Metric.id).label('count')
    ).filter(
        Metric.timestamp >= start,
        Metric.timestamp <= end
    )
    
    if event_type:
        query = query.filter(Metric.event_type == event_type)
    
    results = query.group_by(
        cast(Metric.timestamp, Date),
        Metric.event_type
    ).order_by(cast(Metric.timestamp, Date)).all()
    
    return [
        MetricTimeSeries(
            date=str(row.date),
            event_type=row.event_type,
            count=row.count
        ) for row in results
    ]


@router.get("/recent", response_model=List[MetricResponse])
async def get_recent_metrics(
    limit: int = 50,
    time_range: TimeRange = Query(TimeRange.all, description="Time range filter"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Get recent metrics (admin only).
    """
    start, end = get_date_range(time_range)
    
    return db.query(Metric).filter(
        Metric.timestamp >= start,
        Metric.timestamp <= end
    ).order_by(Metric.timestamp.desc()).limit(limit).all()


@router.get("/export")
async def export_metrics(
    time_range: TimeRange = Query(TimeRange.all, description="Time range filter"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Export metrics as CSV (admin only).
    """
    start, end = get_date_range(time_range)
    
    metrics = db.query(Metric).filter(
        Metric.timestamp >= start,
        Metric.timestamp <= end
    ).order_by(Metric.timestamp.desc()).all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['ID', 'Timestamp', 'Event Type', 'User ID', 'Payload'])
    
    # Data rows
    for m in metrics:
        writer.writerow([
            m.id,
            m.timestamp.isoformat(),
            m.event_type,
            m.user_id or '',
            str(m.payload) if m.payload else ''
        ])
    
    output.seek(0)
    
    filename = f"metrics_{time_range.value}_{datetime.utcnow().strftime('%Y%m%d')}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
