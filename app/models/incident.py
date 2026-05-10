from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from app.core.database import Base
import enum


class IncidentStatus(str, enum.Enum):
    """Incident status enumeration"""
    open = "open"
    resolved = "resolved"
    closed = "closed"


class IncidentSeverity(str, enum.Enum):
    """Incident severity enumeration"""
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Incident(Base):
    """Incident model using SQLAlchemy ORM"""
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(String(2000), nullable=True)
    severity = Column(String(50), nullable=False, index=True)
    service = Column(String(255), nullable=False, index=True)
    status = Column(String(50), nullable=False, index=True, default="open")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        """Convert incident to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "service": self.service,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self) -> str:
        return f"<Incident(id={self.id}, title={self.title}, severity={self.severity}, status={self.status})>"

