from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import health

app = FastAPI(
    title="Binance Endpoints API",
    description="A production-ready FastAPI backend for Binance market data analysis",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["health"])


@app.get("/")
async def root():
    """Root endpoint that redirects to API documentation."""
    return {"message": "Binance Endpoints API", "docs": "/docs", "redoc": "/redoc"}
