# Changelog

## [Unreleased]

### Added
- IAM authentication option for Cloud Run deployment via `_USE_IAM_AUTH` substitution variable
- Comprehensive documentation for both public and IAM-authenticated deployment modes
- Detailed troubleshooting guide for 403 Forbidden errors
- Explanation of MEXC API credentials (Access Key vs Secret Key)
- Instructions for accessing IAM-authenticated services
- Bilingual (EN/ZH) documentation for authentication options

### Fixed
- **Clarified MEXC API credentials** in .env.example and documentation (Access Key = MEXC_API_KEY, Secret Key = MEXC_API_SECRET)
- **403 Forbidden error** documentation with clear solutions for both public and IAM-authenticated access
- Cloud Build configuration now supports conditional authentication based on deployment requirements

### Changed
- Updated cloudbuild.yaml to support both public and IAM-authenticated deployments via substitution variable
- Enhanced README with security comparison table and authentication mode selection guidance
- Improved .env.example with clearer explanations of MEXC API credential naming
- Updated Chinese quick start guide (快速開始.md) with authentication options

## [Previous Changes]

### Added
- Explicit IAM policy binding step in Cloud Build configuration to prevent 403 Forbidden errors
- MEXC subaccount support in exchange configuration
- Detailed API credential setup instructions with links to MEXC API management page

### Fixed
- **403 Forbidden error** on Cloud Run deployment by adding explicit IAM policy binding step
- Deployment configuration now automatically grants public access without manual intervention
- **Incorrect MEXC API credential format** in .env.example with proper descriptive placeholders
- **Missing subaccount configuration** support for MEXC exchange

### Changed
- Updated Cloud Build configuration to include automatic IAM policy setup
- Enhanced README with clearer deployment instructions and better troubleshooting section
- Improved explanation of why 403 errors occur and how the fix works
- Updated .env.example with proper MEXC API key format and subaccount support
- Enhanced exchange.py to support optional MEXC subaccount trading

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
