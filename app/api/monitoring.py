"""
Monitoring API endpoints

Provides endpoints for:
- Getting current metrics
- Starting/stopping monitoring
- Viewing monitoring status
"""

import asyncio
from fastapi import APIRouter
from app.services.monitoring import MonitoringSimulator
from app.tasks import background_manager

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


@router.get("/status")
async def monitoring_status():
    """Get whether the monitoring simulator is currently running."""
    task_active = bool(
        background_manager.monitoring_task
        and not background_manager.monitoring_task.done()
    )
    return {
        "running": background_manager.is_running and task_active,
        "task_active": task_active,
        "check_interval_seconds": 5
    }


@router.post("/start")
async def start_monitoring():
    """Start the monitoring simulator if it is not already running."""
    task_active = bool(
        background_manager.monitoring_task
        and not background_manager.monitoring_task.done()
    )
    if background_manager.is_running and task_active:
        return {
            "status": "running",
            "message": "Monitoring simulator is already running.",
            "running": True
        }

    background_manager.monitoring_task = asyncio.create_task(
        background_manager.start_monitoring()
    )
    return {
        "status": "started",
        "message": "Monitoring simulator has been started.",
        "running": True
    }


@router.post("/stop")
async def stop_monitoring():
    """Stop the monitoring simulator."""
    if not background_manager.is_running:
        return {
            "status": "stopped",
            "message": "Monitoring simulator is already stopped.",
            "running": False
        }

    await background_manager.stop_monitoring()
    return {
        "status": "stopped",
        "message": "Monitoring simulator has been stopped.",
        "running": False
    }
