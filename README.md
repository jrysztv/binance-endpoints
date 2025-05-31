# Binance Endpoints API

A production-ready FastAPI backend for Binance market data analysis with 4 endpoints.

## Features

- Real-time Binance market data integration
- RESTful API with 4 endpoints
- Docker containerization
- CI/CD with GitHub Actions
- Comprehensive testing with pytest

## Quick Start

### Local Development

```bash
# Install dependencies
poetry install

# Run the development server
poetry run uvicorn app.main:app --reload

# Run tests
poetry run pytest
```

### Docker

```bash
# Build image
docker build -t binance-backend .

# Run container
docker run -p 8000:8000 binance-backend
```

## API Endpoints

- `GET /health` - Health check
- `GET /api/v1/market-data` - Market data with parameters
- `GET /api/v1/trading` - Trading information
- `GET /api/v1/analytics` - Analytics and insights

## Documentation

API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc` # Deployment test
