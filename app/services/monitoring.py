"""
Monitoring Simulator Service

Simulates infrastructure monitoring events:
- CPU spikes
- Memory leaks
- API failures
- DB latency
"""

import random
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.schemas.incident import IncidentCreate
from app.services.incident import IncidentService


class MonitoringSimulator:
    """Simulates infrastructure monitoring and creates incidents"""

    # Thresholds for triggering incidents
    CPU_THRESHOLD = 90
    MEMORY_THRESHOLD = 85
    API_ERROR_RATE_THRESHOLD = 0.1  # 10%
    DB_LATENCY_THRESHOLD = 2000  # ms

    # Services being monitored
    SERVICES = [
        "api-server",
        "database",
        "cache-layer",
        "message-queue",
        "auth-service"
    ]

    @staticmethod
    def get_cpu_usage() -> int:
        """
        Simulate CPU usage metric.
        Returns value between 0-100, with occasional spikes above 90.
        """
        base = random.randint(30, 70)
        # 20% chance of spike
        if random.random() < 0.2:
            return random.randint(91, 99)
        return base

    @staticmethod
    def get_memory_usage() -> int:
        """
        Simulate memory usage metric.
        Returns value between 0-100, gradually increasing (memory leak simulation).
        """
        base = random.randint(40, 75)
        # 15% chance of high memory
        if random.random() < 0.15:
            return random.randint(86, 98)
        return base

    @staticmethod
    def get_api_error_rate() -> float:
        """
        Simulate API error rate metric.
        Returns value between 0.0-1.0
        """
        base = random.uniform(0.01, 0.05)
        # 10% chance of high error rate
        if random.random() < 0.1:
            return random.uniform(0.11, 0.25)
        return base

    @staticmethod
    def get_db_latency() -> int:
        """
        Simulate database latency metric.
        Returns value in milliseconds.
        """
        base = random.randint(50, 300)
        # 12% chance of high latency
        if random.random() < 0.12:
            return random.randint(2100, 4500)
        return base

    @staticmethod
    def check_cpu_spike(db: Session) -> bool:
        """Check for CPU spike and create incident if needed"""
        cpu_usage = MonitoringSimulator.get_cpu_usage()

        if cpu_usage > MonitoringSimulator.CPU_THRESHOLD:
            service = random.choice(MonitoringSimulator.SERVICES)
            incident_data = IncidentCreate(
                title=f"High CPU Usage Detected on {service}",
                description=f"CPU usage spiked to {cpu_usage}% (threshold: {MonitoringSimulator.CPU_THRESHOLD}%)",
                severity="high",
                service=service
            )
            IncidentService.create_incident(db, incident_data)
            return True
        return False

    @staticmethod
    def check_memory_leak(db: Session) -> bool:
        """Check for memory leak and create incident if needed"""
        memory_usage = MonitoringSimulator.get_memory_usage()

        if memory_usage > MonitoringSimulator.MEMORY_THRESHOLD:
            service = random.choice(MonitoringSimulator.SERVICES)
            incident_data = IncidentCreate(
                title=f"Memory Usage Critical on {service}",
                description=f"Memory usage at {memory_usage}% (threshold: {MonitoringSimulator.MEMORY_THRESHOLD}%). Possible memory leak detected.",
                severity="critical",
                service=service
            )
            IncidentService.create_incident(db, incident_data)
            return True
        return False

    @staticmethod
    def check_api_failure(db: Session) -> bool:
        """Check for API failures and create incident if needed"""
        error_rate = MonitoringSimulator.get_api_error_rate()

        if error_rate > MonitoringSimulator.API_ERROR_RATE_THRESHOLD:
            service = random.choice(MonitoringSimulator.SERVICES)
            incident_data = IncidentCreate(
                title=f"API Failure Rate High on {service}",
                description=f"Error rate: {error_rate*100:.2f}% (threshold: {MonitoringSimulator.API_ERROR_RATE_THRESHOLD*100:.1f}%)",
                severity="high",
                service=service
            )
            IncidentService.create_incident(db, incident_data)
            return True
        return False

    @staticmethod
    def check_db_latency(db: Session) -> bool:
        """Check for database latency and create incident if needed"""
        latency = MonitoringSimulator.get_db_latency()

        if latency > MonitoringSimulator.DB_LATENCY_THRESHOLD:
            incident_data = IncidentCreate(
                title="Database Latency Exceeded",
                description=f"Database query latency: {latency}ms (threshold: {MonitoringSimulator.DB_LATENCY_THRESHOLD}ms). System performance may be affected.",
                severity="medium",
                service="database"
            )
            IncidentService.create_incident(db, incident_data)
            return True
        return False

    @staticmethod
    def get_metrics() -> Dict[str, Any]:
        """Get current metrics snapshot"""
        return {
            "cpu_usage": MonitoringSimulator.get_cpu_usage(),
            "memory_usage": MonitoringSimulator.get_memory_usage(),
            "api_error_rate": round(MonitoringSimulator.get_api_error_rate(), 4),
            "db_latency_ms": MonitoringSimulator.get_db_latency(),
        }
