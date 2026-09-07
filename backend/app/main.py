"""Main FastAPI application for Sahlaan AI Backend"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .config import settings
from .api import generations

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# Include routers
app.include_router(generations.router)

# Mount outputs directory for file serving
outputs_path = Path(settings.OUTPUTS_DIR)
if outputs_path.exists():
    app.mount("/api/v1/outputs", StaticFiles(directory=str(outputs_path)), name="outputs")


@app.get("/", tags=["health"])
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "mock_mode": settings.MOCK_MODE
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT
    )
