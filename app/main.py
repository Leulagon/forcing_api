from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import init_db
from .routers import ingestion

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="LEULS YUMMY YUMMY APP",
    lifespan=lifespan,
)

app.include_router(ingestion.router)

@app.get("/")
def root():
    return {
        "message": "Forcing Pipeline App",
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {
        "status": "ok"
    }