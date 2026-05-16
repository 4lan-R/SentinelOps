from fastapi import FastAPI, WebSocket
from fastapi.websockets import WebSocketDisconnect
from app.api.incidents import router as incidents_router
from app.api.logs import router as logs_router
from app.api.monitoring import router as monitoring_router
from app.core.database import init_db
from app.websocket import connection_manager
from app.tasks import lifespan

app = FastAPI(
    title="SentinelOps API",
    description="AI DevOps Incident Management System",
    version="1.0.0",
    lifespan=lifespan
)

# Initialize database on startup
init_db()

# Include routers
app.include_router(incidents_router)
app.include_router(logs_router)
app.include_router(monitoring_router)


@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    await connection_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)


@app.get("/")
async def root():
    return {"message": "AI DevOps Agent Running 🚀"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
