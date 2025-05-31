from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    timestamp: str
    service: str
    version: str


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str
    message: str
    timestamp: str
