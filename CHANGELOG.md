# Changelog

## [Unreleased]

### Added
- Explicit IAM policy binding step in Cloud Build configuration to prevent 403 Forbidden errors

### Fixed
- **403 Forbidden error** on Cloud Run deployment by adding explicit IAM policy binding step
- Deployment configuration now automatically grants public access without manual intervention

### Changed
- Updated Cloud Build configuration to include automatic IAM policy setup
- Enhanced README with clearer deployment instructions and better troubleshooting section
- Improved explanation of why 403 errors occur and how the fix works

## [Previous Releases]

### Added
- Google Cloud Run deployment support
  - Dockerfile for containerization
  - cloudbuild.yaml for automated deployment
  - .dockerignore for build optimization
- Health check endpoint (/health) in web dashboard
- Complete bilingual documentation (EN/ZH)
- Comprehensive code docstrings for all modules

### Fixed
- Missing `import os` in exchange.py
- Missing database commit in state.py
- Automatic data directory creation

### Changed
- Updated requirements.txt with production dependencies (FastAPI, uvicorn, gunicorn)

## [0.1.0] - Initial Release

### Added
- EMA-based trading strategy (EMA20/EMA60)
- MEXC exchange integration via CCXT
- Risk management with position limits
- SQLite position tracking
- FastAPI web dashboard
- Environment-based configuration
