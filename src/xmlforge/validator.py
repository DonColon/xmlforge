"""
XML Validator module for validating XML documents.
"""

from pathlib import Path
from typing import Union

from lxml import etree


class ValidationError(Exception):
    """Exception raised when XML validation fails."""

    pass


class XMLValidator:
    """
    A class for validating XML documents against schemas.

    Supports XSD, DTD, and RelaxNG validation.
    """

    def __init__(self) -> None:
        """Initialize the XMLValidator."""
        pass

    def validate_with_xsd(self, xml_file: Union[str, Path], xsd_file: Union[str, Path]) -> bool:
        """
        Validate an XML file against an XSD schema.

        Args:
            xml_file: Path to the XML file to validate.
            xsd_file: Path to the XSD schema file.

        Returns:
            True if validation succeeds.

        Raises:
            ValidationError: If validation fails.
            FileNotFoundError: If any file does not exist.
        """
        xml_file = Path(xml_file)
        xsd_file = Path(xsd_file)

        if not xml_file.exists():
            raise FileNotFoundError(f"XML file not found: {xml_file}")
        if not xsd_file.exists():
            raise FileNotFoundError(f"XSD file not found: {xsd_file}")

        schema_doc = etree.parse(str(xsd_file))
        schema = etree.XMLSchema(schema_doc)

        xml_doc = etree.parse(str(xml_file))

        if not schema.validate(xml_doc):
            errors = self._format_errors(schema.error_log)
            raise ValidationError(f"XSD validation failed:\n{errors}")

        return True

    def validate_with_dtd(self, xml_file: Union[str, Path], dtd_file: Union[str, Path]) -> bool:
        """
        Validate an XML file against a DTD.

        Args:
            xml_file: Path to the XML file to validate.
            dtd_file: Path to the DTD file.

        Returns:
            True if validation succeeds.

        Raises:
            ValidationError: If validation fails.
            FileNotFoundError: If any file does not exist.
        """
        xml_file = Path(xml_file)
        dtd_file = Path(dtd_file)

        if not xml_file.exists():
            raise FileNotFoundError(f"XML file not found: {xml_file}")
        if not dtd_file.exists():
            raise FileNotFoundError(f"DTD file not found: {dtd_file}")

        dtd = etree.DTD(str(dtd_file))
        xml_doc = etree.parse(str(xml_file))

        if not dtd.validate(xml_doc):
            errors = self._format_errors(dtd.error_log)
            raise ValidationError(f"DTD validation failed:\n{errors}")

        return True

    def validate_with_relaxng(self, xml_file: Union[str, Path], rng_file: Union[str, Path]) -> bool:
        """
        Validate an XML file against a RelaxNG schema.

        Args:
            xml_file: Path to the XML file to validate.
            rng_file: Path to the RelaxNG schema file.

        Returns:
            True if validation succeeds.

        Raises:
            ValidationError: If validation fails.
            FileNotFoundError: If any file does not exist.
        """
        xml_file = Path(xml_file)
        rng_file = Path(rng_file)

        if not xml_file.exists():
            raise FileNotFoundError(f"XML file not found: {xml_file}")
        if not rng_file.exists():
            raise FileNotFoundError(f"RelaxNG file not found: {rng_file}")

        relaxng_doc = etree.parse(str(rng_file))
        relaxng = etree.RelaxNG(relaxng_doc)

        xml_doc = etree.parse(str(xml_file))

        if not relaxng.validate(xml_doc):
            errors = self._format_errors(relaxng.error_log)
            raise ValidationError(f"RelaxNG validation failed:\n{errors}")

        return True

    def is_well_formed(self, xml_input: Union[str, Path]) -> bool:
        """
        Check if an XML file or string is well-formed.

        Args:
            xml_input: Path to XML file or XML string.

        Returns:
            True if the XML is well-formed, False otherwise.
        """
        try:
            # Handle empty string
            if not xml_input or (isinstance(xml_input, str) and not xml_input.strip()):
                return False

            if isinstance(xml_input, (str, Path)) and Path(xml_input).exists():
                etree.parse(str(xml_input))
            else:
                etree.fromstring(str(xml_input).encode("utf-8"))
            return True
        except (etree.XMLSyntaxError, OSError):
            return False

    def _format_errors(self, error_log: etree._ListErrorLog) -> str:
        """
        Format validation errors into a readable string.

        Args:
            error_log: The error log from validation.

        Returns:
            Formatted error messages.
        """
        errors = []
        for error in error_log:
            errors.append(f"Line {error.line}, Column {error.column}: {error.message}")
        return "\n".join(errors)
