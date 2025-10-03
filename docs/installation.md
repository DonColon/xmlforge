# Installation

## Requirements

- Python 3.8 or higher
- pip

## Install from PyPI

```bash
pip install xmlforge
```

## Install for Development

If you want to contribute or modify the code:

```bash
# Clone the repository
git clone https://github.com/DonColon/xmlforge.git
cd xmlforge

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Verify Installation

```python
import xmlforge
print(xmlforge.__version__)
```

## Dependencies

xmlforge has minimal dependencies:

- **lxml** (>=4.9.0): XML processing library

Development dependencies include:
- pytest, pytest-cov: Testing
- black, isort: Code formatting
- flake8: Linting
- mypy: Type checking
- pre-commit: Git hooks
- tox: Testing automation
