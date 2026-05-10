from fastapi import FastAPI
from app.api.incidents import router as incidents_router
from app.core.database import init_db

app = FastAPI(
    title="SentinelOps API",
    description="AI DevOps Incident Management System",
    version="1.0.0"
)

# Initialize database on startup
init_db()

# Include routers
app.include_router(incidents_router)


@app.get("/")
async def root():
    return {"message": "AI DevOps Agent Running 🚀"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
