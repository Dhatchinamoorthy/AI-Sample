from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os

from app.config import settings
from app.database import create_tables
from app.api import chat
from app.api import widgets

# Create FastAPI app
app = FastAPI(
    title="AI Widget Chat API",
    description="Backend API for AI-powered chat application with dynamic widgets",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(widgets.router, prefix="/api/v1/widgets", tags=["widgets"])


@app.on_event("startup")
async def startup_event():
    """Initialize database and other startup tasks"""
    # Create database directory if it doesn't exist
    db_dir = os.path.dirname(settings.database_url.replace("sqlite:///", ""))
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    # Create database tables
    create_tables()
    print("Database tables created successfully")


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "AI Widget Chat API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    if settings.debug:
        import traceback
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(exc),
                "traceback": traceback.format_exc()
            }
        )
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
