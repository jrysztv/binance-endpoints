"""
Binance API Endpoints with Different Serialization Formats

This module implements 4 endpoints that demonstrate different serialization approaches:
1. JSON Endpoint - Standard API response format
2. CSV Endpoint - Tabular data export format
3. HTML Endpoint - Human-readable report format
4. XML Endpoint - Structured markup format

Plus a bonus Chart endpoint for visual data representation.
"""

from fastapi import APIRouter, Query, Path, HTTPException, Response
from typing import List, Optional
from app.core.binance_analysis import BinanceAnalyzer
from app.core.serializers import get_serializer
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1", tags=["binance-analysis"])

# Initialize analyzer (singleton pattern)
analyzer = BinanceAnalyzer()


@router.get("/market/statistics/json", summary="Market Statistics (JSON Format)")
async def get_market_statistics_json(
    symbols: Optional[List[str]] = Query(
        None, description="List of symbols to analyze (default: major cryptos)"
    ),
    include_volume: bool = Query(
        True, description="Include volume data in calculations"
    ),
):
    """
    **ENDPOINT 1: Market Statistics with JSON Serialization**

    Returns aggregated market statistics with custom volatility metrics,
    sentiment analysis, and performance rankings in JSON format.

    **Serialization Format**: JSON (application/json)
    - Statistical summary with aggregated metrics
    - Top performers ranking
    - Market sentiment classification
    - Custom volatility calculations
    """
    try:
        # Get data from business logic
        data = analyzer.get_market_statistics(
            symbols=symbols, include_volume=include_volume
        )

        if "error" in data:
            raise HTTPException(status_code=500, detail=data["error"])

        # Serialize to JSON
        serializer = get_serializer(data, "json")
        content = serializer.serialize()

        return Response(
            content=content,
            media_type=serializer.get_content_type(),
            headers={"Content-Disposition": "inline; filename=market_statistics.json"},
        )

    except Exception as e:
        logger.error(f"Error in get_market_statistics_json: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/analysis/technical/{symbol}/csv", summary="Technical Analysis (CSV Format)"
)
async def get_technical_analysis_csv(
    symbol: str = Path(..., description="Trading symbol (e.g., BTCUSDT)"),
    interval: str = Query("1h", description="Time interval for candlesticks"),
    limit: int = Query(100, description="Number of data points to retrieve"),
):
    """
    **ENDPOINT 2: Technical Analysis with CSV Serialization**

    Returns technical analysis data with computed indicators in CSV format
    suitable for spreadsheet import and data analysis.

    **Serialization Format**: CSV (text/csv)
    - Time-series data in tabular format
    - Technical indicators (SMA, RSI, MACD)
    - Downloadable spreadsheet format
    """
    try:
        # Get data from business logic
        data = analyzer.get_technical_analysis(
            symbol=symbol, interval=interval, limit=limit
        )

        if "error" in data:
            raise HTTPException(status_code=500, detail=data["error"])

        # Serialize to CSV
        serializer = get_serializer(data, "csv")
        content = serializer.serialize()

        return Response(
            content=content,
            media_type=serializer.get_content_type(),
            headers={
                "Content-Disposition": f"attachment; filename={symbol}_technical_analysis.csv"
            },
        )

    except Exception as e:
        logger.error(f"Error in get_technical_analysis_csv: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis/correlation/html", summary="Correlation Analysis (HTML Report)")
async def get_correlation_analysis_html(
    symbols: Optional[List[str]] = Query(
        None, description="List of symbols to analyze"
    ),
    days: int = Query(30, description="Number of days of historical data"),
    include_clusters: bool = Query(
        True, description="Include risk clustering analysis"
    ),
):
    """
    **ENDPOINT 3: Correlation Analysis with HTML Serialization**

    Returns correlation analysis with portfolio metrics in a beautiful
    HTML report format for human consumption.

    **Serialization Format**: HTML (text/html)
    - Interactive correlation matrix visualization
    - Portfolio diversification metrics
    - Styled report with color-coded data
    - Risk clustering information
    """
    try:
        # Get data from business logic
        data = analyzer.get_correlation_analysis(
            symbols=symbols, days=days, include_clusters=include_clusters
        )

        if "error" in data:
            raise HTTPException(status_code=500, detail=data["error"])

        # Serialize to HTML
        serializer = get_serializer(data, "html")
        content = serializer.serialize()

        return Response(
            content=content,
            media_type=serializer.get_content_type(),
            headers={
                "Content-Disposition": "inline; filename=correlation_analysis.html"
            },
        )

    except Exception as e:
        logger.error(f"Error in get_correlation_analysis_html: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market/liquidity/{symbol}/xml", summary="Liquidity Analysis (XML Format)")
async def get_liquidity_analysis_xml(
    symbol: str = Path(..., description="Trading symbol to analyze"),
    depth_limit: int = Query(
        100, description="Number of order book levels to retrieve"
    ),
    include_levels: bool = Query(True, description="Include detailed level data"),
):
    """
    **ENDPOINT 4: Liquidity Analysis with XML Serialization**

    Returns order book depth analysis with liquidity metrics in structured
    XML format suitable for system integration and data exchange.

    **Serialization Format**: XML (application/xml)
    - Hierarchical order book structure
    - Nested bid/ask analysis
    - Market microstructure data
    - Machine-readable structured format
    """
    try:
        # Get data from business logic
        data = analyzer.get_liquidity_analysis(
            symbol=symbol, depth_limit=depth_limit, include_levels=include_levels
        )

        if "error" in data:
            raise HTTPException(status_code=500, detail=data["error"])

        # Serialize to XML
        serializer = get_serializer(data, "xml")
        content = serializer.serialize()

        return Response(
            content=content,
            media_type=serializer.get_content_type(),
            headers={
                "Content-Disposition": f"attachment; filename={symbol}_liquidity_analysis.xml"
            },
        )

    except Exception as e:
        logger.error(f"Error in get_liquidity_analysis_xml: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/charts/{analysis_type}", summary="Chart Visualization (PNG Format)")
async def get_analysis_chart(
    analysis_type: str = Path(
        ..., description="Type of analysis: market, technical, correlation, liquidity"
    ),
    symbol: Optional[str] = Query(
        None, description="Symbol for technical/liquidity analysis"
    ),
    symbols: Optional[List[str]] = Query(
        None, description="Symbols for market/correlation analysis"
    ),
    interval: str = Query("1h", description="Interval for technical analysis"),
    days: int = Query(30, description="Days for correlation analysis"),
):
    """
    **BONUS ENDPOINT: Chart Visualization with PNG Serialization**

    Returns visual charts and graphs of the analysis data in PNG format
    for presentations and visual analysis.

    **Serialization Format**: PNG (image/png)
    - Technical analysis price charts
    - Correlation heatmaps
    - Market performance bar charts
    - Order book depth visualization
    """
    try:
        # Get appropriate data based on analysis type
        if analysis_type == "market":
            data = analyzer.get_market_statistics(symbols=symbols)
        elif analysis_type == "technical":
            if not symbol:
                raise HTTPException(
                    status_code=400, detail="Symbol required for technical analysis"
                )
            data = analyzer.get_technical_analysis(symbol=symbol, interval=interval)
        elif analysis_type == "correlation":
            data = analyzer.get_correlation_analysis(symbols=symbols, days=days)
        elif analysis_type == "liquidity":
            if not symbol:
                raise HTTPException(
                    status_code=400, detail="Symbol required for liquidity analysis"
                )
            data = analyzer.get_liquidity_analysis(symbol=symbol)
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid analysis type. Use: market, technical, correlation, liquidity",
            )

        if "error" in data:
            raise HTTPException(status_code=500, detail=data["error"])

        # Serialize to Chart (PNG)
        serializer = get_serializer(data, "chart")
        content = serializer.serialize()

        return Response(
            content=content,
            media_type=serializer.get_content_type(),
            headers={
                "Content-Disposition": f"inline; filename={analysis_type}_chart.png"
            },
        )

    except Exception as e:
        logger.error(f"Error in get_analysis_chart: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Summary endpoint for documentation
@router.get("/", summary="API Overview")
async def api_overview():
    """
    **Binance Analysis API - Different Serialization Formats**

    This API demonstrates 4 different serialization approaches for the same underlying data:

    ### Endpoints by Serialization Format:

    1. **JSON Format** (`/market/statistics/json`)
       - Standard API response format
       - Structured data with nested objects
       - Content-Type: application/json

    2. **CSV Format** (`/analysis/technical/{symbol}/csv`)
       - Tabular data export format
       - Suitable for spreadsheet import
       - Content-Type: text/csv

    3. **HTML Format** (`/analysis/correlation/html`)
       - Human-readable report format
       - Styled presentation with tables
       - Content-Type: text/html

    4. **XML Format** (`/market/liquidity/{symbol}/xml`)
       - Structured markup format
       - Machine-readable hierarchical data
       - Content-Type: application/xml

    5. **PNG Charts** (`/charts/{analysis_type}`)
       - Visual data representation
       - Charts and graphs
       - Content-Type: image/png

    ### Underlying Analysis Types:

    - **Market Statistics**: Aggregated ticker data with sentiment analysis
    - **Technical Analysis**: Price data with technical indicators (SMA, RSI, MACD)
    - **Correlation Analysis**: Multi-asset correlation matrix with portfolio metrics
    - **Liquidity Analysis**: Order book depth with market microstructure data

    Each endpoint uses the same business logic but different serialization formats!
    """
    return {
        "title": "Binance Analysis API",
        "description": "4 Different Serialization Formats for Financial Data",
        "formats": {
            "json": "/market/statistics/json",
            "csv": "/analysis/technical/BTCUSDT/csv",
            "html": "/analysis/correlation/html",
            "xml": "/market/liquidity/BTCUSDT/xml",
            "png": "/charts/technical?symbol=BTCUSDT",
        },
        "documentation": "/docs",
    }
