from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class LogEntry(Base):
    """Log entry model for stored logs."""
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True, index=True)
    service = Column(String(255), nullable=False, index=True)
    level = Column(String(50), nullable=False, default="INFO", index=True)
    message = Column(String(2000), nullable=False)
    raw_message = Column(String(4000), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    incident = relationship("Incident", back_populates="logs")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "service": self.service,
            "level": self.level,
            "message": self.message,
            "raw_message": self.raw_message,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
