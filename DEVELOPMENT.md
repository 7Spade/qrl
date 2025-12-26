# Development Guide

## Code Standards

This project follows PEP 8 coding standards and modern Python best practices.

### Code Style

- **Indentation**: 4 spaces (no tabs)
- **Line length**: Maximum 79 characters
- **Naming conventions**:
  - Variables and functions: `snake_case`
  - Classes: `CamelCase`
  - Constants: `UPPER_SNAKE_CASE`
- **Blank lines**:
  - 2 blank lines between functions and classes
  - 1 blank line within functions for logical separation

### Type Hints

All functions must include type hints for parameters and return values:

```python
def calculate_price(amount: float, rate: float) -> float:
    """Calculate total price."""
    return amount * rate
```

### Error Handling

Use specific exception types instead of bare `except`:

```python
try:
    result = risky_operation()
except ValueError as e:
    print(f"Invalid value: {e}")
except NetworkError as e:
    print(f"Network error: {e}")
```

### Documentation

All modules, classes, and functions must have docstrings:

```python
def process_data(data: List[str]) -> Dict[str, int]:
    """
    Process input data and return statistics.
    
    Args:
        data: List of strings to process
        
    Returns:
        Dictionary containing processed statistics
        
    Raises:
        ValueError: When data is empty
    """
    pass
```

## Development Setup

### Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest flake8 black mypy
```

### Code Quality Tools

#### Format Code with Black

```bash
black --line-length 79 .
```

#### Check PEP 8 Compliance

```bash
flake8 .
```

#### Type Checking

```bash
mypy *.py
```

### Running the Application

#### Main Trading Bot

```bash
python main.py
```

#### Web Dashboard

```bash
cd web
uvicorn app:app --reload
```

## Project Structure

```
qrl/
├── config.py          # Configuration and environment variables
├── exchange.py        # MEXC exchange integration
├── main.py           # Main trading logic entry point
├── risk.py           # Risk management rules
├── state.py          # Position state persistence
├── strategy.py       # Trading strategy (EMA-based)
├── web/
│   └── app.py        # FastAPI dashboard
├── requirements.txt   # Production dependencies
├── pyproject.toml    # Project configuration
└── .flake8           # Linter configuration
```

## Best Practices

1. **Version Control**: Use Git for all code changes
2. **Dependencies**: Manage via `requirements.txt` and `pyproject.toml`
3. **Secrets**: Use environment variables (`.env` file), never hardcode
4. **Testing**: Write unit tests for critical functions
5. **Documentation**: Keep docstrings and comments up to date
6. **Code Review**: Run linters before committing

## Contributing

1. Follow PEP 8 standards
2. Add type hints to all functions
3. Write comprehensive docstrings
4. Test your changes
5. Run `flake8` before committing
