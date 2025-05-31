"""
Test suite for serializers

Tests the core serialization functionality for different output formats.
"""

import pytest
import json
import xml.etree.ElementTree as ET
from app.core.serializers import (
    JSONSerializer,
    CSVSerializer,
    HTMLSerializer,
    XMLSerializer,
    ChartSerializer,
    get_serializer,
)


class TestJSONSerializer:
    """Test JSON serialization"""

    def test_json_serialization(self):
        """Test basic JSON serialization"""
        data = {"test": "value", "number": 123, "nested": {"key": "value"}}

        serializer = JSONSerializer(data)
        result = serializer.serialize()

        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed["test"] == "value"
        assert parsed["number"] == 123
        assert parsed["nested"]["key"] == "value"

    def test_json_content_type(self):
        """Test JSON content type"""
        serializer = JSONSerializer({"test": "data"})
        assert serializer.get_content_type() == "application/json"


class TestCSVSerializer:
    """Test CSV serialization"""

    def test_csv_market_stats(self):
        """Test CSV serialization for market statistics"""
        data = {
            "summary": {"total_symbols": 5, "avg_price_change_percent": 2.5},
            "rankings": {
                "top_performers": [{"symbol": "BTCUSDT", "price_change_percent": 5.0}]
            },
        }

        serializer = CSVSerializer(data)
        result = serializer.serialize()

        # Should contain headers and data
        assert "metric,value" in result
        assert "summary_total_symbols,5" in result
        assert "BTCUSDT,5.0" in result

    def test_csv_content_type(self):
        """Test CSV content type"""
        serializer = CSVSerializer({"test": "data"})
        assert serializer.get_content_type() == "text/csv"


class TestHTMLSerializer:
    """Test HTML serialization"""

    def test_html_market_stats(self):
        """Test HTML serialization for market statistics"""
        data = {
            "summary": {
                "total_symbols": 5,
                "avg_price_change_percent": 2.5,
                "avg_volatility": 10.0,
            },
            "rankings": {
                "top_performers": [{"symbol": "BTCUSDT", "price_change_percent": 5.0}]
            },
            "market_analysis": {
                "sentiment": "bullish",
                "sentiment_strength": 75.0,
                "market_regime": "trending_up",
                "uniformity": "high",
            },
            "metadata": {"symbols_processed": 5},
        }

        serializer = HTMLSerializer(data)
        result = serializer.serialize()

        # Should be valid HTML
        assert "<!DOCTYPE html>" in result
        assert "<title>Market Statistics Report</title>" in result
        assert "BTCUSDT" in result
        assert "5.00%" in result

    def test_html_content_type(self):
        """Test HTML content type"""
        serializer = HTMLSerializer({"test": "data"})
        assert serializer.get_content_type() == "text/html"


class TestXMLSerializer:
    """Test XML serialization"""

    def test_xml_serialization(self):
        """Test basic XML serialization"""
        data = {"test": "value", "number": 123, "nested": {"key": "value"}}

        serializer = XMLSerializer(data)
        result = serializer.serialize()

        # Should be valid XML with proper structure
        root = ET.fromstring(result)
        assert root.tag == "binance_data"
        assert root.get("timestamp") is not None

        # Check that data was converted properly
        assert result.startswith("<?xml version=")
        assert "binance_data" in result

    def test_xml_content_type(self):
        """Test XML content type"""
        serializer = XMLSerializer({"test": "data"})
        assert serializer.get_content_type() == "application/xml"


class TestChartSerializer:
    """Test Chart serialization"""

    def test_chart_content_type(self):
        """Test Chart content type"""
        serializer = ChartSerializer({"test": "data"})
        assert serializer.get_content_type() == "image/png"

    def test_chart_serialization_returns_bytes(self):
        """Test that chart serialization returns bytes"""
        data = {"test": "data"}
        serializer = ChartSerializer(data)
        result = serializer.serialize()

        # Should return bytes (PNG data)
        assert isinstance(result, bytes)
        assert len(result) > 0


class TestSerializerFactory:
    """Test serializer factory function"""

    def test_get_serializer_json(self):
        """Test getting JSON serializer"""
        serializer = get_serializer({"test": "data"}, "json")
        assert isinstance(serializer, JSONSerializer)

    def test_get_serializer_csv(self):
        """Test getting CSV serializer"""
        serializer = get_serializer({"test": "data"}, "csv")
        assert isinstance(serializer, CSVSerializer)

    def test_get_serializer_html(self):
        """Test getting HTML serializer"""
        serializer = get_serializer({"test": "data"}, "html")
        assert isinstance(serializer, HTMLSerializer)

    def test_get_serializer_xml(self):
        """Test getting XML serializer"""
        serializer = get_serializer({"test": "data"}, "xml")
        assert isinstance(serializer, XMLSerializer)

    def test_get_serializer_chart(self):
        """Test getting Chart serializer"""
        serializer = get_serializer({"test": "data"}, "chart")
        assert isinstance(serializer, ChartSerializer)

    def test_get_serializer_invalid_format(self):
        """Test error handling for invalid format"""
        with pytest.raises(ValueError, match="Unsupported format"):
            get_serializer({"test": "data"}, "invalid")
