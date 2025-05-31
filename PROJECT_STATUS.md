# Binance Connector Backend - Project Status & Instructions

## 🎯 Assignment Overview
**Goal:** Build a production-ready Binance connector backend with 4 endpoints for CEU DE3 course submission.

**Original Assignment:** R-based API deployment, but we're implementing in Python using FastAPI.

**GitHub Repository:** https://github.com/jrysztv/binance-endpoints.git

## 📋 Project Requirements

### Core Features
- [ ] 4 API endpoints with different serializers
- [ ] At least one endpoint with multiple parameters
- [ ] Production-ready FastAPI backend
- [ ] Integration with [Binance Python Connector](https://github.com/binance/binance-connector-python)
- [x] TDD approach with pytest
- [x] Poetry for dependency management

### Infrastructure & DevOps
- [ ] GitHub Workflows CI/CD pipeline
- [x] Production Dockerfile deployment to EC2
- [x] Devcontainer for local development
- [ ] Automated testing in CI/CD
- [x] Health check endpoint (implement first)
- [x] NGINX reverse proxy for production security

### Deployment
- [ ] Deploy to own EC2 instance (not provided AMI)
- [ ] SSH key stored in base64 format for GitHub Secrets
- [ ] Docker image push to EC2 on repository push

## 🛠 Tech Stack
- **Backend:** FastAPI (Python)
- **Dependency Management:** Poetry
- **Testing:** pytest (TDD approach)
- **Containerization:** Docker + Devcontainer (Dev/Prod separation)
- **Reverse Proxy:** NGINX with security headers & rate limiting
- **CI/CD:** GitHub Workflows
- **Deployment:** AWS EC2
- **External API:** Binance Connector Python

## 📁 Project Structure (Current)
```
binance-endpoints/
├── .devcontainer/
│   └── devcontainer.json         ✅ Complete
├── .github/
│   └── workflows/                🔄 TODO
│       ├── ci.yml
│       └── deploy.yml
├── app/
│   ├── __init__.py              ✅ Complete
│   ├── main.py                  ✅ Complete
│   ├── api/
│   │   ├── __init__.py          ✅ Complete
│   │   ├── endpoints/
│   │   │   ├── __init__.py      ✅ Complete
│   │   │   ├── health.py        ✅ Complete
│   │   │   ├── market_data.py   🔄 TODO
│   │   │   ├── trading.py       🔄 TODO
│   │   │   └── analytics.py     🔄 TODO
│   │   └── dependencies.py      🔄 TODO
│   ├── core/
│   │   ├── __init__.py          ✅ Complete
│   │   ├── config.py            🔄 TODO
│   │   └── binance_client.py    🔄 TODO
│   └── schemas/
│       ├── __init__.py          ✅ Complete
│       └── responses.py         ✅ Complete
├── tests/
│   ├── __init__.py              ✅ Complete
│   ├── conftest.py              ✅ Complete
│   ├── test_health.py           ✅ Complete
│   ├── test_market_data.py      🔄 TODO
│   ├── test_trading.py          🔄 TODO
│   └── test_analytics.py        🔄 TODO
├── Dockerfile                   ✅ Production (multi-stage)
├── Dockerfile.dev               ✅ Development (with tests)
├── docker-compose.dev.yml       ✅ Dev with volume mounts
├── docker-compose.prod.yml      ✅ Production with NGINX
├── nginx.conf                   ✅ Security headers & rate limiting
├── .dockerignore                ✅ Complete
├── .gitignore                   ✅ Complete
├── pyproject.toml               ✅ Complete
├── README.md                    ✅ Complete
└── PROJECT_STATUS.md            ✅ Complete
```

## ⚡ Prerequisites

### Local Development
- [x] Python 3.11+
- [x] Poetry installed
- [x] Docker Desktop (running)
- [ ] VS Code (for devcontainer)
- [ ] Git configured

### AWS Setup
- [x] AWS Account with EC2 access
- [x] EC2 Key Pair created (binance-endpoints-key)
- [x] Security Group configured (ports 80, 443, 22)
- [x] EC2 instance launched (Ubuntu 24.04, t2.micro, 63.35.236.42)
- [x] Docker installed on EC2 (Docker 26.1.3, Compose 2.27.1)

### GitHub Setup
- [ ] Repository created: https://github.com/jrysztv/binance-endpoints.git
- [ ] SSH key generated and added to GitHub
- [ ] SSH private key converted to base64 for GitHub Secrets
- [ ] Repository secrets configured:
  - `EC2_SSH_KEY` (base64 encoded private key)
  - `EC2_HOST` (EC2 public IP)
  - `EC2_USERNAME` (usually 'ubuntu' or 'ec2-user')

### Binance API
- [ ] Binance account (for testing)
- [ ] API keys (optional for public endpoints)

## 🚀 Development Phases

### Phase 1: Project Setup ✅ COMPLETE
- [x] Initialize Poetry project
- [x] Set up basic FastAPI structure
- [x] Create health check endpoint
- [x] Set up pytest configuration
- [x] Create Dockerfile (production)
- [x] Create Dockerfile.dev (development)
- [x] Set up devcontainer
- [x] Create docker-compose files (dev/prod)
- [x] NGINX reverse proxy configuration

### Phase 2: CI/CD Pipeline (Current Phase)
- [x] EC2 Infrastructure Setup (Ubuntu 24.04, Docker installed)
- [x] SSH Key Setup (base64 encoded for GitHub Secrets)
- [ ] Create GitHub Repository
- [ ] Create GitHub Workflows
- [ ] Configure GitHub Secrets
- [ ] Test deployment pipeline

### Phase 3: Binance Integration
- [ ] Integrate Binance Python connector
- [ ] Implement 4 main endpoints
- [ ] Add comprehensive tests
- [ ] Documentation

### Phase 4: Production Ready
- [ ] Error handling
- [ ] Logging
- [ ] Security considerations
- [ ] Performance optimization
- [ ] Final testing

## 📸 Screenshot Requirements
Screenshots needed at these points:
- [x] Initial project setup in VS Code
- [x] Poetry dependencies installation
- [x] First test passing
- [x] Health endpoint working locally
- [x] Docker build success
- [x] Tests running in devcontainer
- [ ] GitHub Actions pipeline success
- [ ] EC2 deployment success
- [ ] All endpoints working on EC2
- [ ] Final API documentation

## 🔧 PowerShell Commands Reference
```powershell
# Poetry commands (remember: we're in PowerShell, no &&)
poetry install
poetry add fastapi uvicorn pytest
poetry run pytest
poetry run uvicorn app.main:app --reload

# Docker commands (Development)
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up -d
docker-compose -f docker-compose.dev.yml exec app poetry run pytest -v

# Docker commands (Production with NGINX)
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
curl http://localhost/health  # Test through NGINX (port 80)

# Git commands
git add .
git commit -m "message"
git push origin main
```

## 📝 Current Status: PHASE 2 - EC2 SETUP COMPLETE ✅

### ✅ Completed Tasks:
1. ✅ Poetry project initialized with dependencies
2. ✅ Basic FastAPI structure created
3. ✅ Health endpoint implemented with TDD
4. ✅ Tests passing (2/2 tests)
5. ✅ Local server running successfully
6. ✅ **Dockerfile.dev created** (development with tests & hot reload)
7. ✅ **Dockerfile created** (production multi-stage build)
8. ✅ **docker-compose.dev.yml** (volume mounts, test execution)
9. ✅ **docker-compose.prod.yml** (NGINX reverse proxy)
10. ✅ **nginx.conf** (security headers, rate limiting)
11. ✅ Devcontainer configuration created
12. ✅ .gitignore and .dockerignore created
13. ✅ **Tests running successfully in devcontainer**
14. ✅ **Production NGINX setup working** (port 80 with security headers)
15. ✅ **EC2 Instance Setup** (Ubuntu 24.04.2 LTS, t2.micro, IP: 63.35.236.42)
16. ✅ **SSH Key Configuration** (binance-endpoints-key.pem, base64 encoded)
17. ✅ **Docker Installation on EC2** (Docker 26.1.3, Compose 2.27.1, tested with hello-world)
18. ✅ **Security Group Configuration** (sg-0d4bddfc2a85814d2, HTTP/HTTPS/SSH access)

### 🔄 Next Immediate Steps (Phase 2):
1. **Create GitHub Repository** (https://github.com/jrysztv/binance-endpoints.git)
2. **Create GitHub Workflows** (ci.yml, deploy.yml - adapt from ratelimiter project)
3. **Configure GitHub Secrets**:
   - `EC2_SSH_KEY_B64` (base64 encoded private key)
   - `EC2_HOST=63.35.236.42`
   - `EC2_USERNAME=ubuntu`
   - `EC2_APP_PATH=/opt/binance-endpoints`
   - `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION=eu-west-1`
   - `EC2_SECURITY_GROUP_ID=sg-0d4bddfc2a85814d2`
4. **Test deployment pipeline**

### 🎯 EC2 Setup Commands Reference:
```bash
# SSH Connection (from WSL)
ssh -i ~/.ssh/binance-endpoints.pem ubuntu@63.35.236.42

# Docker Installation (on EC2)
sudo apt update
sudo apt install -y docker.io docker-compose-v2
sudo usermod -aG docker ubuntu
newgrp docker
docker run hello-world

# Application Directory Setup (on EC2)
sudo mkdir -p /opt/binance-endpoints
sudo chown ubuntu:ubuntu /opt/binance-endpoints
```

### 📸 Screenshots to Take Now:
1. **VS Code showing complete project structure** (full screen with date/time)
2. **Terminal showing development container tests**: `docker-compose -f docker-compose.dev.yml exec app poetry run pytest -v`
3. **Browser showing health endpoint through NGINX**: http://localhost/health
4. **Browser showing API docs through NGINX**: http://localhost/docs
5. **Docker containers running**: `docker ps`

### 🎉 Major Achievement:
**Production-Ready Docker Setup Complete!** 
- ✅ Development environment with hot reload and volume mounts
- ✅ Production environment with NGINX reverse proxy
- ✅ Security headers and rate limiting configured
- ✅ Multi-stage builds for optimized production images
- ✅ Tests running successfully in containers

### Instructions for Future Chat Sessions:
1. Always read this document first
2. Check current phase and completed tasks
3. Update checkboxes as tasks are completed
4. Take screenshots where indicated
5. Remember PowerShell syntax (no &&)
6. Always run tests via `poetry run pytest` or in containers
7. Update dependencies via `poetry add` or `poetry update`

## 🐛 Known Issues & Solutions
- **SSH Key for GitHub:** Must be base64 encoded when storing in GitHub Secrets
- **PowerShell:** Use separate commands instead of && chaining
- **Testing:** Always use `poetry run pytest` not bare `pytest`
- **Docker:** Docker Desktop must be running for build commands
- **NGINX:** Production setup uses port 80, development uses port 8000

## 📚 Useful Links
- [Binance Python Connector](https://github.com/binance/binance-connector-python)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [GitHub Workflow Examples](https://docs.github.com/en/actions/examples)
- [Reference Project](https://github.com/jrysztv/ratelimiter/tree/main) - Similar Docker/NGINX setup 