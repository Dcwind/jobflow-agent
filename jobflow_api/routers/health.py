"""Health check endpoints."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy"}


@router.get("/")
def root() -> dict:
    """Root endpoint."""
    return {"service": "Jobflow API", "status": "running"}
