# QRL Trading Bot Documentation

This directory contains the essential documentation for the QRL trading bot project.

## Core Specifications

**Primary reference documents** - Read these first:

1. **[交易機器人完整規範指南.md](交易機器人完整規範指南.md)** - Complete trading bot specification (Chinese)
   - System architecture and design patterns
   - Trading strategy framework
   - Risk management system
   - State management and data persistence

2. **[交易機器人頁面指南.md](交易機器人頁面指南.md)** - Dashboard and UI specification (Chinese)
   - Web interface design
   - Chart visualization requirements
   - API endpoint specifications
   - User interface components

## Implementation Documentation

**Production-ready guides** for deployment and usage:

3. **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture overview
   - Module structure and responsibilities
   - Data flow and dependencies
   - Design patterns used

4. **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Complete module reference
   - Directory structure
   - File descriptions
   - Import relationships

5. **[QUICK_START.md](QUICK_START.md)** - Quick start guide
   - Installation instructions
   - Configuration setup
   - Running the bot and dashboard

## Feature-Specific Guides

6. **[MEXC_DOCUMENTATION_INDEX.md](MEXC_DOCUMENTATION_INDEX.md)** - Complete guide to MEXC API documentation
   - Quick reference to all MEXC docs
   - Documentation navigation guide
   - Performance summary
   - Official MEXC resource links

7. **[MEXC_API_優化總結.md](MEXC_API_優化總結.md)** - MEXC API 優化總結 (中文)
   - 效能指標與分析 (繁體中文)
   - 快取策略優化
   - 使用指南
   - 最佳實踐建議

8. **[MEXC_API_GUIDE.md](MEXC_API_GUIDE.md)** - Complete MEXC API integration guide
   - API endpoints documentation
   - Authentication and rate limiting
   - Optimization strategies
   - Best practices and troubleshooting

9. **[MEXC_OPTIMIZATION_RECOMMENDATIONS.md](MEXC_OPTIMIZATION_RECOMMENDATIONS.md)** - MEXC API optimization analysis
   - Performance metrics and analysis
   - Cache strategy optimization
   - Rate limit management
   - Security recommendations

10. **[REDIS_SETUP.md](REDIS_SETUP.md)** - Redis configuration
    - Redis installation
    - Environment variables
    - Caching configuration

11. **[REDIS_CACHING_GUIDE.md](REDIS_CACHING_GUIDE.md)** - MEXC API caching integration
    - Cache-aside pattern implementation
    - TTL configuration per data type
    - Performance optimization

12. **[CHART_VISUALIZATION_GUIDE.md](CHART_VISUALIZATION_GUIDE.md)** - Chart.js integration
    - Interactive chart setup
    - Multi-timeframe selector
    - Chart data API usage

13. **[TECHNICAL_INDICATORS_GUIDE.md](TECHNICAL_INDICATORS_GUIDE.md)** - Technical indicators
    - Williams %R, MA, MACD, RSI, Volume, EMA
    - Calculation methodologies
    - Usage in trading strategies

## Quick Links

- **Repository Root**: [../README.md](../README.md)
- **CHANGELOG**: [../CHANGELOG.md](../CHANGELOG.md)
- **Tests**: [../tests/](../tests/)
- **Source Code**: [../src/](../src/)

## Documentation Structure

```
docs/
├── 交易機器人完整規範指南.md          # Core specification
├── 交易機器人頁面指南.md              # UI specification
├── ARCHITECTURE.md                  # System architecture
├── PROJECT_STRUCTURE.md             # Module reference
├── QUICK_START.md                  # Getting started
├── MEXC_DOCUMENTATION_INDEX.md     # MEXC docs navigation
├── MEXC_API_優化總結.md             # MEXC optimization (Chinese)
├── MEXC_API_GUIDE.md               # MEXC API integration
├── MEXC_OPTIMIZATION_RECOMMENDATIONS.md # MEXC optimization
├── REDIS_SETUP.md                  # Redis config
├── REDIS_CACHING_GUIDE.md          # Caching guide
├── CHART_VISUALIZATION_GUIDE.md    # Charts guide
├── TECHNICAL_INDICATORS_GUIDE.md   # Indicators
└── README.md                       # This file
```

## Support

For issues, questions, or contributions, please refer to the main [README.md](../README.md) in the repository root.
