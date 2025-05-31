from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import health
from app.api.endpoints import binance_endpoints

app = FastAPI(
    title="Binance Connector Backend",
    description="""
    ## Binance Analysis API with Different Serialization Formats
    
    This API demonstrates 4 different serialization approaches for financial data analysis:
    
    ### 🔄 Serialization Formats:
    - **JSON** - Standard API responses (`application/json`)
    - **CSV** - Tabular data exports (`text/csv`) 
    - **HTML** - Human-readable reports (`text/html`)
    - **XML** - Structured markup (`application/xml`)
    - **PNG** - Visual charts (`image/png`)
    
    ### 📊 Analysis Types:
    - **Market Statistics** - Aggregated ticker data with sentiment analysis
    - **Technical Analysis** - Price data with technical indicators  
    - **Correlation Analysis** - Multi-asset correlation matrices
    - **Liquidity Analysis** - Order book depth analysis
    
    Each endpoint uses the same underlying business logic but different serialization formats!
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(binance_endpoints.router)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Binance Connector Backend - Different Serialization Formats",
        "version": "1.0.0",
        "formats": {
            "json": "Standard API responses",
            "csv": "Tabular data exports",
            "html": "Human-readable reports",
            "xml": "Structured markup",
            "png": "Visual charts",
        },
        "endpoints": {
            "json_example": "/api/v1/market/statistics/json",
            "csv_example": "/api/v1/analysis/technical/BTCUSDT/csv",
            "html_example": "/api/v1/analysis/correlation/html",
            "xml_example": "/api/v1/market/liquidity/BTCUSDT/xml",
            "chart_example": "/api/v1/charts/technical?symbol=BTCUSDT",
        },
        "documentation": "/docs",
        "health": "/health",
    }
