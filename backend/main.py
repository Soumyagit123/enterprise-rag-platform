from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings
import structlog
import time
import os

from api.middleware import setup_observability_and_security

# LangSmith Tracing Configuration
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "enterprise-rag-platform"
# Ensure LANGCHAIN_API_KEY is set in your environment

class Settings(BaseSettings):
    app_name: str = "Enterprise RAG Platform API"
    environment: str = "development"

    class Config:
        env_file = ".env"

settings = Settings()
logger = structlog.get_logger()

app = FastAPI(
    title=settings.app_name,
    description="Backend API for Enterprise RAG Platform",
    version="1.0.0"
)

# CORS configuration to allow Next.js frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Apply rate limiting and prometheus metrics
setup_observability_and_security(app)

# Include the main API routes
from api.routes import router as api_router
app.include_router(api_router, prefix="/api")

@app.get("/health")
async def health_check():
    """Basic health check endpoint for liveness probes."""
    return {"status": "ok", "environment": settings.environment}

@app.get("/")
async def root():
    return {"message": f"Welcome to the {settings.app_name}"}
