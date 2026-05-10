from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.incident import (
    IncidentCreate,
    IncidentUpdate,
    SeverityUpdate,
    IncidentResponse
)
from app.services.incident import IncidentService
from app.core.database import get_db
from app.websocket import connection_manager

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.post("/", response_model=IncidentResponse, status_code=201)
async def create_incident(
    incident_data: IncidentCreate,
    db: Session = Depends(get_db)
) -> dict:
    """
    Create a new incident
    
    - **title**: Incident title (required)
    - **severity**: Incident severity level (required)
    - **service**: Service affected (required)
    - **description**: Detailed description (optional)
    """
    incident = IncidentService.create_incident(db, incident_data)
    await connection_manager.broadcast({
        "type": "incident_created",
        "payload": incident,
    })
    return incident


@router.get("/", response_model=List[IncidentResponse])
async def get_incidents(
    status: Optional[str] = Query(None, description="Filter by status (open, resolved, closed)"),
    db: Session = Depends(get_db)
) -> List[dict]:
    """
    Get all incidents, optionally filtered by status
    
    - **status**: Filter by status (open, resolved, closed) - optional
    """
    incidents = IncidentService.get_all_incidents(db, status=status)
    return incidents


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """
    Get a specific incident by ID
    
    - **incident_id**: The incident ID
    """
    incident = IncidentService.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    return incident


@router.put("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: int,
    incident_data: IncidentUpdate,
    db: Session = Depends(get_db)
) -> dict:
    """
    Update an incident
    
    - **incident_id**: The incident ID
    - **title**: New title (optional)
    - **severity**: New severity level (optional)
    - **description**: New description (optional)
    """
    incident = IncidentService.update_incident(db, incident_id, incident_data)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    return incident


@router.patch("/{incident_id}/severity", response_model=IncidentResponse)
async def update_incident_severity(
    incident_id: int,
    severity_data: SeverityUpdate,
    db: Session = Depends(get_db)
) -> dict:
    """
    Update incident severity
    
    - **incident_id**: The incident ID
    - **severity**: New severity level
    """
    incident = IncidentService.update_severity(db, incident_id, severity_data.severity)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    return incident


@router.patch("/{incident_id}/resolve", response_model=IncidentResponse)
async def resolve_incident(
    incident_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """
    Resolve an incident (mark as resolved)
    
    - **incident_id**: The incident ID
    """
    incident = IncidentService.resolve_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    return incident


@router.patch("/{incident_id}/close", response_model=IncidentResponse)
async def close_incident(
    incident_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """
    Close an incident
    
    - **incident_id**: The incident ID
    """
    incident = IncidentService.close_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    return incident


@router.delete("/{incident_id}", status_code=204)
async def delete_incident(
    incident_id: int,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete an incident
    
    - **incident_id**: The incident ID
    """
    success = IncidentService.delete_incident(db, incident_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
