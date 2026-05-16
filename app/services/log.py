import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from app.models.incident import Incident
from app.models.log import LogEntry
from app.schemas.log import LogCreate


class LogService:
    """Service layer for log ingestion, search, and correlation."""

    @staticmethod
    def create_log(db: Session, log_data: LogCreate) -> dict:
        """Persist a single log entry."""
        log_entry = LogEntry(
            incident_id=log_data.incident_id,
            service=log_data.service,
            level=log_data.level or "INFO",
            message=log_data.message,
            raw_message=log_data.raw_message,
            timestamp=log_data.timestamp or datetime.utcnow()
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry.to_dict()

    @staticmethod
    def create_logs(db: Session, logs_data: List[LogCreate]) -> List[dict]:
        """Persist a batch of log entries."""
        created_logs = []
        for log_data in logs_data:
            created_logs.append(LogService.create_log(db, log_data))
        return created_logs

    @staticmethod
    def create_logs_from_text(
        db: Session,
        raw_logs: str,
        service: str,
        incident_id: Optional[int] = None,
    ) -> List[dict]:
        """Parse raw log text and persist entries for a service."""
        parsed = LogService._parse_log_text(raw_logs, service, incident_id)
        return LogService.create_logs(db, parsed)

    @staticmethod
    def get_logs(
        db: Session,
        query: Optional[str] = None,
        service: Optional[str] = None,
        incident_id: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[dict]:
        """Search logs by text, service, incident linkage, and time range."""
        q = db.query(LogEntry)
        if service:
            q = q.filter(LogEntry.service == service)
        if incident_id is not None:
            q = q.filter(LogEntry.incident_id == incident_id)
        if start_time:
            q = q.filter(LogEntry.timestamp >= start_time)
        if end_time:
            q = q.filter(LogEntry.timestamp <= end_time)
        if query:
            search = f"%{query}%"
            q = q.filter(
                LogEntry.message.ilike(search)
                | LogEntry.raw_message.ilike(search)
            )
        q = q.order_by(LogEntry.timestamp.desc())
        logs = q.offset(offset).limit(min(limit, 500)).all()
        return [log.to_dict() for log in logs]

    @staticmethod
    def get_logs_for_incident(
        db: Session,
        incident_id: int,
        query: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[dict]:
        """Return logs linked to an incident or correlated by service/time."""
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            return []

        window_start = incident.created_at - timedelta(minutes=10)
        window_end = incident.created_at + timedelta(minutes=10)
        q = db.query(LogEntry).filter(
            or_(
                LogEntry.incident_id == incident_id,
                and_(
                    LogEntry.service == incident.service,
                    LogEntry.timestamp >= window_start,
                    LogEntry.timestamp <= window_end,
                ),
            )
        )
        if query:
            search = f"%{query}%"
            q = q.filter(
                LogEntry.message.ilike(search)
                | LogEntry.raw_message.ilike(search)
            )
        q = q.order_by(LogEntry.timestamp.desc())
        logs = q.offset(offset).limit(min(limit, 500)).all()
        return [log.to_dict() for log in logs]

    @staticmethod
    def _parse_log_text(
        raw_logs: str,
        service: str,
        incident_id: Optional[int] = None,
    ) -> List[LogCreate]:
        """Parse raw log lines into LogCreate items."""
        entries: List[LogCreate] = []
        if not raw_logs:
            return entries

        line_pattern = re.compile(
            r"^\[(?P<datetime>[^\]]+)\]\s+(?P<level>INFO|WARN|ERROR|DEBUG|TRACE|FATAL)\s+(?P<service>[\w\-]+):\s+(?P<message>.*)$",
            re.IGNORECASE,
        )

        for line in raw_logs.splitlines():
            line = line.strip()
            if not line:
                continue
            match = line_pattern.match(line)
            if match:
                timestamp_text = match.group("datetime")
                try:
                    timestamp = datetime.fromisoformat(timestamp_text)
                except ValueError:
                    timestamp = datetime.utcnow()
                entries.append(LogCreate(
                    incident_id=incident_id,
                    service=service,
                    level=match.group("level").upper(),
                    message=match.group("message").strip(),
                    raw_message=line,
                    timestamp=timestamp,
                ))
            else:
                entries.append(LogCreate(
                    incident_id=incident_id,
                    service=service,
                    level="INFO",
                    message=line,
                    raw_message=line,
                    timestamp=datetime.utcnow(),
                ))

        return entries
