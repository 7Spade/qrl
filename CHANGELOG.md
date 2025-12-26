# Changelog

## [Unreleased]

### Changed
- **Refactored Dash app into modular architecture**: Broke down 719-line monolithic `dash_app.py` into focused modules
- Organized code into components, layouts, and callbacks for better maintainability
- Renamed main entry point from `dash_app.py` to `app.py` for clarity
- Each module now has a single responsibility (62-264 lines each)
- **Migrated from FastAPI to Dash**: Replaced FastAPI web framework with Dash for interactive dashboards
- Web dashboard now uses Dash with Bootstrap theme (CYBORG)
- Updated all documentation to reflect Dash migration
- Dashboard now runs with `python web/app.py` instead of `uvicorn web.app:app`

### Added
- **Component modules** (`web/components/`):
  - `charts.py`: Reusable chart creation functions (204 lines)
  - `cards.py`: Card content generators (264 lines)
- **Layout modules** (`web/layouts/`):
  - `main.py`: Dashboard layout structure (162 lines)
- **Callback modules** (`web/callbacks/`):
  - `data_callbacks.py`: Data update callbacks (177 lines)
  - `chart_callbacks.py`: Chart update callbacks (87 lines)
- `docs/DASH_ARCHITECTURE.md`: Comprehensive architecture documentation
- Dash dependencies (dash, dash-bootstrap-components, plotly)
- Interactive Plotly charts for price and technical indicators
- Real-time dashboard with auto-refresh functionality
- Enhanced visualization with candlestick charts and subplots
- `/health` endpoint for Cloud Run health checks
- Gunicorn production server configuration for Cloud Run deployment
- **Performance dependencies**: orjson (fast JSON) and redis[hiredis] (fast C parser)

### Fixed
- Cloud Run deployment: Added `/health` endpoint for container health checks
- Cloud Run deployment: Switched to Gunicorn for production server
- Container startup: Added proper PORT environment variable handling
- Balance display: Fixed balance fetching to use correct API method and data structure
- Balance display: Added debug logging for balance data troubleshooting
- Error handling: Replaced bare `except:` clause with proper exception handling in cache stats callback
- Error handling: Added logging for cache stats fetch errors to improve debugging
- Position callback: Added exchange_client None check to prevent callback failures
### Improved
- **Reduced cognitive load**: Smaller, focused files instead of one large file
- **Better separation of concerns**: UI, logic, and data handling are distinct
- **Easier testing**: Components can be tested independently
- **Enhanced reusability**: Components can be used across different layouts
- **Clearer code organization**: Easy to locate and modify specific functionality

### Removed
- FastAPI dependencies (fastapi, uvicorn, jinja2)
- Legacy HTML templates (index.html, history.html)
- Monolithic `web/dash_app.py` file (replaced with modular structure)

## [Previous Changes]

### Added
- Comprehensive documentation for MEXC API credentials and Cloud Run authentication
- Detailed troubleshooting guide for 403 Forbidden errors
- Explanation of MEXC API credentials (Access Key vs Secret Key)
- Instructions for switching between public and IAM authentication
- Bilingual (EN/ZH) documentation for authentication options

### Fixed
- **Clarified MEXC API credentials** in .env.example and documentation (Access Key = MEXC_API_KEY, Secret Key = MEXC_API_SECRET)
- **403 Forbidden error** documentation with clear solutions for both public and IAM-authenticated access
- **Cloud Build deployment** - reverted to reliable two-step approach (deploy + IAM binding) to fix build failures
- Simplified authentication workflow - IAM authentication is now configured post-deployment via manual commands

### Changed
- Updated cloudbuild.yaml to use simple, reliable deployment with automatic public access
- Enhanced README with security comparison and clear deployment instructions
- Improved .env.example with clearer explanations of MEXC API credential naming
- Updated Chinese quick start guide (快速開始.md) with authentication options
- Removed complex conditional deployment logic that was causing build failures

## [Historical Changes]

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
