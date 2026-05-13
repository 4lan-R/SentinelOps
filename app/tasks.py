"""
Background Tasks

Runs monitoring simulation and other background jobs.
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import SessionLocal
from app.services.monitoring import MonitoringSimulator


class BackgroundTaskManager:
    """Manages background tasks"""

    def __init__(self):
        self.monitoring_task = None
        self.is_running = False

    async def start_monitoring(self):
        """Start the monitoring simulator"""
        self.is_running = True
        while self.is_running:
            try:
                db = SessionLocal()
                try:
                    # Check all monitoring metrics every 5 seconds
                    MonitoringSimulator.check_cpu_spike(db)
                    MonitoringSimulator.check_memory_leak(db)
                    MonitoringSimulator.check_api_failure(db)
                    MonitoringSimulator.check_db_latency(db)
                finally:
                    db.close()

                # Wait before next check
                await asyncio.sleep(5)
            except Exception as e:
                print(f"Error in monitoring task: {e}")
                await asyncio.sleep(5)

    async def stop_monitoring(self):
        """Stop the monitoring simulator"""
        self.is_running = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass


# Global task manager instance
background_manager = BackgroundTaskManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager.
    Starts background tasks on startup, stops on shutdown.
    """
    # Startup: start monitoring
    background_manager.monitoring_task = asyncio.create_task(
        background_manager.start_monitoring()
    )
    print("✓ Monitoring simulator started")

    yield

    # Shutdown: stop monitoring
    await background_manager.stop_monitoring()
    print("✓ Monitoring simulator stopped")
