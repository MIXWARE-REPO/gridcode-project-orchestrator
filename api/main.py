"""
GriPro Dashboard API
FastAPI backend for the client-facing dashboard.

Provides:
- Authentication via project codes
- Project status and details
- Chat with Primo (Project Manager AI)
- Real-time updates via WebSocket
"""
from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routes import auth, chat, projects


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    # Startup
    print("[GriPro] Dashboard API starting up...")
    print(f"   Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"   Supabase: {'configured' if os.getenv('SUPABASE_URL') else 'not configured (using demo data)'}")
    yield
    # Shutdown
    print("[GriPro] Dashboard API shutting down...")


# Create FastAPI application
app = FastAPI(
    title="GriPro Dashboard API",
    description="""
    API for the GriPro (GridCode Project Orchestrator) client dashboard.

    ## Features

    - **Authentication**: Login with project codes to access your dashboard
    - **Project Status**: View real-time progress, phases, and agent activity
    - **Chat with Primo**: Interact with your AI Project Manager
    - **Activity Timeline**: Track all work done on your project
    - **Real-time Updates**: WebSocket connection for live updates

    ## Authentication

    1. Get your project code (e.g., GRIP-001, DEMO-123)
    2. Call POST /api/auth/login with your code
    3. Use the returned JWT token in the Authorization header

    ## Demo Access

    Use code `DEMO-123` to access a demo project.
    """,
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://localhost:3001",
        "https://*.evasoft.app",  # Production subdomains
        "https://gripro.dev",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(chat.router, prefix="/api")


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "gripro-dashboard-api",
        "version": "0.1.0",
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "GriPro Dashboard API",
        "version": "0.1.0",
        "docs": "/api/docs",
        "health": "/api/health",
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Not found", "detail": str(exc.detail) if hasattr(exc, 'detail') else "Resource not found"},
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "An unexpected error occurred"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
