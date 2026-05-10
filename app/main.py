from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "AI DevOps Agent Running 🚀"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
