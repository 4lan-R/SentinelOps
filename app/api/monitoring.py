"""
Monitoring API endpoints

Provides endpoints for:
- Getting current metrics
- Starting/stopping monitoring
- Viewing monitoring status
"""

from fastapi import APIRouter
from app.services.monitoring import MonitoringSimulator

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/metrics")
async def get_metrics():
    """
    Get current infrastructure metrics.

    Returns:
    - **cpu_usage**: CPU usage percentage (0-100)
    - **memory_usage**: Memory usage percentage (0-100)
    - **api_error_rate**: API error rate (0.0-1.0)
    - **db_latency_ms**: Database latency in milliseconds
    """
    metrics = MonitoringSimulator.get_metrics()
    return {
        "status": "healthy",
        "metrics": metrics,
        "thresholds": {
            "cpu_threshold": MonitoringSimulator.CPU_THRESHOLD,
            "memory_threshold": MonitoringSimulator.MEMORY_THRESHOLD,
            "api_error_rate_threshold": MonitoringSimulator.API_ERROR_RATE_THRESHOLD,
            "db_latency_threshold_ms": MonitoringSimulator.DB_LATENCY_THRESHOLD
        }
    }


@router.get("/health")
async def monitoring_health():
    """Get monitoring system health status"""
    return {
        "status": "operational",
        "services_monitored": MonitoringSimulator.SERVICES,
        "check_interval_seconds": 5
    }
