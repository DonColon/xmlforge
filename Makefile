.PHONY: help install install-dev test lint format type-check clean build publish docs

help:
	@echo "Available commands:"
	@echo "  install      - Install package"
	@echo "  install-dev  - Install package with dev dependencies"
	@echo "  test         - Run tests"
	@echo "  lint         - Run linters"
	@echo "  format       - Format code with black and isort"
	@echo "  type-check   - Run type checker"
	@echo "  clean        - Remove build artifacts"
	@echo "  build        - Build distribution packages"
	@echo "  publish      - Publish to PyPI (requires credentials)"
	@echo "  docs         - Build documentation"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest --cov=xmlforge --cov-report=term-missing

lint:
	black --check src tests
	isort --check-only src tests
	flake8 src tests

format:
	black src tests
	isort src tests

type-check:
	mypy src

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .tox/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

publish: build
	twine upload dist/*

docs:
	@echo "Documentation is in docs/ directory"
	@echo "Open docs/index.md to get started"
