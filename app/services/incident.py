from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.incident import Incident
from app.schemas.incident import IncidentCreate, IncidentUpdate
from app.services.ai import AIIncidentAnalyzer, AnalysisResult


class IncidentService:
    """Service layer for incident operations"""

    @staticmethod
    def create_incident(db: Session, incident_data: IncidentCreate) -> dict:
        """Create a new incident"""
        incident = Incident(
            title=incident_data.title,
            severity=incident_data.severity,
            service=incident_data.service,
            description=incident_data.description,
            status="open"
        )
        db.add(incident)
        db.commit()
        db.refresh(incident)
        return incident.to_dict()

    @staticmethod
    def analyze_incident(logs: str, metrics: dict) -> AnalysisResult:
        """Analyze incident using AI to provide insights"""
        analyzer = AIIncidentAnalyzer()
        return analyzer.analyze_incident(logs, metrics)

    @staticmethod
    def get_incident(db: Session, incident_id: int) -> Optional[dict]:
        """Get a specific incident by ID"""
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        return incident.to_dict() if incident else None

    @staticmethod
    def get_all_incidents(db: Session, status: Optional[str] = None) -> List[dict]:
        """Get all incidents, optionally filtered by status"""
        query = db.query(Incident)
        if status:
            query = query.filter(Incident.status == status)
        incidents = query.all()
        return [incident.to_dict() for incident in incidents]

    @staticmethod
    def update_incident(db: Session, incident_id: int, incident_data: IncidentUpdate) -> Optional[dict]:
        """Update an incident"""
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            return None

        if incident_data.title is not None:
            incident.title = incident_data.title
        if incident_data.severity is not None:
            incident.severity = incident_data.severity
        if incident_data.description is not None:
            incident.description = incident_data.description

        db.commit()
        db.refresh(incident)
        return incident.to_dict()

    @staticmethod
    def update_severity(db: Session, incident_id: int, new_severity: str) -> Optional[dict]:
        """Update incident severity"""
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            return None
        incident.severity = new_severity
        db.commit()
        db.refresh(incident)
        return incident.to_dict()

    @staticmethod
    def resolve_incident(db: Session, incident_id: int) -> Optional[dict]:
        """Resolve an incident (mark as resolved)"""
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            return None
        incident.status = "resolved"
        db.commit()
        db.refresh(incident)
        return incident.to_dict()

    @staticmethod
    def close_incident(db: Session, incident_id: int) -> Optional[dict]:
        """Close an incident"""
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            return None
        incident.status = "closed"
        db.commit()
        db.refresh(incident)
        return incident.to_dict()

    @staticmethod
    def delete_incident(db: Session, incident_id: int) -> bool:
        """Delete an incident"""
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            return False
        db.delete(incident)
        db.commit()
        return True
