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
from app.services.ai import AIIncidentAnalyzer
from app.services.log import LogService


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

            # Generate sample logs for the incident
            logs = MonitoringSimulator._generate_cpu_logs(service, cpu_usage)

            # Get current metrics
            metrics = MonitoringSimulator.get_metrics()

            # Create incident
            incident_data = IncidentCreate(
                title=f"High CPU Usage Detected on {service}",
                description=f"CPU usage spiked to {cpu_usage}% (threshold: {MonitoringSimulator.CPU_THRESHOLD}%)",
                severity="high",
                service=service
            )
            incident = IncidentService.create_incident(db, incident_data)
            LogService.create_logs_from_text(db, logs, service, incident_id=incident["id"])

            # Perform AI analysis
            try:
                analyzer = AIIncidentAnalyzer()
                analysis = analyzer.analyze_incident(logs, metrics)
                if analysis:
                    print(f"AI Analysis for incident {incident['id']}:")
                    print(f"Possible causes: {analysis.possible_causes}")
                    print(f"Recommended actions: {analysis.recommended_actions}")
                    print(f"Confidence: {analysis.confidence_score}, Severity: {analysis.severity_assessment}")
            except Exception as e:
                print(f"AI analysis failed: {e}")

            return True
        return False

    @staticmethod
    def check_memory_leak(db: Session) -> bool:
        """Check for memory leak and create incident if needed"""
        memory_usage = MonitoringSimulator.get_memory_usage()

        if memory_usage > MonitoringSimulator.MEMORY_THRESHOLD:
            service = random.choice(MonitoringSimulator.SERVICES)

            # Generate sample logs for the incident
            logs = MonitoringSimulator._generate_memory_logs(service, memory_usage)

            # Get current metrics
            metrics = MonitoringSimulator.get_metrics()

            incident_data = IncidentCreate(
                title=f"Memory Usage Critical on {service}",
                description=f"Memory usage at {memory_usage}% (threshold: {MonitoringSimulator.MEMORY_THRESHOLD}%). Possible memory leak detected.",
                severity="critical",
                service=service
            )
            incident = IncidentService.create_incident(db, incident_data)
            LogService.create_logs_from_text(db, logs, service, incident_id=incident["id"])

            # Perform AI analysis
            try:
                analyzer = AIIncidentAnalyzer()
                analysis = analyzer.analyze_incident(logs, metrics)
                if analysis:
                    print(f"AI Analysis for incident {incident['id']}:")
                    print(f"Possible causes: {analysis.possible_causes}")
                    print(f"Recommended actions: {analysis.recommended_actions}")
                    print(f"Confidence: {analysis.confidence_score}, Severity: {analysis.severity_assessment}")
            except Exception as e:
                print(f"AI analysis failed: {e}")

            return True
        return False

    @staticmethod
    def check_api_failure(db: Session) -> bool:
        """Check for API failures and create incident if needed"""
        error_rate = MonitoringSimulator.get_api_error_rate()

        if error_rate > MonitoringSimulator.API_ERROR_RATE_THRESHOLD:
            service = random.choice(MonitoringSimulator.SERVICES)

            # Generate sample logs for the incident
            logs = MonitoringSimulator._generate_api_logs(service, error_rate)

            # Get current metrics
            metrics = MonitoringSimulator.get_metrics()

            incident_data = IncidentCreate(
                title=f"API Failure Rate High on {service}",
                description=f"Error rate: {error_rate*100:.2f}% (threshold: {MonitoringSimulator.API_ERROR_RATE_THRESHOLD*100:.1f}%)",
                severity="high",
                service=service
            )
            incident = IncidentService.create_incident(db, incident_data)
            LogService.create_logs_from_text(db, logs, service, incident_id=incident["id"])

            # Perform AI analysis
            try:
                analyzer = AIIncidentAnalyzer()
                analysis = analyzer.analyze_incident(logs, metrics)
                if analysis:
                    print(f"AI Analysis for incident {incident['id']}:")
                    print(f"Possible causes: {analysis.possible_causes}")
                    print(f"Recommended actions: {analysis.recommended_actions}")
                    print(f"Confidence: {analysis.confidence_score}, Severity: {analysis.severity_assessment}")
            except Exception as e:
                print(f"AI analysis failed: {e}")

            return True
        return False

    @staticmethod
    def check_db_latency(db: Session) -> bool:
        """Check for database latency and create incident if needed"""
        latency = MonitoringSimulator.get_db_latency()

        if latency > MonitoringSimulator.DB_LATENCY_THRESHOLD:
            # Generate sample logs for the incident
            logs = MonitoringSimulator._generate_db_logs(latency)

            # Get current metrics
            metrics = MonitoringSimulator.get_metrics()

            incident_data = IncidentCreate(
                title="Database Latency Exceeded",
                description=f"Database query latency: {latency}ms (threshold: {MonitoringSimulator.DB_LATENCY_THRESHOLD}ms). System performance may be affected.",
                severity="medium",
                service="database"
            )
            incident = IncidentService.create_incident(db, incident_data)
            LogService.create_logs_from_text(db, logs, "database", incident_id=incident["id"])

            # Perform AI analysis
            try:
                analyzer = AIIncidentAnalyzer()
                analysis = analyzer.analyze_incident(logs, metrics)
                if analysis:
                    print(f"AI Analysis for incident {incident['id']}:")
                    print(f"Possible causes: {analysis.possible_causes}")
                    print(f"Recommended actions: {analysis.recommended_actions}")
                    print(f"Confidence: {analysis.confidence_score}, Severity: {analysis.severity_assessment}")
            except Exception as e:
                print(f"AI analysis failed: {e}")

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

    @staticmethod
    def _generate_cpu_logs(service: str, cpu_usage: int) -> str:
        """Generate sample logs for CPU spike incident"""
        timestamp = "2024-01-15 10:30:45"
        return f"""
[{timestamp}] INFO {service}: CPU usage at {cpu_usage}%
[{timestamp}] WARN {service}: High CPU load detected, spawning additional worker processes
[{timestamp}] ERROR {service}: CPU throttle activated - system performance degraded
[{timestamp}] WARN {service}: Request queue growing due to CPU bottleneck
[{timestamp}] INFO {service}: Attempting to scale horizontally
"""

    @staticmethod
    def _generate_memory_logs(service: str, memory_usage: int) -> str:
        """Generate sample logs for memory leak incident"""
        timestamp = "2024-01-15 10:30:45"
        return f"""
[{timestamp}] INFO {service}: Memory usage at {memory_usage}%
[{timestamp}] WARN {service}: Garbage collection running frequently
[{timestamp}] ERROR {service}: OutOfMemoryError in worker thread
[{timestamp}] WARN {service}: Memory pressure causing request timeouts
[{timestamp}] INFO {service}: Attempting emergency memory cleanup
"""

    @staticmethod
    def _generate_api_logs(service: str, error_rate: float) -> str:
        """Generate sample logs for API failure incident"""
        timestamp = "2024-01-15 10:30:45"
        error_percent = error_rate * 100
        return f"""
[{timestamp}] INFO {service}: API error rate: {error_percent:.2f}%
[{timestamp}] ERROR {service}: HTTP 500 Internal Server Error - /api/users
[{timestamp}] ERROR {service}: HTTP 502 Bad Gateway - /api/orders
[{timestamp}] WARN {service}: Circuit breaker activated for downstream service
[{timestamp}] INFO {service}: Retrying failed requests
"""

    @staticmethod
    def _generate_db_logs(latency: int) -> str:
        """Generate sample logs for database latency incident"""
        timestamp = "2024-01-15 10:30:45"
        return f"""
[{timestamp}] INFO database: Query latency: {latency}ms
[{timestamp}] WARN database: Connection pool exhausted
[{timestamp}] ERROR database: Query timeout after 30 seconds
[{timestamp}] WARN database: Deadlock detected in transaction
[{timestamp}] INFO database: Rolling back slow transactions
"""
