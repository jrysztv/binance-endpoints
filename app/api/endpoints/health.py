from datetime import datetime, UTC
from fastapi import APIRouter
from app.schemas.responses import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint that returns the service status.

    Returns:
        HealthResponse: Service health information including status, timestamp, service name, and version.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(UTC).isoformat(),
        service="binance-endpoints",
        version="0.1.0",
    )
