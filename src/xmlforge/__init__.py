"""
xmlforge - A python library for splitting, transforming, parsing and validation xml files.

This library provides utilities to work with XML files including:
- Splitting large XML files into smaller chunks
- Transforming XML using XSLT or custom transformations
- Parsing XML documents with validation support
- Validating XML against schemas (XSD, DTD, RelaxNG)
"""

__version__ = "0.1.0"
__author__ = "DonColon"
__license__ = "Apache-2.0"

from xmlforge.parser import XMLParser
from xmlforge.splitter import XMLSplitter
from xmlforge.transformer import XMLTransformer
from xmlforge.validator import XMLValidator

__all__ = [
    "XMLParser",
    "XMLSplitter",
    "XMLTransformer",
    "XMLValidator",
    "__version__",
]
