# Contributing to xmlforge

Thank you for your interest in contributing to xmlforge! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and constructive in all interactions with the project maintainers and other contributors.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/xmlforge.git
   cd xmlforge
   ```

3. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Development Workflow

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and ensure all tests pass:
   ```bash
   pytest
   ```

3. Format your code:
   ```bash
   black src tests
   isort src tests
   ```

4. Run linters:
   ```bash
   flake8 src tests
   mypy src
   ```

5. Commit your changes:
   ```bash
   git add .
   git commit -m "Add your descriptive commit message"
   ```

6. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

7. Open a Pull Request on GitHub

## Testing

- Write tests for all new functionality
- Ensure all tests pass before submitting a PR
- Aim for high test coverage (>80%)

Run tests with:
```bash
pytest
pytest --cov=xmlforge  # With coverage report
```

## Code Style

This project uses:
- **black** for code formatting (line length: 100)
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

Run all formatters and linters:
```bash
tox -e format  # Format code
tox -e lint    # Check code style
tox -e type    # Type checking
```

## Documentation

- Update documentation for any new features
- Use docstrings for all public functions and classes
- Follow Google-style docstring format

## Pull Request Guidelines

- Keep PRs focused on a single feature or bugfix
- Include tests for new functionality
- Update documentation as needed
- Ensure all CI checks pass
- Write clear, descriptive commit messages
- Reference any related issues in your PR description

## Reporting Bugs

When reporting bugs, please include:
- Python version
- xmlforge version
- Operating system
- Steps to reproduce the issue
- Expected vs actual behavior
- Any relevant error messages or logs

## Feature Requests

We welcome feature requests! Please:
- Check if the feature has already been requested
- Clearly describe the feature and its use case
- Explain how it would benefit the project

## Questions?

If you have questions, feel free to:
- Open an issue on GitHub
- Contact the maintainers

Thank you for contributing to xmlforge!
