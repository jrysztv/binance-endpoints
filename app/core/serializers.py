"""
Data Serializers for Different Output Formats

This module provides serializers for converting Binance analysis data
into different formats: JSON, CSV, HTML, and XML.

Each serializer implements a different approach to data representation:
1. JSON - Standard API response format
2. CSV - Tabular data export format
3. HTML - Human-readable report format
4. XML - Structured markup format
"""

import json
import csv
import io
import xml.etree.ElementTree as ET
from typing import Dict, Any, List
from datetime import datetime
import pandas as pd
from jinja2 import Template


class BaseSerializer:
    """Base serializer class"""

    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.timestamp = datetime.now().isoformat()

    def serialize(self) -> str:
        """Serialize data to string format"""
        raise NotImplementedError("Subclasses must implement serialize method")

    def get_content_type(self) -> str:
        """Return the appropriate Content-Type header"""
        raise NotImplementedError("Subclasses must implement get_content_type method")


class JSONSerializer(BaseSerializer):
    """JSON serializer - Standard API response format"""

    def serialize(self) -> str:
        """Serialize to JSON format"""
        return json.dumps(self.data, indent=2, ensure_ascii=False)

    def get_content_type(self) -> str:
        return "application/json"


class CSVSerializer(BaseSerializer):
    """CSV serializer - Tabular data export format"""

    def serialize(self) -> str:
        """Serialize to CSV format"""
        output = io.StringIO()

        # Handle different data structures
        if "summary" in self.data:  # Market Statistics
            return self._serialize_market_stats_csv()
        elif "time_series_data" in self.data:  # Technical Analysis
            return self._serialize_technical_csv()
        elif "correlation_matrix" in self.data:  # Correlation Analysis
            return self._serialize_correlation_csv()
        elif "order_book_depth" in self.data:  # Liquidity Analysis
            return self._serialize_liquidity_csv()
        else:
            # Generic CSV for unknown structure
            return self._serialize_generic_csv()

    def _serialize_market_stats_csv(self) -> str:
        """Serialize market statistics to CSV"""
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(["metric", "value"])

        # Summary data
        if "summary" in self.data:
            for key, value in self.data["summary"].items():
                writer.writerow([f"summary_{key}", value])

        # Top performers
        if "rankings" in self.data and "top_performers" in self.data["rankings"]:
            writer.writerow(["--- top_performers ---", ""])
            writer.writerow(["symbol", "price_change_percent"])
            for performer in self.data["rankings"]["top_performers"]:
                writer.writerow(
                    [
                        performer.get("symbol", ""),
                        performer.get("price_change_percent", ""),
                    ]
                )

        return output.getvalue()

    def _serialize_technical_csv(self) -> str:
        """Serialize technical analysis to CSV"""
        output = io.StringIO()
        writer = csv.writer(output)

        # Time series data
        if "time_series_data" in self.data:
            if self.data["time_series_data"]:
                # Header from first row keys
                headers = list(self.data["time_series_data"][0].keys())
                writer.writerow(headers)

                # Data rows
                for row in self.data["time_series_data"]:
                    writer.writerow([row.get(h, "") for h in headers])

        return output.getvalue()

    def _serialize_correlation_csv(self) -> str:
        """Serialize correlation analysis to CSV"""
        output = io.StringIO()
        writer = csv.writer(output)

        # Correlation matrix
        if (
            "correlation_matrix" in self.data
            and "raw_matrix" in self.data["correlation_matrix"]
        ):
            matrix = self.data["correlation_matrix"]["raw_matrix"]

            # Header
            symbols = list(matrix.keys())
            writer.writerow(["symbol"] + symbols)

            # Matrix rows
            for symbol in symbols:
                row = [symbol]
                for other_symbol in symbols:
                    row.append(matrix[symbol].get(other_symbol, ""))
                writer.writerow(row)

        return output.getvalue()

    def _serialize_liquidity_csv(self) -> str:
        """Serialize liquidity analysis to CSV"""
        output = io.StringIO()
        writer = csv.writer(output)

        # Order book depth levels
        writer.writerow(["side", "level", "price", "quantity", "cumulative_volume"])

        if "order_book_depth" in self.data:
            # Bids
            bids = self.data["order_book_depth"].get("bids", {})
            if "depth_levels" in bids:
                for level in bids["depth_levels"]:
                    writer.writerow(
                        [
                            "bid",
                            level.get("level", ""),
                            level.get("price", ""),
                            level.get("quantity", ""),
                            level.get("cumulative_volume", ""),
                        ]
                    )

            # Asks
            asks = self.data["order_book_depth"].get("asks", {})
            if "depth_levels" in asks:
                for level in asks["depth_levels"]:
                    writer.writerow(
                        [
                            "ask",
                            level.get("level", ""),
                            level.get("price", ""),
                            level.get("quantity", ""),
                            level.get("cumulative_volume", ""),
                        ]
                    )

        return output.getvalue()

    def _serialize_generic_csv(self) -> str:
        """Generic CSV serialization for unknown data structures"""
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["key", "value"])

        def flatten_dict(d, prefix=""):
            for key, value in d.items():
                full_key = f"{prefix}_{key}" if prefix else key
                if isinstance(value, dict):
                    yield from flatten_dict(value, full_key)
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            yield from flatten_dict(item, f"{full_key}_{i}")
                        else:
                            writer.writerow([f"{full_key}_{i}", item])
                else:
                    writer.writerow([full_key, value])

        list(flatten_dict(self.data))
        return output.getvalue()

    def get_content_type(self) -> str:
        return "text/csv"


class HTMLSerializer(BaseSerializer):
    """HTML serializer - Human-readable report format"""

    def serialize(self) -> str:
        """Serialize to HTML format"""
        if "summary" in self.data:  # Market Statistics
            return self._serialize_market_stats_html()
        elif "time_series_data" in self.data:  # Technical Analysis
            return self._serialize_technical_html()
        elif "correlation_matrix" in self.data:  # Correlation Analysis
            return self._serialize_correlation_html()
        elif "order_book_depth" in self.data:  # Liquidity Analysis
            return self._serialize_liquidity_html()
        else:
            return self._serialize_generic_html()

    def _serialize_market_stats_html(self) -> str:
        """Serialize market statistics to HTML"""
        template = Template("""
<!DOCTYPE html>
<html>
<head>
    <title>Market Statistics Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { background: #f4f4f4; padding: 20px; border-radius: 5px; }
        .summary { background: #e8f5e8; padding: 15px; margin: 20px 0; border-radius: 5px; }
        .rankings { background: #fff3cd; padding: 15px; margin: 20px 0; border-radius: 5px; }
        .sentiment { background: #d4edda; padding: 15px; margin: 20px 0; border-radius: 5px; }
        table { border-collapse: collapse; width: 100%; margin: 10px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .positive { color: green; font-weight: bold; }
        .negative { color: red; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Binance Market Statistics Report</h1>
        <p><strong>Generated:</strong> {{ timestamp }}</p>
        <p><strong>Symbols Analyzed:</strong> {{ metadata.symbols_processed }}</p>
    </div>
    
    <div class="summary">
        <h2>📈 Market Summary</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Total Symbols</td><td>{{ summary.total_symbols }}</td></tr>
            <tr><td>Average Price Change</td><td class="{{ 'positive' if summary.avg_price_change_percent > 0 else 'negative' }}">{{ "%.2f"|format(summary.avg_price_change_percent) }}%</td></tr>
            <tr><td>Average Volatility</td><td>{{ "%.2f"|format(summary.avg_volatility) }}%</td></tr>
            {% if summary.total_volume %}
            <tr><td>Total Volume</td><td>{{ "{:,.0f}"|format(summary.total_volume) }}</td></tr>
            {% endif %}
        </table>
    </div>
    
    <div class="rankings">
        <h2>🏆 Top Performers</h2>
        <table>
            <tr><th>Symbol</th><th>Price Change %</th></tr>
            {% for performer in rankings.top_performers %}
            <tr>
                <td>{{ performer.symbol }}</td>
                <td class="{{ 'positive' if performer.price_change_percent > 0 else 'negative' }}">{{ "%.3f"|format(performer.price_change_percent) }}%</td>
            </tr>
            {% endfor %}
        </table>
    </div>
    
    <div class="sentiment">
        <h2>🎯 Market Analysis</h2>
        <p><strong>Market Sentiment:</strong> <span class="{{ 'positive' if market_analysis.sentiment == 'bullish' else 'negative' }}">{{ market_analysis.sentiment|upper }}</span></p>
        <p><strong>Sentiment Strength:</strong> {{ "%.2f"|format(market_analysis.sentiment_strength) }}%</p>
        <p><strong>Market Regime:</strong> {{ market_analysis.market_regime|replace('_', ' ')|title }}</p>
        <p><strong>Market Uniformity:</strong> {{ market_analysis.uniformity|title }}</p>
    </div>
</body>
</html>
        """)

        return template.render(**self.data, timestamp=self.timestamp)

    def _serialize_technical_html(self) -> str:
        """Serialize technical analysis to HTML"""
        template = Template("""
<!DOCTYPE html>
<html>
<head>
    <title>Technical Analysis Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { background: #f4f4f4; padding: 20px; border-radius: 5px; }
        .current { background: #e3f2fd; padding: 15px; margin: 20px 0; border-radius: 5px; }
        .indicators { background: #f3e5f5; padding: 15px; margin: 20px 0; border-radius: 5px; }
        .trend { background: #fff3e0; padding: 15px; margin: 20px 0; border-radius: 5px; }
        table { border-collapse: collapse; width: 100%; margin: 10px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .upward { color: green; font-weight: bold; }
        .downward { color: red; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📈 Technical Analysis Report</h1>
        <p><strong>Symbol:</strong> {{ metadata.symbol }}</p>
        <p><strong>Interval:</strong> {{ metadata.interval }}</p>
        <p><strong>Generated:</strong> {{ timestamp }}</p>
    </div>
    
    <div class="current">
        <h2>💰 Current State</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Latest Price</td><td>${{ "{:,.2f}"|format(current_state.latest_price) }}</td></tr>
            <tr><td>Volume</td><td>{{ "{:,.0f}"|format(current_state.volume) }}</td></tr>
            {% if current_state.price_change_24h %}
            <tr><td>24h Change</td><td class="{{ 'upward' if current_state.price_change_24h > 0 else 'downward' }}">{{ "%.2f"|format(current_state.price_change_24h) }}%</td></tr>
            {% endif %}
        </table>
    </div>
    
    <div class="indicators">
        <h2>📊 Technical Indicators</h2>
        <h3>Moving Averages</h3>
        <table>
            <tr><th>Indicator</th><th>Value</th></tr>
            {% if indicators.moving_averages.sma_20 %}
            <tr><td>SMA 20</td><td>${{ "{:,.2f}"|format(indicators.moving_averages.sma_20) }}</td></tr>
            {% endif %}
            {% if indicators.moving_averages.sma_50 %}
            <tr><td>SMA 50</td><td>${{ "{:,.2f}"|format(indicators.moving_averages.sma_50) }}</td></tr>
            {% endif %}
        </table>
        
        <h3>Oscillators</h3>
        <table>
            <tr><th>Indicator</th><th>Value</th><th>Signal</th></tr>
            {% if indicators.oscillators.rsi %}
            <tr><td>RSI</td><td>{{ "%.2f"|format(indicators.oscillators.rsi) }}</td><td>{{ indicators.oscillators.rsi_signal|title }}</td></tr>
            {% endif %}
        </table>
    </div>
    
    <div class="trend">
        <h2>📈 Trend Analysis</h2>
        <p><strong>Short-term Trend:</strong> <span class="{{ trend_analysis.short_term_trend }}">{{ trend_analysis.short_term_trend|title }}</span></p>
        <p><strong>Long-term Trend:</strong> <span class="{{ trend_analysis.long_term_trend }}">{{ trend_analysis.long_term_trend|title }}</span></p>
        <p><strong>Volatility Regime:</strong> {{ trend_analysis.volatility_regime|title }}</p>
    </div>
</body>
</html>
        """)

        return template.render(**self.data, timestamp=self.timestamp)

    def _serialize_correlation_html(self) -> str:
        """Serialize correlation analysis to HTML"""
        template = Template("""
<!DOCTYPE html>
<html>
<head>
    <title>Correlation Analysis Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { background: #f4f4f4; padding: 20px; border-radius: 5px; }
        .matrix { background: #f8f9fa; padding: 15px; margin: 20px 0; border-radius: 5px; }
        .metrics { background: #e8f5e8; padding: 15px; margin: 20px 0; border-radius: 5px; }
        table { border-collapse: collapse; width: 100%; margin: 10px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
        th { background-color: #f2f2f2; }
        .high-corr { background-color: #ffcccc; }
        .medium-corr { background-color: #ffffcc; }
        .low-corr { background-color: #ccffcc; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔗 Correlation Analysis Report</h1>
        <p><strong>Analysis Period:</strong> {{ metadata.analysis_period_days }} days</p>
        <p><strong>Symbols:</strong> {{ metadata.symbols_analyzed|join(', ') }}</p>
        <p><strong>Generated:</strong> {{ timestamp }}</p>
    </div>
    
    <div class="matrix">
        <h2>📊 Correlation Matrix</h2>
        <table>
            <tr>
                <th>Asset</th>
                {% for symbol in metadata.symbols_analyzed %}
                <th>{{ symbol }}</th>
                {% endfor %}
            </tr>
            {% for row_symbol in metadata.symbols_analyzed %}
            <tr>
                <th>{{ row_symbol }}</th>
                {% for col_symbol in metadata.symbols_analyzed %}
                {% set corr_val = correlation_matrix.raw_matrix[row_symbol][col_symbol] %}
                <td class="{{ 'high-corr' if corr_val > 0.7 else 'medium-corr' if corr_val > 0.3 else 'low-corr' }}">
                    {{ "%.3f"|format(corr_val) }}
                </td>
                {% endfor %}
            </tr>
            {% endfor %}
        </table>
    </div>
    
    <div class="metrics">
        <h2>📈 Portfolio Metrics</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Average Correlation</td><td>{{ "%.4f"|format(portfolio_metrics.average_correlation) }}</td></tr>
            <tr><td>Diversification Score</td><td>{{ "%.4f"|format(portfolio_metrics.diversification_score) }}</td></tr>
            <tr><td>Market Regime</td><td>{{ market_regime_analysis.regime|replace('_', ' ')|title }}</td></tr>
            <tr><td>Systemic Risk</td><td>{{ market_regime_analysis.systemic_risk|title }}</td></tr>
        </table>
    </div>
</body>
</html>
        """)

        return template.render(**self.data, timestamp=self.timestamp)

    def _serialize_liquidity_html(self) -> str:
        """Serialize liquidity analysis to HTML"""
        template = Template("""
<!DOCTYPE html>
<html>
<head>
    <title>Liquidity Analysis Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { background: #f4f4f4; padding: 20px; border-radius: 5px; }
        .spread { background: #e3f2fd; padding: 15px; margin: 20px 0; border-radius: 5px; }
        .metrics { background: #f3e5f5; padding: 15px; margin: 20px 0; border-radius: 5px; }
        table { border-collapse: collapse; width: 100%; margin: 10px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .excellent { color: green; font-weight: bold; }
        .good { color: orange; font-weight: bold; }
        .poor { color: red; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>💧 Liquidity Analysis Report</h1>
        <p><strong>Symbol:</strong> {{ metadata.symbol }}</p>
        <p><strong>Current Price:</strong> ${{ "{:,.2f}"|format(metadata.current_price) }}</p>
        <p><strong>Generated:</strong> {{ timestamp }}</p>
    </div>
    
    <div class="spread">
        <h2>📊 Spread Analysis</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Best Bid</td><td>${{ "{:,.2f}"|format(spread_analysis.best_bid) }}</td></tr>
            <tr><td>Best Ask</td><td>${{ "{:,.2f}"|format(spread_analysis.best_ask) }}</td></tr>
            <tr><td>Spread</td><td>${{ "%.2f"|format(spread_analysis.spread.absolute) }} ({{ "%.4f"|format(spread_analysis.spread.percent) }}%)</td></tr>
            <tr><td>Classification</td><td>{{ spread_analysis.spread.classification|title }}</td></tr>
        </table>
    </div>
    
    <div class="metrics">
        <h2>🎯 Liquidity Metrics</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Liquidity Score</td><td>{{ "%.2f"|format(liquidity_metrics.liquidity_score) }}/100</td></tr>
            <tr><td>Market Quality</td><td class="{{ liquidity_metrics.market_quality }}">{{ liquidity_metrics.market_quality|title }}</td></tr>
            <tr><td>Market Imbalance</td><td>{{ "%.4f"|format(liquidity_metrics.market_imbalance) }}</td></tr>
            <tr><td>Imbalance Direction</td><td>{{ liquidity_metrics.imbalance_direction|replace('_', ' ')|title }}</td></tr>
        </table>
        
        <h3>Order Book Summary</h3>
        <table>
            <tr><th>Side</th><th>Total Volume</th><th>Price Levels</th></tr>
            <tr><td>Bids</td><td>{{ "{:,.0f}"|format(order_book_depth.bids.total_volume) }}</td><td>{{ order_book_depth.bids.price_levels }}</td></tr>
            <tr><td>Asks</td><td>{{ "{:,.0f}"|format(order_book_depth.asks.total_volume) }}</td><td>{{ order_book_depth.asks.price_levels }}</td></tr>
        </table>
    </div>
</body>
</html>
        """)

        return template.render(**self.data, timestamp=self.timestamp)

    def _serialize_generic_html(self) -> str:
        """Generic HTML serialization"""
        template = Template("""
<!DOCTYPE html>
<html>
<head>
    <title>Binance Data Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .data { background: #f8f9fa; padding: 15px; margin: 20px 0; border-radius: 5px; }
        pre { background: #f4f4f4; padding: 10px; border-radius: 3px; overflow-x: auto; }
    </style>
</head>
<body>
    <h1>📊 Binance Data Report</h1>
    <p><strong>Generated:</strong> {{ timestamp }}</p>
    <div class="data">
        <pre>{{ data_json }}</pre>
    </div>
</body>
</html>
        """)

        return template.render(
            timestamp=self.timestamp, data_json=json.dumps(self.data, indent=2)
        )

    def get_content_type(self) -> str:
        return "text/html"


class XMLSerializer(BaseSerializer):
    """XML serializer - Structured markup format"""

    def serialize(self) -> str:
        """Serialize to XML format"""
        root = ET.Element("binance_data")
        root.set("timestamp", self.timestamp)

        # Convert dictionary to XML recursively
        self._dict_to_xml(self.data, root)

        # Create tree and return string
        tree = ET.ElementTree(root)
        xml_str = io.StringIO()
        tree.write(xml_str, encoding="unicode", xml_declaration=True)
        return xml_str.getvalue()

    def _dict_to_xml(self, data: Any, parent: ET.Element, key: str = None):
        """Convert dictionary to XML elements recursively"""
        if isinstance(data, dict):
            for k, v in data.items():
                # Clean key names for valid XML
                clean_key = (
                    str(k).replace(" ", "_").replace("%", "percent").replace("-", "_")
                )
                # Always create a sub-element for dictionary items
                element = ET.SubElement(parent, clean_key)
                self._dict_to_xml(v, element, clean_key)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, dict):
                    list_element = ET.SubElement(parent, "item")
                    list_element.set("index", str(i))
                    self._dict_to_xml(item, list_element)
                else:
                    list_element = ET.SubElement(parent, "item")
                    list_element.set("index", str(i))
                    list_element.text = str(item)
        else:
            parent.text = str(data) if data is not None else ""

    def get_content_type(self) -> str:
        return "application/xml"


class ChartSerializer(BaseSerializer):
    """Chart serializer - Visual data representation using matplotlib"""

    def __init__(self, data: Dict[str, Any], chart_type: str = "auto"):
        super().__init__(data)
        self.chart_type = chart_type

    def serialize(self) -> bytes:
        """Serialize to PNG chart format"""
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        from datetime import datetime
        import base64

        plt.style.use("seaborn-v0_8")
        fig, ax = plt.subplots(figsize=(12, 8))

        if "time_series_data" in self.data:  # Technical Analysis Chart
            self._create_technical_chart(ax)
        elif "correlation_matrix" in self.data:  # Correlation Heatmap
            self._create_correlation_heatmap(ax)
        elif "rankings" in self.data:  # Market Statistics Chart
            self._create_market_stats_chart(ax)
        elif "order_book_depth" in self.data:  # Liquidity Chart
            self._create_liquidity_chart(ax)
        else:
            ax.text(
                0.5,
                0.5,
                "No chart available for this data type",
                ha="center",
                va="center",
                transform=ax.transAxes,
                fontsize=16,
            )

        plt.tight_layout()

        # Save to bytes
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format="png", dpi=150, bbox_inches="tight")
        img_buffer.seek(0)
        plt.close()

        return img_buffer.getvalue()

    def _create_technical_chart(self, ax):
        """Create technical analysis chart"""
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        from datetime import datetime

        time_series = self.data["time_series_data"]
        if not time_series:
            return

        dates = [
            datetime.fromisoformat(item["timestamp"].replace("Z", "+00:00"))
            for item in time_series
        ]
        prices = [item["close"] for item in time_series]
        sma_20 = [
            item.get("sma_20") for item in time_series if item.get("sma_20") is not None
        ]

        ax.plot(dates, prices, label="Close Price", linewidth=2, color="blue")

        if len(sma_20) > 0:
            sma_dates = dates[-len(sma_20) :]
            ax.plot(sma_dates, sma_20, label="SMA 20", alpha=0.7, color="orange")

        ax.set_title(
            f"{self.data.get('metadata', {}).get('symbol', 'Unknown')} - Technical Analysis",
            fontsize=16,
        )
        ax.set_xlabel("Time")
        ax.set_ylabel("Price (USDT)")
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

    def _create_correlation_heatmap(self, ax):
        """Create correlation matrix heatmap"""
        import numpy as np
        import matplotlib.pyplot as plt

        matrix = self.data["correlation_matrix"]["raw_matrix"]
        symbols = list(matrix.keys())

        # Convert to numpy array
        corr_array = np.array(
            [[matrix[row][col] for col in symbols] for row in symbols]
        )

        im = ax.imshow(corr_array, cmap="RdYlGn", aspect="auto", vmin=-1, vmax=1)

        # Set ticks and labels
        ax.set_xticks(range(len(symbols)))
        ax.set_yticks(range(len(symbols)))
        ax.set_xticklabels(symbols)
        ax.set_yticklabels(symbols)

        # Add correlation values to cells
        for i in range(len(symbols)):
            for j in range(len(symbols)):
                text = ax.text(
                    j,
                    i,
                    f"{corr_array[i, j]:.3f}",
                    ha="center",
                    va="center",
                    color="black",
                )

        ax.set_title("Cryptocurrency Correlation Matrix", fontsize=16)
        plt.colorbar(im, ax=ax, label="Correlation Coefficient")

    def _create_market_stats_chart(self, ax):
        """Create market statistics chart"""
        if "rankings" not in self.data or "top_performers" not in self.data["rankings"]:
            return

        performers = self.data["rankings"]["top_performers"]
        symbols = [p["symbol"].replace("USDT", "") for p in performers]
        changes = [p["price_change_percent"] for p in performers]

        colors = ["green" if change >= 0 else "red" for change in changes]

        bars = ax.bar(symbols, changes, color=colors, alpha=0.7)
        ax.set_title("Top Performing Cryptocurrencies (24h Change)", fontsize=16)
        ax.set_xlabel("Symbol")
        ax.set_ylabel("Price Change (%)")
        ax.grid(True, alpha=0.3, axis="y")

        # Add value labels on bars
        for bar, change in zip(bars, changes):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{change:.2f}%",
                ha="center",
                va="bottom" if change >= 0 else "top",
            )

    def _create_liquidity_chart(self, ax):
        """Create liquidity analysis chart"""
        order_book = self.data["order_book_depth"]

        # Get bid and ask data
        bids = order_book.get("bids", {}).get("depth_levels", [])
        asks = order_book.get("asks", {}).get("depth_levels", [])

        if not bids or not asks:
            ax.text(
                0.5,
                0.5,
                "Insufficient order book data",
                ha="center",
                va="center",
                transform=ax.transAxes,
                fontsize=16,
            )
            return

        # Plot bid and ask levels
        bid_prices = [level["price"] for level in bids[:10]]
        bid_volumes = [level["quantity"] for level in bids[:10]]
        ask_prices = [level["price"] for level in asks[:10]]
        ask_volumes = [level["quantity"] for level in asks[:10]]

        ax.barh(bid_prices, bid_volumes, alpha=0.7, color="green", label="Bids")
        ax.barh(
            ask_prices,
            [-vol for vol in ask_volumes],
            alpha=0.7,
            color="red",
            label="Asks",
        )

        ax.set_title(
            f"{self.data.get('metadata', {}).get('symbol', 'Unknown')} - Order Book Depth",
            fontsize=16,
        )
        ax.set_xlabel("Volume")
        ax.set_ylabel("Price (USDT)")
        ax.legend()
        ax.grid(True, alpha=0.3)

    def get_content_type(self) -> str:
        return "image/png"


# Factory function to get appropriate serializer
def get_serializer(data: Dict[str, Any], format_type: str) -> BaseSerializer:
    """Factory function to get the appropriate serializer"""
    serializers = {
        "json": JSONSerializer,
        "csv": CSVSerializer,
        "html": HTMLSerializer,
        "xml": XMLSerializer,
        "chart": ChartSerializer,
    }

    if format_type not in serializers:
        raise ValueError(f"Unsupported format: {format_type}")

    return serializers[format_type](data)
