# Changelog

All notable changes to the QRL Trading Bot project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Docker Support**: Dockerfile for containerization
- **Google Cloud Run**: Complete deployment configuration
  - cloudbuild.yaml for automated builds
  - docker-compose.yml for local testing
  - .dockerignore for optimized builds
- **Deployment Documentation**:
  - DEPLOYMENT.md (English) - Complete Cloud Run guide
  - 部署指南.md (Chinese) - 完整部署說明
  - deploy.sh - Automated deployment script
- **Web Dashboard Improvements**:
  - Health check endpoint (/health) for Cloud Run
  - Error handling for API failures
- **Dependencies**: Added FastAPI, uvicorn, gunicorn, requests
- Comprehensive project analysis document (PROJECT_ANALYSIS.md)
- Complete README with setup instructions
- Comprehensive docstrings for all modules and functions
- CHANGELOG file for tracking project changes
- Automatic data directory creation in state.py

### Fixed
- Missing `import os` in exchange.py
- Missing database commit in state.py update_position_usdt()
- Data directory not being created automatically

### Changed
- Enhanced all Python files with detailed module and function documentation
- Improved code organization and readability
- Updated requirements.txt with production dependencies

### Security
- .dockerignore prevents sensitive files in containers
- Cloud Run configuration supports Secret Manager integration

## [0.1.0] - Initial Release

### Added
- Core trading bot functionality
- EMA-based trading strategy (EMA20/EMA60 crossover)
- MEXC exchange integration via CCXT
- Risk management with position limits
- SQLite-based position state tracking
- FastAPI web dashboard for monitoring
- Configuration via environment variables
- Basic project structure and dependencies

### Features
- Automated limit buy order placement
- Technical analysis using EMA indicators
- Real-time price monitoring
- Position tracking and persistence
- Configurable trading parameters

### Dependencies
- ccxt >= 4.2.0
- pandas >= 2.1.0
- numpy >= 1.26.0
- ta >= 0.11.0
- pydantic >= 2.5.0
- python-dotenv >= 1.0.0
- SQLAlchemy >= 2.0.0
