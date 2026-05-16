from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel, Field


class LogCreate(BaseModel):
    """Schema for ingesting a log entry."""
    service: str = Field(..., min_length=1, max_length=255)
    level: Optional[str] = Field("INFO", description="Log severity level")
    message: str = Field(..., min_length=1, max_length=2000)
    raw_message: Optional[str] = Field(None, description="Raw log text or details")
    incident_id: Optional[int] = Field(None, description="Optional linked incident ID")
    timestamp: Optional[datetime] = Field(None, description="Log timestamp")


class LogResponse(BaseModel):
    """Schema for returning stored log entries."""
    id: int
    incident_id: Optional[int]
    service: str
    level: str
    message: str
    raw_message: Optional[str]
    timestamp: datetime
    created_at: datetime

    class Config:
        orm_mode = True


class LogBatchCreate(BaseModel):
    """Schema for ingesting multiple log entries."""
    logs: List[LogCreate]
