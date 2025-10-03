# xmlforge

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

A modern Python library for splitting, transforming, parsing and validating XML files.

## Features

- **XML Parsing**: Parse XML files and strings with a simple, intuitive API
- **XML Splitting**: Split large XML files into smaller, manageable chunks
- **XML Transformation**: Transform XML using XSLT or custom transformations
- **XML Validation**: Validate XML against XSD, DTD, and RelaxNG schemas
- **Namespace Handling**: Easy namespace addition and removal
- **Type Hints**: Full type annotations for better IDE support
- **Well Tested**: Comprehensive test suite with high coverage

## Installation

Install xmlforge using pip:

```bash
pip install xmlforge
```

For development installation with all tools:

```bash
pip install xmlforge[dev]
```

## Quick Start

### Parsing XML

```python
from xmlforge import XMLParser

parser = XMLParser()

# Parse from file
tree = parser.parse_file("example.xml")

# Parse from string
xml_string = '<?xml version="1.0"?><root><child>value</child></root>'
element = parser.parse_string(xml_string)

# Convert to dictionary
data = parser.to_dict(element)
print(data)  # {'child': {'@text': 'value'}}
```

### Splitting Large XML Files

```python
from xmlforge import XMLSplitter

splitter = XMLSplitter(target_tag="item", chunk_size=1000)

# Split and write to files
splitter.split_file("large_file.xml", output_dir="chunks/")

# Or iterate over chunks
for chunk in splitter.split_file("large_file.xml"):
    # Process each chunk
    print(f"Processing chunk with {len(chunk)} items")
```

### Transforming XML

```python
from xmlforge import XMLTransformer

# Transform with XSLT
transformer = XMLTransformer(xslt_file="transform.xslt")
result = transformer.transform_file("input.xml", output_file="output.xml")

# Remove namespaces
transformer = XMLTransformer()
element = parser.parse_string(xml_with_namespaces)
clean_element = transformer.remove_namespace(element)
```

### Validating XML

```python
from xmlforge import XMLValidator

validator = XMLValidator()

# Validate against XSD
try:
    validator.validate_with_xsd("document.xml", "schema.xsd")
    print("Valid!")
except ValidationError as e:
    print(f"Validation failed: {e}")

# Check if well-formed
is_valid = validator.is_well_formed("document.xml")
```

## Requirements

- Python 3.8+
- lxml >= 4.9.0

## Development

### Setting Up Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/DonColon/xmlforge.git
   cd xmlforge
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=xmlforge

# Run specific test file
pytest tests/test_parser.py
```

### Code Quality

```bash
# Format code
black src tests
isort src tests

# Lint code
flake8 src tests

# Type checking
mypy src

# Run all checks with tox
tox
```

## Project Structure

```
xmlforge/
├── src/
│   └── xmlforge/
│       ├── __init__.py
│       ├── parser.py
│       ├── splitter.py
│       ├── transformer.py
│       └── validator.py
├── tests/
│   ├── __init__.py
│   ├── test_parser.py
│   ├── test_splitter.py
│   ├── test_transformer.py
│   └── test_validator.py
├── docs/
├── examples/
├── .github/
│   └── workflows/
├── .editorconfig
├── .flake8
├── .gitignore
├── .pre-commit-config.yaml
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── MANIFEST.in
├── README.md
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── setup.py
└── tox.ini
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes.

## Support

- **Issues**: [GitHub Issues](https://github.com/DonColon/xmlforge/issues)
- **Documentation**: [GitHub Repository](https://github.com/DonColon/xmlforge)

## Acknowledgments

Built with [lxml](https://lxml.de/) - a powerful and Pythonic XML processing library.
