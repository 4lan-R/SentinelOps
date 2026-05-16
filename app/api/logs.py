from datetime import datetime
from typing import List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.schemas.log import LogCreate, LogResponse
from app.services.log import LogService
from app.core.database import get_db

router = APIRouter(prefix="/logs", tags=["logs"])


@router.post("/", response_model=List[LogResponse], status_code=201)
async def ingest_logs(
    log_data: Union[LogCreate, List[LogCreate]],
    db: Session = Depends(get_db)
) -> List[dict]:
    """Ingest one or more log entries."""
    if isinstance(log_data, LogCreate):
        logs = [log_data]
    else:
        logs = log_data
    if not logs:
        raise HTTPException(status_code=400, detail="No log entries provided.")
    created_logs = LogService.create_logs(db, logs)
    return created_logs


@router.get("/", response_model=List[LogResponse])
async def search_logs(
    query: Optional[str] = Query(None, description="Text query to search log message or raw content"),
    service: Optional[str] = Query(None, description="Filter logs by service name"),
    incident_id: Optional[int] = Query(None, description="Filter logs linked to an incident"),
    start_time: Optional[datetime] = Query(None, description="Filter logs created after this timestamp"),
    end_time: Optional[datetime] = Query(None, description="Filter logs created before this timestamp"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> List[dict]:
    """Search stored logs with optional filters."""
    logs = LogService.get_logs(
        db,
        query=query,
        service=service,
        incident_id=incident_id,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        offset=offset,
    )
    return logs
