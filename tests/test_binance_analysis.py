"""
Test cases for Binance Analysis Module

Tests the 4 different analysis methods with their distinct serialization formats:
1. Market Statistics - Statistical Summary Format
2. Technical Analysis - Time-Series Format
3. Correlation Analysis - Matrix/Heatmap Format
4. Liquidity Analysis - Hierarchical/Nested Format
"""

import pytest
from unittest.mock import Mock, patch
from app.core.binance_analysis import BinanceAnalyzer


class TestBinanceAnalyzer:
    """Test suite for BinanceAnalyzer class"""

    @pytest.fixture
    def analyzer(self):
        """Create a BinanceAnalyzer instance for testing"""
        with patch("app.core.binance_analysis.Spot") as mock_spot:
            analyzer = BinanceAnalyzer()
            analyzer.client = mock_spot.return_value
            return analyzer

    @pytest.fixture
    def mock_ticker_data(self):
        """Mock ticker data for testing"""
        return {
            "priceChange": "1000.50",
            "priceChangePercent": "1.05",
            "highPrice": "98000.00",
            "lowPrice": "95000.00",
            "volume": "1000.50",
        }

    @pytest.fixture
    def mock_klines_data(self):
        """Mock klines data for testing"""
        return [
            [
                1640995200000,
                "95000.00",
                "96000.00",
                "94000.00",
                "95500.00",
                "100.0",
                1640998800000,
                "9550000.00",
                1000,
                "50.0",
                "4775000.00",
                "0",
            ],
            [
                1640998800000,
                "95500.00",
                "97000.00",
                "95000.00",
                "96000.00",
                "120.0",
                1641002400000,
                "11520000.00",
                1200,
                "60.0",
                "5760000.00",
                "0",
            ],
            [
                1641002400000,
                "96000.00",
                "98000.00",
                "95500.00",
                "97000.00",
                "150.0",
                1641006000000,
                "14550000.00",
                1500,
                "75.0",
                "7275000.00",
                "0",
            ],
        ]

    def test_get_market_statistics_success(self, analyzer, mock_ticker_data):
        """Test successful market statistics retrieval"""
        # Mock the client response
        analyzer.client.ticker_24hr.return_value = mock_ticker_data

        # Call the method
        result = analyzer.get_market_statistics(["BTCUSDT"])

        # Assertions for Statistical Summary Format
        assert "metadata" in result
        assert "summary" in result
        assert "rankings" in result
        assert "market_analysis" in result

        # Check metadata structure
        assert result["metadata"]["symbols_processed"] == 1
        assert "timestamp" in result["metadata"]

        # Check summary statistics
        assert "total_symbols" in result["summary"]
        assert "avg_price_change_percent" in result["summary"]
        assert "avg_volatility" in result["summary"]

        # Check rankings structure
        assert "top_performers" in result["rankings"]
        assert "worst_performers" in result["rankings"]
        assert "most_volatile" in result["rankings"]

        # Check market analysis
        assert result["market_analysis"]["sentiment"] in ["bullish", "bearish"]
        assert "sentiment_strength" in result["market_analysis"]

    def test_get_market_statistics_no_symbols(self, analyzer):
        """Test market statistics with no valid symbols"""
        # Mock client to raise exception
        analyzer.client.ticker_24hr.side_effect = Exception("Symbol not found")

        result = analyzer.get_market_statistics(["INVALID"])

        assert "error" in result
        assert "No data available" in result["error"]

    def test_get_technical_analysis_success(self, analyzer, mock_klines_data):
        """Test successful technical analysis retrieval"""
        # Mock the client responses
        analyzer.client.klines.return_value = mock_klines_data
        analyzer.client.ticker_price.return_value = {"price": "97000.00"}

        # Call the method
        result = analyzer.get_technical_analysis("BTCUSDT")

        # Assertions for Time-Series Format
        assert "metadata" in result
        assert "current_state" in result
        assert "indicators" in result
        assert "trend_analysis" in result
        assert "time_series_data" in result

        # Check metadata structure
        assert result["metadata"]["symbol"] == "BTCUSDT"
        assert "timestamp" in result["metadata"]
        assert "data_points" in result["metadata"]

        # Check current state
        assert "latest_price" in result["current_state"]
        assert "volume" in result["current_state"]

        # Check indicators structure
        assert "moving_averages" in result["indicators"]
        assert "oscillators" in result["indicators"]
        assert "bollinger_bands" in result["indicators"]
        assert "macd" in result["indicators"]

        # Check trend analysis
        assert result["trend_analysis"]["short_term_trend"] in ["upward", "downward"]
        assert result["trend_analysis"]["long_term_trend"] in ["upward", "downward"]

        # Check time series data is a list
        assert isinstance(result["time_series_data"], list)
        if result["time_series_data"]:
            assert "timestamp" in result["time_series_data"][0]
            assert "close" in result["time_series_data"][0]

    def test_get_technical_analysis_error(self, analyzer):
        """Test technical analysis with API error"""
        # Mock client to raise exception
        analyzer.client.klines.side_effect = Exception("API Error")

        result = analyzer.get_technical_analysis("BTCUSDT")

        assert "error" in result
        assert "Failed to fetch technical analysis" in result["error"]

    def test_get_correlation_analysis_success(self, analyzer, mock_klines_data):
        """Test successful correlation analysis retrieval"""
        # Mock the client response
        analyzer.client.klines.return_value = mock_klines_data

        # Call the method with 2 symbols for correlation
        result = analyzer.get_correlation_analysis(["BTCUSDT", "ETHUSDT"])

        # Assertions for Matrix/Heatmap Format
        assert "metadata" in result
        assert "correlation_matrix" in result
        assert "correlation_rankings" in result
        assert "portfolio_metrics" in result
        assert "market_regime_analysis" in result

        # Check metadata structure
        assert result["metadata"]["analysis_period_days"] == 30
        assert "symbols_analyzed" in result["metadata"]
        assert "timestamp" in result["metadata"]

        # Check correlation matrix structure
        assert "raw_matrix" in result["correlation_matrix"]
        assert "matrix_size" in result["correlation_matrix"]
        assert "matrix_values" in result["correlation_matrix"]

        # Check rankings structure
        assert "highest_positive" in result["correlation_rankings"]
        assert "highest_negative" in result["correlation_rankings"]
        assert "most_extreme" in result["correlation_rankings"]

        # Check portfolio metrics
        assert "average_correlation" in result["portfolio_metrics"]
        assert "diversification_score" in result["portfolio_metrics"]

        # Check market regime analysis
        assert result["market_regime_analysis"]["regime"] in [
            "highly_correlated",
            "moderately_correlated",
            "diversified",
        ]

    def test_get_correlation_analysis_insufficient_data(self, analyzer):
        """Test correlation analysis with insufficient data"""
        # Mock client to raise exception for all symbols
        analyzer.client.klines.side_effect = Exception("No data")

        result = analyzer.get_correlation_analysis(["BTCUSDT"])

        assert "error" in result
        assert "Insufficient data" in result["error"]

    def test_get_liquidity_analysis_success(self, analyzer):
        """Test successful liquidity analysis retrieval"""
        # Mock the client responses
        mock_order_book = {
            "bids": [["96000.00", "10.0"], ["95900.00", "5.0"]],
            "asks": [["96100.00", "8.0"], ["96200.00", "12.0"]],
        }
        analyzer.client.depth.return_value = mock_order_book
        analyzer.client.ticker_price.return_value = {"price": "96050.00"}

        # Call the method
        result = analyzer.get_liquidity_analysis("BTCUSDT")

        # Assertions for Hierarchical/Nested Format
        assert "metadata" in result
        assert "spread_analysis" in result
        assert "order_book_depth" in result
        assert "liquidity_metrics" in result
        assert "price_impact_analysis" in result
        assert "market_microstructure" in result

        # Check metadata structure
        assert result["metadata"]["symbol"] == "BTCUSDT"
        assert "current_price" in result["metadata"]
        assert "timestamp" in result["metadata"]

        # Check spread analysis (nested structure)
        assert "best_bid" in result["spread_analysis"]
        assert "best_ask" in result["spread_analysis"]
        assert "spread" in result["spread_analysis"]
        assert "absolute" in result["spread_analysis"]["spread"]
        assert "percent" in result["spread_analysis"]["spread"]

        # Check order book depth (hierarchical structure)
        assert "bids" in result["order_book_depth"]
        assert "asks" in result["order_book_depth"]
        assert "total_volume" in result["order_book_depth"]["bids"]
        assert "depth_levels" in result["order_book_depth"]["bids"]

        # Check liquidity metrics
        assert "liquidity_score" in result["liquidity_metrics"]
        assert "market_imbalance" in result["liquidity_metrics"]
        assert result["liquidity_metrics"]["imbalance_direction"] in [
            "buy_pressure",
            "sell_pressure",
            "balanced",
        ]

        # Check price impact analysis (nested structure)
        assert isinstance(result["price_impact_analysis"], dict)

        # Check market microstructure
        assert "bid_ask_ratio" in result["market_microstructure"]
        assert result["market_microstructure"]["depth_asymmetry"] in [
            "bid_heavy",
            "ask_heavy",
            "balanced",
        ]

    def test_get_liquidity_analysis_error(self, analyzer):
        """Test liquidity analysis with API error"""
        # Mock client to raise exception
        analyzer.client.depth.side_effect = Exception("API Error")

        result = analyzer.get_liquidity_analysis("BTCUSDT")

        assert "error" in result
        assert "Failed to analyze liquidity" in result["error"]

    def test_different_serialization_formats(
        self, analyzer, mock_ticker_data, mock_klines_data
    ):
        """Test that each endpoint returns a distinctly different data structure"""
        # Mock all necessary client calls
        analyzer.client.ticker_24hr.return_value = mock_ticker_data
        analyzer.client.klines.return_value = mock_klines_data
        analyzer.client.ticker_price.return_value = {"price": "97000.00"}
        mock_order_book = {
            "bids": [["96000.00", "10.0"]],
            "asks": [["96100.00", "8.0"]],
        }
        analyzer.client.depth.return_value = mock_order_book

        # Get results from all endpoints
        stats_result = analyzer.get_market_statistics(["BTCUSDT"])
        tech_result = analyzer.get_technical_analysis("BTCUSDT")
        corr_result = analyzer.get_correlation_analysis(["BTCUSDT", "ETHUSDT"])
        liquidity_result = analyzer.get_liquidity_analysis("BTCUSDT")

        # Verify each has unique top-level keys (different serialization)
        stats_keys = set(stats_result.keys())
        tech_keys = set(tech_result.keys())
        corr_keys = set(corr_result.keys())
        liquidity_keys = set(liquidity_result.keys())

        # Each should have different primary structure
        assert "rankings" in stats_keys and "rankings" not in tech_keys
        assert "indicators" in tech_keys and "indicators" not in stats_keys
        assert (
            "correlation_matrix" in corr_keys and "correlation_matrix" not in tech_keys
        )
        assert (
            "spread_analysis" in liquidity_keys and "spread_analysis" not in corr_keys
        )

        # Verify different data organizations
        # Stats: Statistical summary format
        assert "market_analysis" in stats_result
        assert "sentiment" in stats_result["market_analysis"]

        # Tech: Time-series format
        assert "time_series_data" in tech_result
        assert isinstance(tech_result["time_series_data"], list)

        # Correlation: Matrix format
        assert "matrix_values" in corr_result["correlation_matrix"]
        assert isinstance(corr_result["correlation_matrix"]["matrix_values"], list)

        # Liquidity: Hierarchical/nested format
        assert "order_book_depth" in liquidity_result
        assert "bids" in liquidity_result["order_book_depth"]
        assert "depth_levels" in liquidity_result["order_book_depth"]["bids"]

    @pytest.mark.parametrize(
        "symbols,include_volume",
        [
            (["BTCUSDT"], True),
            (["BTCUSDT", "ETHUSDT"], False),
            (None, True),  # Should use default symbols
        ],
    )
    def test_get_market_statistics_parameters(
        self, analyzer, mock_ticker_data, symbols, include_volume
    ):
        """Test market statistics with different parameters"""
        analyzer.client.ticker_24hr.return_value = mock_ticker_data

        result = analyzer.get_market_statistics(
            symbols=symbols, include_volume=include_volume
        )

        assert result["metadata"]["include_volume"] == include_volume
        if include_volume:
            assert result["summary"]["total_volume"] is not None
        else:
            assert result["summary"]["total_volume"] is None

    @pytest.mark.parametrize(
        "interval,limit",
        [
            ("1h", 100),
            ("4h", 50),
            ("1d", 30),
        ],
    )
    def test_get_technical_analysis_parameters(
        self, analyzer, mock_klines_data, interval, limit
    ):
        """Test technical analysis with different parameters"""
        analyzer.client.klines.return_value = mock_klines_data

        result = analyzer.get_technical_analysis(
            "BTCUSDT", interval=interval, limit=limit
        )

        assert result["metadata"]["interval"] == interval
        # Verify client was called with correct parameters
        analyzer.client.klines.assert_called_with(
            symbol="BTCUSDT", interval=interval, limit=limit
        )

    @pytest.mark.parametrize(
        "days,include_clusters",
        [
            (30, True),
            (7, False),
            (60, True),
        ],
    )
    def test_get_correlation_analysis_parameters(
        self, analyzer, mock_klines_data, days, include_clusters
    ):
        """Test correlation analysis with different parameters"""
        analyzer.client.klines.return_value = mock_klines_data

        result = analyzer.get_correlation_analysis(
            ["BTCUSDT", "ETHUSDT"], days=days, include_clusters=include_clusters
        )

        assert result["metadata"]["analysis_period_days"] == days
        assert result["metadata"]["include_clusters"] == include_clusters

        if include_clusters:
            assert "risk_clusters" in result
        else:
            assert "risk_clusters" not in result

    @pytest.mark.parametrize(
        "depth_limit,include_levels",
        [
            (100, True),
            (50, False),
            (200, True),
        ],
    )
    def test_get_liquidity_analysis_parameters(
        self, analyzer, depth_limit, include_levels
    ):
        """Test liquidity analysis with different parameters"""
        mock_order_book = {
            "bids": [["96000.00", "10.0"]],
            "asks": [["96100.00", "8.0"]],
        }
        analyzer.client.depth.return_value = mock_order_book
        analyzer.client.ticker_price.return_value = {"price": "96050.00"}

        result = analyzer.get_liquidity_analysis(
            "BTCUSDT", depth_limit=depth_limit, include_levels=include_levels
        )

        assert result["metadata"]["depth_limit"] == depth_limit
        assert result["metadata"]["include_levels"] == include_levels

        # Verify client was called with correct depth limit
        analyzer.client.depth.assert_called_with(symbol="BTCUSDT", limit=depth_limit)
