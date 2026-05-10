from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class IncidentCreate(BaseModel):
    """Schema for creating an incident"""
    title: str = Field(..., min_length=1, max_length=255)
    severity: str = Field(..., description="Incident severity level")
    service: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)

    class Config:
        example = {
            "title": "Redis timeout",
            "severity": "critical",
            "service": "payment-service",
            "description": "Payment service unable to connect to Redis"
        }


class IncidentUpdate(BaseModel):
    """Schema for updating an incident"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    severity: Optional[str] = None
    description: Optional[str] = Field(None, max_length=2000)

    class Config:
        example = {
            "title": "Redis timeout - RESOLVED",
            "severity": "high",
            "description": "Issue has been escalated"
        }


class SeverityUpdate(BaseModel):
    """Schema for updating incident severity"""
    severity: str = Field(..., description="New severity level")

    class Config:
        example = {
            "severity": "critical"
        }


class IncidentResponse(BaseModel):
    """Schema for incident response"""
    id: int
    title: str
    severity: str
    service: str
    status: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        example = {
            "id": 1,
            "title": "Redis timeout",
            "severity": "critical",
            "service": "payment-service",
            "status": "open",
            "description": "Payment service unable to connect to Redis",
            "created_at": "2026-05-10T10:30:00",
            "updated_at": "2026-05-10T10:30:00"
        }
