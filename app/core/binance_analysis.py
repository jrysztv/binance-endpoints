"""
Binance Analysis Module

This module contains the business logic for analyzing Binance market data.
It provides 4 different types of analysis with distinct data structures:

1. Market Statistics - Aggregated ticker statistics with sentiment analysis
2. Technical Analysis - Time-series data with technical indicators
3. Correlation Analysis - Matrix-based correlation analysis
4. Liquidity Analysis - Hierarchical order book depth analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from binance.spot import Spot
import logging

# Configure logging
logger = logging.getLogger(__name__)


class BinanceAnalyzer:
    """Main analyzer class for Binance market data"""

    def __init__(self):
        """Initialize the Binance client (public endpoints only)"""
        self.client = Spot()
        logger.info("BinanceAnalyzer initialized successfully")

    def get_market_statistics(
        self, symbols: List[str] = None, include_volume: bool = True
    ) -> Dict:
        """
        ENDPOINT 1: Market Statistics with Statistical Summary Format

        Provides aggregated ticker statistics with custom volatility metrics,
        market sentiment analysis, and top performers ranking.

        Args:
            symbols: List of trading symbols (defaults to major cryptos)
            include_volume: Whether to include volume data in calculations

        Returns:
            Dict with statistical summary format including:
            - Aggregated market metrics
            - Top performers ranking
            - Market sentiment classification
            - Custom volatility calculations
        """
        if symbols is None:
            symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "XRPUSDT"]

        try:
            ticker_data = []

            for symbol in symbols:
                try:
                    ticker = self.client.ticker_24hr(symbol=symbol)

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
                    logger.warning(f"Failed to fetch ticker for {symbol}: {e}")
                    continue

            if not ticker_data:
                return {"error": "No data available for any symbols"}

            # Create DataFrame for analysis
            df = pd.DataFrame(ticker_data)

            # Custom statistical analysis
            total_volume = df["volume"].sum() if include_volume else 0

            stats = {
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "symbols_requested": symbols,
                    "symbols_processed": len(df),
                    "include_volume": include_volume,
                },
                "summary": {
                    "total_symbols": len(df),
                    "avg_price_change_percent": float(
                        df["price_change_percent"].mean()
                    ),
                    "avg_volatility": float(df["volatility"].mean()),
                    "max_volatility": float(df["volatility"].max()),
                    "min_volatility": float(df["volatility"].min()),
                    "total_volume": float(total_volume) if include_volume else None,
                },
                "rankings": {
                    "top_performers": df.nlargest(3, "price_change_percent")[
                        ["symbol", "price_change_percent"]
                    ].to_dict("records"),
                    "worst_performers": df.nsmallest(3, "price_change_percent")[
                        ["symbol", "price_change_percent"]
                    ].to_dict("records"),
                    "most_volatile": df.nlargest(3, "volatility")[
                        ["symbol", "volatility"]
                    ].to_dict("records"),
                },
                "market_analysis": {
                    "sentiment": "bullish"
                    if df["price_change_percent"].mean() > 0
                    else "bearish",
                    "sentiment_strength": abs(float(df["price_change_percent"].mean())),
                    "market_regime": "high_volatility"
                    if df["volatility"].mean() > 5
                    else "normal_volatility",
                    "uniformity": "uniform"
                    if df["price_change_percent"].std() < 2
                    else "divergent",
                },
            }

            return stats

        except Exception as e:
            logger.error(f"Error in get_market_statistics: {e}")
            return {"error": f"Failed to fetch market statistics: {str(e)}"}

    def get_technical_analysis(
        self, symbol: str, interval: str = "1h", limit: int = 100
    ) -> Dict:
        """
        ENDPOINT 2: Technical Analysis with Time-Series Format

        Provides historical candlestick data with computed technical indicators
        including moving averages, RSI, and Bollinger Bands.

        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            interval: Time interval for candlesticks
            limit: Number of data points to retrieve

        Returns:
            Dict with time-series format including:
            - Historical price data
            - Technical indicators (SMA, RSI, Bollinger Bands)
            - Trend classification
            - Time-series data points
        """
        try:
            # Get candlestick data
            klines = self.client.klines(symbol=symbol, interval=interval, limit=limit)

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

            # MACD
            exp1 = df["close"].ewm(span=12).mean()
            exp2 = df["close"].ewm(span=26).mean()
            df["macd"] = exp1 - exp2
            df["macd_signal"] = df["macd"].ewm(span=9).mean()

            # Prepare response data
            latest_data = df.iloc[-1]

            response = {
                "metadata": {
                    "symbol": symbol,
                    "interval": interval,
                    "data_points": len(df),
                    "timestamp": datetime.now().isoformat(),
                },
                "current_state": {
                    "latest_price": float(latest_data["close"]),
                    "volume": float(latest_data["volume"]),
                    "price_change_24h": float(
                        (latest_data["close"] - df.iloc[-24]["close"])
                        / df.iloc[-24]["close"]
                        * 100
                    )
                    if len(df) >= 24
                    else None,
                },
                "indicators": {
                    "moving_averages": {
                        "sma_20": float(latest_data["sma_20"])
                        if not pd.isna(latest_data["sma_20"])
                        else None,
                        "sma_50": float(latest_data["sma_50"])
                        if not pd.isna(latest_data["sma_50"])
                        else None,
                    },
                    "oscillators": {
                        "rsi": float(latest_data["rsi"])
                        if not pd.isna(latest_data["rsi"])
                        else None,
                        "rsi_signal": "overbought"
                        if not pd.isna(latest_data["rsi"]) and latest_data["rsi"] > 70
                        else "oversold"
                        if not pd.isna(latest_data["rsi"]) and latest_data["rsi"] < 30
                        else "neutral",
                    },
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
                        "position": "above_upper"
                        if not pd.isna(latest_data["bb_upper"])
                        and latest_data["close"] > latest_data["bb_upper"]
                        else "below_lower"
                        if not pd.isna(latest_data["bb_lower"])
                        and latest_data["close"] < latest_data["bb_lower"]
                        else "within_bands",
                    },
                    "macd": {
                        "macd": float(latest_data["macd"])
                        if not pd.isna(latest_data["macd"])
                        else None,
                        "signal": float(latest_data["macd_signal"])
                        if not pd.isna(latest_data["macd_signal"])
                        else None,
                        "histogram": float(
                            latest_data["macd"] - latest_data["macd_signal"]
                        )
                        if not pd.isna(latest_data["macd"])
                        and not pd.isna(latest_data["macd_signal"])
                        else None,
                    },
                },
                "trend_analysis": {
                    "short_term_trend": "upward"
                    if not pd.isna(latest_data["sma_20"])
                    and latest_data["close"] > latest_data["sma_20"]
                    else "downward",
                    "long_term_trend": "upward"
                    if not pd.isna(latest_data["sma_50"])
                    and latest_data["close"] > latest_data["sma_50"]
                    else "downward",
                    "volatility_regime": "high"
                    if not pd.isna(latest_data["bb_upper"])
                    and (
                        latest_data["close"] > latest_data["bb_upper"]
                        or latest_data["close"] < latest_data["bb_lower"]
                    )
                    else "normal",
                },
                "time_series_data": [
                    {
                        "timestamp": row["datetime"].isoformat(),
                        "close": float(row["close"]),
                        "volume": float(row["volume"]),
                        "sma_20": float(row["sma_20"])
                        if not pd.isna(row["sma_20"])
                        else None,
                        "rsi": float(row["rsi"]) if not pd.isna(row["rsi"]) else None,
                    }
                    for _, row in df.tail(20).iterrows()
                ],
            }

            return response

        except Exception as e:
            logger.error(f"Error in get_technical_analysis: {e}")
            return {"error": f"Failed to fetch technical analysis: {str(e)}"}

    def get_correlation_analysis(
        self, symbols: List[str] = None, days: int = 30, include_clusters: bool = True
    ) -> Dict:
        """
        ENDPOINT 3: Correlation Analysis with Matrix/Heatmap Format

        Analyzes correlations between multiple cryptocurrencies with portfolio
        metrics and risk clustering analysis.

        Args:
            symbols: List of symbols to analyze
            days: Number of days of historical data
            include_clusters: Whether to include clustering analysis

        Returns:
            Dict with matrix format including:
            - Correlation matrix data
            - Portfolio diversification metrics
            - Risk clustering information
            - Market regime classification
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
            successful_symbols = []

            for symbol in symbols:
                try:
                    # Get daily candlestick data
                    klines = self.client.klines(
                        symbol=symbol, interval="1d", limit=days
                    )
                    prices = [float(kline[4]) for kline in klines]  # closing prices
                    price_data[symbol.replace("USDT", "")] = prices
                    successful_symbols.append(symbol)
                except Exception as e:
                    logger.warning(f"Could not fetch data for {symbol}: {e}")
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
                            "asset_1": correlation_matrix.columns[i],
                            "asset_2": correlation_matrix.columns[j],
                            "correlation": float(correlation_matrix.iloc[i, j]),
                        }
                    )

            corr_pairs.sort(key=lambda x: abs(x["correlation"]), reverse=True)

            # Portfolio metrics
            avg_correlation = correlation_matrix.mean().mean()

            # Risk clustering (if requested)
            clusters = {}
            if include_clusters:
                clusters = {
                    "high_correlation_cluster": [
                        p for p in corr_pairs if p["correlation"] > 0.8
                    ],
                    "moderate_correlation_cluster": [
                        p for p in corr_pairs if 0.5 <= p["correlation"] <= 0.8
                    ],
                    "low_correlation_cluster": [
                        p for p in corr_pairs if 0.0 <= p["correlation"] < 0.5
                    ],
                    "negative_correlation_cluster": [
                        p for p in corr_pairs if p["correlation"] < 0.0
                    ],
                }

            response = {
                "metadata": {
                    "analysis_period_days": days,
                    "symbols_requested": symbols,
                    "symbols_analyzed": list(df.columns),
                    "successful_symbols": successful_symbols,
                    "timestamp": datetime.now().isoformat(),
                    "include_clusters": include_clusters,
                },
                "correlation_matrix": {
                    "raw_matrix": correlation_matrix.round(4).to_dict(),
                    "matrix_size": f"{len(correlation_matrix)}x{len(correlation_matrix)}",
                    "matrix_values": [
                        {
                            "row_asset": correlation_matrix.index[i],
                            "col_asset": correlation_matrix.columns[j],
                            "correlation": float(correlation_matrix.iloc[i, j]),
                        }
                        for i in range(len(correlation_matrix.index))
                        for j in range(len(correlation_matrix.columns))
                    ],
                },
                "correlation_rankings": {
                    "highest_positive": [p for p in corr_pairs if p["correlation"] > 0][
                        :5
                    ],
                    "highest_negative": [p for p in corr_pairs if p["correlation"] < 0][
                        -5:
                    ],
                    "most_extreme": corr_pairs[:5],  # Highest absolute values
                },
                "portfolio_metrics": {
                    "average_correlation": float(avg_correlation),
                    "diversification_score": float(
                        1 - avg_correlation
                    ),  # Higher is more diversified
                    "max_correlation": float(correlation_matrix.max().max()),
                    "min_correlation": float(correlation_matrix.min().min()),
                    "correlation_std": float(correlation_matrix.stack().std()),
                },
                "market_regime_analysis": {
                    "regime": "highly_correlated"
                    if avg_correlation > 0.8
                    else "moderately_correlated"
                    if avg_correlation > 0.5
                    else "diversified",
                    "diversification_quality": "poor"
                    if avg_correlation > 0.8
                    else "moderate"
                    if avg_correlation > 0.5
                    else "good",
                    "systemic_risk": "high"
                    if avg_correlation > 0.7
                    else "moderate"
                    if avg_correlation > 0.4
                    else "low",
                },
            }

            if include_clusters:
                response["risk_clusters"] = clusters

            return response

        except Exception as e:
            logger.error(f"Error in get_correlation_analysis: {e}")
            return {"error": f"Failed to perform correlation analysis: {str(e)}"}

    def get_liquidity_analysis(
        self, symbol: str, depth_limit: int = 100, include_levels: bool = True
    ) -> Dict:
        """
        ENDPOINT 4: Liquidity Analysis with Hierarchical/Nested Format

        Analyzes order book depth and liquidity metrics with nested structure
        for bid/ask analysis and market microstructure.

        Args:
            symbol: Trading symbol to analyze
            depth_limit: Number of order book levels to retrieve
            include_levels: Whether to include detailed level data

        Returns:
            Dict with hierarchical structure including:
            - Bid/ask spread analysis
            - Order book depth levels
            - Liquidity scoring
            - Market imbalance detection
        """
        try:
            # Get order book data
            order_book = self.client.depth(symbol=symbol, limit=depth_limit)

            # Get current ticker for reference price
            ticker = self.client.ticker_price(symbol=symbol)
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
                    return {
                        "total_volume": 0,
                        "weighted_avg_price": 0,
                        "depth_levels": [],
                        "volume_distribution": {},
                    }

                total_volume = sum(qty for price, qty in orders)
                weighted_price = (
                    sum(price * qty for price, qty in orders) / total_volume
                    if total_volume > 0
                    else 0
                )

                # Volume distribution analysis
                volume_buckets = {"0-1%": 0, "1-2%": 0, "2-5%": 0, "5%+": 0}

                # Group by price ranges (depth levels)
                depth_levels = []
                cumulative_volume = 0

                for i, (price, qty) in enumerate(
                    orders[:20] if include_levels else orders[:5]
                ):
                    cumulative_volume += qty
                    price_distance = abs(price - current_price) / current_price * 100

                    # Categorize into volume buckets
                    if price_distance <= 1:
                        volume_buckets["0-1%"] += qty
                    elif price_distance <= 2:
                        volume_buckets["1-2%"] += qty
                    elif price_distance <= 5:
                        volume_buckets["2-5%"] += qty
                    else:
                        volume_buckets["5%+"] += qty

                    if include_levels:
                        depth_levels.append(
                            {
                                "level": i + 1,
                                "price": price,
                                "quantity": qty,
                                "cumulative_volume": cumulative_volume,
                                "price_distance_percent": price_distance,
                                "value_usd": price * qty,
                            }
                        )

                return {
                    "total_volume": total_volume,
                    "weighted_avg_price": weighted_price,
                    "depth_levels": depth_levels,
                    "volume_distribution": volume_buckets,
                    "concentration_ratio": volume_buckets["0-1%"] / total_volume
                    if total_volume > 0
                    else 0,
                }

            bid_metrics = calculate_depth_metrics(bids, True)
            ask_metrics = calculate_depth_metrics(asks, False)

            # Calculate advanced liquidity metrics
            total_liquidity = bid_metrics["total_volume"] + ask_metrics["total_volume"]
            liquidity_score = min(100, total_liquidity / 1000)  # Normalized score

            # Market microstructure analysis
            if total_liquidity > 0:
                imbalance = (
                    bid_metrics["total_volume"] - ask_metrics["total_volume"]
                ) / total_liquidity
            else:
                imbalance = 0

            # Price impact estimation (simplified)
            def estimate_price_impact(volume_target, orders, is_buy=True):
                cumulative_volume = 0
                total_cost = 0

                for price, qty in orders:
                    if cumulative_volume >= volume_target:
                        break

                    volume_to_take = min(qty, volume_target - cumulative_volume)
                    total_cost += price * volume_to_take
                    cumulative_volume += volume_to_take

                if cumulative_volume > 0:
                    avg_price = total_cost / cumulative_volume
                    impact = abs(avg_price - current_price) / current_price * 100
                    return {"avg_price": avg_price, "impact_percent": impact}

                return {"avg_price": None, "impact_percent": None}

            # Calculate price impact for different trade sizes
            trade_sizes = [100, 1000, 10000]  # Volume in base currency
            price_impact_analysis = {}

            for size in trade_sizes:
                price_impact_analysis[f"volume_{size}"] = {
                    "buy_impact": estimate_price_impact(size, asks, True),
                    "sell_impact": estimate_price_impact(size, bids, False),
                }

            response = {
                "metadata": {
                    "symbol": symbol,
                    "timestamp": datetime.now().isoformat(),
                    "depth_limit": depth_limit,
                    "include_levels": include_levels,
                    "current_price": current_price,
                },
                "spread_analysis": {
                    "best_bid": best_bid,
                    "best_ask": best_ask,
                    "spread": {
                        "absolute": spread,
                        "percent": spread_percent,
                        "classification": "tight"
                        if spread_percent < 0.05
                        else "normal"
                        if spread_percent < 0.1
                        else "wide",
                    },
                    "midpoint": (best_bid + best_ask) / 2
                    if best_bid > 0 and best_ask > 0
                    else current_price,
                },
                "order_book_depth": {
                    "bids": {**bid_metrics, "side": "buy", "price_levels": len(bids)},
                    "asks": {**ask_metrics, "side": "sell", "price_levels": len(asks)},
                    "total_liquidity": total_liquidity,
                    "book_balance": bid_metrics["total_volume"] / total_liquidity
                    if total_liquidity > 0
                    else 0.5,
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
                    else "fair"
                    if liquidity_score > 20
                    else "poor",
                    "concentration_risk": {
                        "bid_concentration": bid_metrics.get("concentration_ratio", 0),
                        "ask_concentration": ask_metrics.get("concentration_ratio", 0),
                        "overall_risk": "high"
                        if max(
                            bid_metrics.get("concentration_ratio", 0),
                            ask_metrics.get("concentration_ratio", 0),
                        )
                        > 0.7
                        else "moderate",
                    },
                },
                "price_impact_analysis": price_impact_analysis,
                "market_microstructure": {
                    "bid_ask_ratio": bid_metrics["total_volume"]
                    / ask_metrics["total_volume"]
                    if ask_metrics["total_volume"] > 0
                    else float("inf"),
                    "depth_asymmetry": "bid_heavy"
                    if bid_metrics["total_volume"] > ask_metrics["total_volume"] * 1.2
                    else "ask_heavy"
                    if ask_metrics["total_volume"] > bid_metrics["total_volume"] * 1.2
                    else "balanced",
                    "market_state": "liquid" if total_liquidity > 1000 else "thin",
                },
            }

            return response

        except Exception as e:
            logger.error(f"Error in get_liquidity_analysis: {e}")
            return {"error": f"Failed to analyze liquidity: {str(e)}"}
