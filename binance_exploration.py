# %% [markdown]
# # Binance API Exploration Notebook
#
# This notebook explores the Binance API to identify 4 different endpoints
# with various serialization approaches for our FastAPI backend.
#
# Goals:
# - Explore different Binance API endpoints
# - Test various data formats and structures
# - Identify interesting visualizations
# - Design 4 unique endpoints with different serializers

# %%
# Standard imports for data analysis
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional
import time

# Binance connector
from binance.spot import Spot

# Set up plotting style
plt.style.use("seaborn-v0_8")
sns.set_palette("husl")

# %%
# Initialize Binance client (public endpoints only, no API key needed for market data)
client = Spot()

print("✅ Binance client initialized successfully!")
print(f"Server time: {client.time()}")

# %% [markdown]
# ## 1. Market Data Endpoint Ideas
#
# Let's explore different types of market data that could form our endpoints

# %%
# Test basic symbol information
try:
    # Get exchange info for popular symbols
    exchange_info = client.exchange_info()
    symbols = [s for s in exchange_info["symbols"] if s["status"] == "TRADING"][:10]

    print(
        f"Total trading symbols: {len([s for s in exchange_info['symbols'] if s['status'] == 'TRADING'])}"
    )
    print("Sample symbols:")
    for symbol in symbols:
        print(f"  {symbol['symbol']}: {symbol['baseAsset']}/{symbol['quoteAsset']}")

except Exception as e:
    print(f"Error fetching exchange info: {e}")

# %%
# ENDPOINT IDEA 1: Real-time ticker data with statistical analysis
# Serializer: Custom statistical summary format


def get_ticker_statistics(symbols: List[str] = None) -> Dict:
    """
    Get ticker statistics for multiple symbols with custom analysis
    Returns: Statistical summary in custom format
    """
    if symbols is None:
        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "XRPUSDT"]

    ticker_data = []

    for symbol in symbols:
        try:
            ticker = client.ticker_24hr(symbol=symbol)

            # Convert to float for calculations
            price_change = float(ticker["priceChange"])
            price_change_percent = float(ticker["priceChangePercent"])
            high_price = float(ticker["highPrice"])
            low_price = float(ticker["lowPrice"])
            volume = float(ticker["volume"])

            ticker_data.append(
                {
                    "symbol": symbol,
                    "price_change": price_change,
                    "price_change_percent": price_change_percent,
                    "high_price": high_price,
                    "low_price": low_price,
                    "volume": volume,
                    "volatility": (high_price - low_price)
                    / low_price
                    * 100,  # Custom metric
                }
            )

        except Exception as e:
            print(f"Error fetching ticker for {symbol}: {e}")
            continue

    # Create DataFrame for analysis
    df = pd.DataFrame(ticker_data)

    if df.empty:
        return {"error": "No data available"}

    # Custom statistical analysis
    stats = {
        "summary": {
            "total_symbols": len(df),
            "avg_price_change_percent": df["price_change_percent"].mean(),
            "avg_volatility": df["volatility"].mean(),
            "total_volume": df["volume"].sum(),
        },
        "top_performers": df.nlargest(3, "price_change_percent")[
            ["symbol", "price_change_percent"]
        ].to_dict("records"),
        "most_volatile": df.nlargest(3, "volatility")[["symbol", "volatility"]].to_dict(
            "records"
        ),
        "market_sentiment": "bullish"
        if df["price_change_percent"].mean() > 0
        else "bearish",
        "raw_data": ticker_data,
    }

    return stats


# Test the function
print("=" * 50)
print("ENDPOINT 1: Ticker Statistics")
print("=" * 50)
ticker_stats = get_ticker_statistics()
print(f"Market Sentiment: {ticker_stats['summary']}")
print(f"Top Performers: {ticker_stats['top_performers']}")

# %%
# ENDPOINT IDEA 2: Historical candlestick data with technical indicators
# Serializer: Time-series data with computed indicators


def get_technical_analysis(
    symbol: str = "BTCUSDT", interval: str = "1h", limit: int = 100
) -> Dict:
    """
    Get candlestick data with technical indicators
    Returns: Time-series data with moving averages and RSI
    """
    try:
        # Get candlestick data
        klines = client.klines(symbol=symbol, interval=interval, limit=limit)

        # Convert to DataFrame
        df = pd.DataFrame(
            klines,
            columns=[
                "timestamp",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "close_time",
                "quote_asset_volume",
                "number_of_trades",
                "taker_buy_base_asset_volume",
                "taker_buy_quote_asset_volume",
                "ignore",
            ],
        )

        # Convert price columns to float
        price_cols = ["open", "high", "low", "close", "volume"]
        for col in price_cols:
            df[col] = df[col].astype(float)

        # Convert timestamp to datetime
        df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms")

        # Calculate technical indicators
        df["sma_20"] = df["close"].rolling(window=20).mean()
        df["sma_50"] = df["close"].rolling(window=50).mean()

        # Simple RSI calculation
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df["rsi"] = 100 - (100 / (1 + rs))

        # Bollinger Bands
        bb_period = 20
        df["bb_middle"] = df["close"].rolling(window=bb_period).mean()
        bb_std = df["close"].rolling(window=bb_period).std()
        df["bb_upper"] = df["bb_middle"] + (bb_std * 2)
        df["bb_lower"] = df["bb_middle"] - (bb_std * 2)

        # Prepare response data
        latest_data = df.iloc[-1]

        response = {
            "symbol": symbol,
            "interval": interval,
            "latest_price": float(latest_data["close"]),
            "indicators": {
                "sma_20": float(latest_data["sma_20"])
                if not pd.isna(latest_data["sma_20"])
                else None,
                "sma_50": float(latest_data["sma_50"])
                if not pd.isna(latest_data["sma_50"])
                else None,
                "rsi": float(latest_data["rsi"])
                if not pd.isna(latest_data["rsi"])
                else None,
                "bollinger_bands": {
                    "upper": float(latest_data["bb_upper"])
                    if not pd.isna(latest_data["bb_upper"])
                    else None,
                    "middle": float(latest_data["bb_middle"])
                    if not pd.isna(latest_data["bb_middle"])
                    else None,
                    "lower": float(latest_data["bb_lower"])
                    if not pd.isna(latest_data["bb_lower"])
                    else None,
                },
            },
            "price_action": {
                "trend": "upward"
                if latest_data["close"] > latest_data["sma_20"]
                else "downward",
                "volatility": "high"
                if latest_data["close"] > latest_data["bb_upper"]
                or latest_data["close"] < latest_data["bb_lower"]
                else "normal",
            },
            "time_series": df[["datetime", "close", "volume", "sma_20", "rsi"]]
            .tail(20)
            .to_dict("records"),
        }

        return response

    except Exception as e:
        return {"error": f"Failed to fetch technical analysis: {str(e)}"}


# Test the function
print("=" * 50)
print("ENDPOINT 2: Technical Analysis")
print("=" * 50)
tech_analysis = get_technical_analysis()
print(f"Symbol: {tech_analysis.get('symbol')}")
print(f"Latest Price: {tech_analysis.get('latest_price')}")
print(f"Trend: {tech_analysis.get('price_action', {}).get('trend')}")

# %%
# ENDPOINT IDEA 3: Multi-symbol correlation analysis
# Serializer: Matrix/heatmap data format


def get_correlation_analysis(symbols: List[str] = None, days: int = 30) -> Dict:
    """
    Analyze correlations between multiple cryptocurrencies
    Returns: Correlation matrix and clustering data
    """
    if symbols is None:
        symbols = [
            "BTCUSDT",
            "ETHUSDT",
            "BNBUSDT",
            "ADAUSDT",
            "XRPUSDT",
            "DOTUSDT",
            "LINKUSDT",
        ]

    try:
        # Collect price data for all symbols
        price_data = {}

        for symbol in symbols:
            try:
                # Get daily candlestick data
                klines = client.klines(symbol=symbol, interval="1d", limit=days)
                prices = [float(kline[4]) for kline in klines]  # closing prices
                price_data[symbol.replace("USDT", "")] = prices
            except Exception as e:
                print(f"Warning: Could not fetch data for {symbol}: {e}")
                continue

        if len(price_data) < 2:
            return {"error": "Insufficient data for correlation analysis"}

        # Create DataFrame
        df = pd.DataFrame(price_data)

        # Calculate returns (percentage change)
        returns_df = df.pct_change().dropna()

        # Calculate correlation matrix
        correlation_matrix = returns_df.corr()

        # Find highest and lowest correlations
        corr_pairs = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i + 1, len(correlation_matrix.columns)):
                corr_pairs.append(
                    {
                        "pair": f"{correlation_matrix.columns[i]}-{correlation_matrix.columns[j]}",
                        "correlation": float(correlation_matrix.iloc[i, j]),
                    }
                )

        corr_pairs.sort(key=lambda x: abs(x["correlation"]), reverse=True)

        # Portfolio metrics
        avg_correlation = correlation_matrix.mean().mean()

        response = {
            "analysis_period_days": days,
            "symbols_analyzed": list(df.columns),
            "correlation_matrix": correlation_matrix.round(4).to_dict(),
            "top_correlations": corr_pairs[:5],
            "portfolio_metrics": {
                "average_correlation": float(avg_correlation),
                "diversification_score": float(
                    1 - avg_correlation
                ),  # Higher is more diversified
                "market_regime": "correlated"
                if avg_correlation > 0.7
                else "diversified",
            },
            "risk_clusters": {
                "high_correlation_pairs": [
                    p for p in corr_pairs if p["correlation"] > 0.8
                ],
                "negative_correlation_pairs": [
                    p for p in corr_pairs if p["correlation"] < -0.3
                ],
            },
        }

        return response

    except Exception as e:
        return {"error": f"Failed to perform correlation analysis: {str(e)}"}


# Test the function
print("=" * 50)
print("ENDPOINT 3: Correlation Analysis")
print("=" * 50)
correlation_data = get_correlation_analysis()
print(
    f"Diversification Score: {correlation_data.get('portfolio_metrics', {}).get('diversification_score')}"
)
print(
    f"Market Regime: {correlation_data.get('portfolio_metrics', {}).get('market_regime')}"
)

# %%
# ENDPOINT IDEA 4: Order book depth analysis with liquidity metrics
# Serializer: Hierarchical/nested structure with aggregations


def get_liquidity_analysis(symbol: str = "BTCUSDT", depth_limit: int = 100) -> Dict:
    """
    Analyze order book depth and liquidity metrics
    Returns: Nested structure with bid/ask analysis and liquidity scores
    """
    try:
        # Get order book data
        order_book = client.depth(symbol=symbol, limit=depth_limit)

        # Get current ticker for reference price
        ticker = client.ticker_price(symbol=symbol)
        current_price = float(ticker["price"])

        # Process bids and asks
        bids = [[float(price), float(qty)] for price, qty in order_book["bids"]]
        asks = [[float(price), float(qty)] for price, qty in order_book["asks"]]

        # Calculate bid/ask spread
        best_bid = bids[0][0] if bids else 0
        best_ask = asks[0][0] if asks else 0
        spread = best_ask - best_bid
        spread_percent = (spread / current_price) * 100 if current_price > 0 else 0

        # Calculate depth metrics
        def calculate_depth_metrics(orders, is_bid=True):
            if not orders:
                return {"total_volume": 0, "avg_price": 0, "depth_levels": []}

            total_volume = sum(qty for price, qty in orders)
            weighted_price = (
                sum(price * qty for price, qty in orders) / total_volume
                if total_volume > 0
                else 0
            )

            # Group by price ranges (depth levels)
            depth_levels = []
            cumulative_volume = 0

            for i, (price, qty) in enumerate(orders[:20]):  # Top 20 levels
                cumulative_volume += qty
                price_distance = abs(price - current_price) / current_price * 100

                depth_levels.append(
                    {
                        "level": i + 1,
                        "price": price,
                        "quantity": qty,
                        "cumulative_volume": cumulative_volume,
                        "price_distance_percent": price_distance,
                    }
                )

            return {
                "total_volume": total_volume,
                "weighted_avg_price": weighted_price,
                "depth_levels": depth_levels,
            }

        bid_metrics = calculate_depth_metrics(bids, True)
        ask_metrics = calculate_depth_metrics(asks, False)

        # Calculate liquidity score (simplified)
        liquidity_score = min(
            100, (bid_metrics["total_volume"] + ask_metrics["total_volume"]) / 1000
        )

        # Market microstructure analysis
        imbalance = (
            (bid_metrics["total_volume"] - ask_metrics["total_volume"])
            / (bid_metrics["total_volume"] + ask_metrics["total_volume"])
            if (bid_metrics["total_volume"] + ask_metrics["total_volume"]) > 0
            else 0
        )

        response = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "current_price": current_price,
            "spread_analysis": {
                "best_bid": best_bid,
                "best_ask": best_ask,
                "spread_absolute": spread,
                "spread_percent": spread_percent,
                "spread_classification": "tight" if spread_percent < 0.1 else "wide",
            },
            "order_book_depth": {
                "bids": bid_metrics,
                "asks": ask_metrics,
                "total_liquidity": bid_metrics["total_volume"]
                + ask_metrics["total_volume"],
            },
            "liquidity_metrics": {
                "liquidity_score": float(liquidity_score),
                "market_imbalance": float(imbalance),
                "imbalance_direction": "buy_pressure"
                if imbalance > 0.1
                else "sell_pressure"
                if imbalance < -0.1
                else "balanced",
                "market_quality": "excellent"
                if liquidity_score > 80
                else "good"
                if liquidity_score > 50
                else "poor",
            },
        }

        return response

    except Exception as e:
        return {"error": f"Failed to analyze liquidity: {str(e)}"}


# Test the function
print("=" * 50)
print("ENDPOINT 4: Liquidity Analysis")
print("=" * 50)
liquidity_data = get_liquidity_analysis()
print(f"Symbol: {liquidity_data.get('symbol')}")
print(
    f"Liquidity Score: {liquidity_data.get('liquidity_metrics', {}).get('liquidity_score')}"
)
print(
    f"Market Quality: {liquidity_data.get('liquidity_metrics', {}).get('market_quality')}"
)

# %% [markdown]
# ## Visualization Examples
#
# Let's create some sample visualizations to demonstrate the data

# %%
# Sample visualization for technical analysis
try:
    tech_data = get_technical_analysis("BTCUSDT", "1h", 50)

    if "time_series" in tech_data:
        # Convert to DataFrame for plotting
        ts_df = pd.DataFrame(tech_data["time_series"])
        ts_df["datetime"] = pd.to_datetime(ts_df["datetime"])

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

        # Price and moving average
        ax1.plot(ts_df["datetime"], ts_df["close"], label="Close Price", linewidth=2)
        ax1.plot(ts_df["datetime"], ts_df["sma_20"], label="SMA 20", alpha=0.7)
        ax1.set_title(f"{tech_data['symbol']} - Price Analysis")
        ax1.set_ylabel("Price (USDT)")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # RSI
        ax2.plot(
            ts_df["datetime"], ts_df["rsi"], label="RSI", color="orange", linewidth=2
        )
        ax2.axhline(y=70, color="r", linestyle="--", alpha=0.7, label="Overbought")
        ax2.axhline(y=30, color="g", linestyle="--", alpha=0.7, label="Oversold")
        ax2.set_title("Relative Strength Index (RSI)")
        ax2.set_ylabel("RSI")
        ax2.set_xlabel("Time")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

except Exception as e:
    print(f"Visualization error: {e}")

# %% [markdown]
# ## Summary: 4 Proposed Endpoints with Different Serializers
#
# Based on the exploration above, here are my recommendations for 4 endpoints:

print("=" * 60)
print("PROPOSED ENDPOINTS SUMMARY")
print("=" * 60)

endpoints_summary = {
    "1. Market Statistics Endpoint": {
        "path": "/api/v1/market/statistics",
        "serializer_type": "Statistical Summary Format",
        "description": "Real-time ticker data with custom statistical analysis",
        "unique_features": [
            "Custom volatility metrics",
            "Market sentiment analysis",
            "Top performers ranking",
            "Aggregated market overview",
        ],
        "parameters": ["symbols (optional list)", "include_volume (bool)"],
    },
    "2. Technical Analysis Endpoint": {
        "path": "/api/v1/analysis/technical/{symbol}",
        "serializer_type": "Time-Series with Indicators",
        "description": "Historical data with computed technical indicators",
        "unique_features": [
            "Moving averages (SMA 20, 50)",
            "RSI calculations",
            "Bollinger Bands",
            "Trend classification",
            "Time-series data points",
        ],
        "parameters": ["symbol (path)", "interval", "limit"],
    },
    "3. Correlation Analysis Endpoint": {
        "path": "/api/v1/analysis/correlation",
        "serializer_type": "Matrix/Heatmap Format",
        "description": "Multi-symbol correlation analysis with portfolio metrics",
        "unique_features": [
            "Correlation matrix data",
            "Portfolio diversification score",
            "Risk clustering",
            "Market regime classification",
        ],
        "parameters": ["symbols (list)", "days", "include_clusters (bool)"],
    },
    "4. Liquidity Analysis Endpoint": {
        "path": "/api/v1/market/liquidity/{symbol}",
        "serializer_type": "Hierarchical/Nested Structure",
        "description": "Order book depth analysis with liquidity metrics",
        "unique_features": [
            "Bid/ask spread analysis",
            "Order book depth levels",
            "Liquidity scoring",
            "Market imbalance detection",
            "Nested data structure",
        ],
        "parameters": ["symbol (path)", "depth_limit", "include_levels (bool)"],
    },
}

for endpoint, details in endpoints_summary.items():
    print(f"\n{endpoint}")
    print(f"  Path: {details['path']}")
    print(f"  Serializer: {details['serializer_type']}")
    print(f"  Description: {details['description']}")
    print(f"  Parameters: {', '.join(details['parameters'])}")
    print(f"  Features: {', '.join(details['unique_features'])}")

print("\n" + "=" * 60)
print("DIFFERENT SERIALIZATION APPROACHES:")
print("=" * 60)
print("1. Statistical Summary - Aggregated metrics with custom calculations")
print("2. Time-Series - Sequential data with computed indicators")
print("3. Matrix/Heatmap - Correlation data in matrix format")
print("4. Hierarchical/Nested - Multi-level order book structure")
print(
    "\nEach endpoint uses a completely different data structure and serialization approach!"
)
