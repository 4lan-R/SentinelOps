# SentinalOps

## Overview

The Monitoring Simulator generates fake infrastructure monitoring events and automatically creates incidents when thresholds are exceeded. This allows you to test the SentinelOps incident management system with realistic scenarios.

## Features

### Simulated Metrics

1. **CPU Usage**
   - Base: 30-70%
   - Spikes: 91-99% (20% probability)
   - Threshold: 90%
   - Severity: HIGH

2. **Memory Usage**
   - Base: 40-75%
   - High: 86-98% (15% probability - simulating memory leaks)
   - Threshold: 85%
   - Severity: CRITICAL

3. **API Error Rate**
   - Base: 1-5%
   - High: 11-25% (10% probability)
   - Threshold: 10%
   - Severity: HIGH

4. **Database Latency**
   - Base: 50-300ms
   - High: 2100-4500ms (12% probability)
   - Threshold: 2000ms
   - Severity: MEDIUM

### Services Monitored

- `api-server`
- `database`
- `cache-layer`
- `message-queue`
- `auth-service`

## Architecture

### Background Tasks

The monitoring simulator runs as a background task that:
- Starts automatically when the FastAPI app initializes
- Checks all metrics every 5 seconds
- Creates incidents when thresholds are exceeded
- Broadcasts incidents via WebSocket to connected clients
- Gracefully stops on application shutdown

### Components

1. **MonitoringSimulator** (`app/services/monitoring.py`)
   - Core simulation logic
   - Metric generation
   - Threshold checking
   - Incident creation

2. **BackgroundTaskManager** (`app/tasks.py`)
   - Manages the monitoring loop
   - Lifecycle hooks (startup/shutdown)
   - Error handling

3. **Monitoring API** (`app/api/monitoring.py`)
   - `/monitoring/metrics` - Get current metrics
   - `/monitoring/health` - System health status

## API Endpoints

### Get Current Metrics
```bash
GET /monitoring/metrics
```

Response:
```json
{
  "status": "healthy",
  "metrics": {
    "cpu_usage": 45,
    "memory_usage": 62,
    "api_error_rate": 0.0245,
    "db_latency_ms": 187
  },
  "thresholds": {
    "cpu_threshold": 90,
    "memory_threshold": 85,
    "api_error_rate_threshold": 0.1,
    "db_latency_threshold_ms": 2000
  }
}
```

### Get Monitoring Health
```bash
GET /monitoring/health
```

Response:
```json
{
  "status": "operational",
  "services_monitored": [
    "api-server",
    "database",
    "cache-layer",
    "message-queue",
    "auth-service"
  ],
  "check_interval_seconds": 5
}
```

## Usage

### Start Monitoring

The monitoring simulator automatically starts when you run the FastAPI app:

```bash
uvicorn app.main:app --reload
```

Console output:
```
✓ Monitoring simulator started
```

### View Generated Incidents

```bash
GET /incidents/
```

### Stop Monitoring

The simulator gracefully stops when you stop the server (Ctrl+C).

Console output:
```
✓ Monitoring simulator stopped
```

## Customization

### Adjust Thresholds

Edit [app/services/monitoring.py](app/services/monitoring.py):

```python
CPU_THRESHOLD = 90  # Change threshold
MEMORY_THRESHOLD = 85
API_ERROR_RATE_THRESHOLD = 0.1
DB_LATENCY_THRESHOLD = 2000  # in ms
```

### Adjust Check Interval

Edit [app/tasks.py](app/tasks.py):

```python
await asyncio.sleep(5)  # Change to desired interval in seconds
```

### Add/Remove Services

Edit [app/services/monitoring.py](app/services/monitoring.py):

```python
SERVICES = [
    "api-server",
    "database",
    "cache-layer",
    "message-queue",
    "auth-service",
    # Add more services here
]
```

### Modify Metric Distribution

Edit the metric generation methods in `MonitoringSimulator`:

```python
@staticmethod
def get_cpu_usage() -> int:
    base = random.randint(30, 70)  # Adjust base range
    if random.random() < 0.2:  # Adjust spike probability
        return random.randint(91, 99)  # Adjust spike range
    return base
```

## Example Workflow

1. **Start the server**
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Monitor metrics in real-time**
   ```bash
   while true; do curl http://localhost:8000/monitoring/metrics; sleep 5; done
   ```

3. **Watch incidents being created**
   ```bash
   while true; do curl http://localhost:8000/incidents/; sleep 5; done
   ```

4. **Connect WebSocket for real-time alerts**
   ```javascript
   const ws = new WebSocket('ws://localhost:8000/ws/alerts');
   ws.onmessage = (event) => console.log(JSON.parse(event.data));
   ```

## Testing

To simulate various scenarios:

- Wait for CPU/memory spikes to trigger HIGH/CRITICAL incidents
- Observe API error rate fluctuations
- Monitor database latency variations
- Verify incidents appear in the system
- Check WebSocket broadcasts to connected clients

## Future Enhancements

- Add predictive alerts based on trends
- Implement metric persistence and historical analysis
- Add custom simulation scenarios
- Support for metric correlation analysis
- Integration with external monitoring tools
