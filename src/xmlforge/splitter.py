"""
XML Splitter module for splitting large XML files.
"""

from pathlib import Path
from typing import Iterator, Optional, Union
import zipfile

from lxml import etree


class XMLSplitter:
    """
    A class for splitting large XML files into smaller chunks.

    Attributes:
        chunk_size (int): The number of elements per chunk.
        target_tag (str): The tag name to split on.
        pattern (str): File pattern to match when processing directories.
        recursive (bool): Whether to search subdirectories recursively.
    """

    def __init__(
        self,
        target_tag: str,
        chunk_size: int = 1000,
        pattern: str = "*.xml",
        recursive: bool = False
    ) -> None:
        """
        Initialize the XMLSplitter.

        Args:
            target_tag: The XML tag to use as split points.
            chunk_size: Number of elements per chunk. Defaults to 1000.
            pattern: File pattern to match when processing directories. Defaults to "*.xml".
            recursive: If True, search subdirectories recursively. Defaults to False.
        """
        self.target_tag = target_tag
        self.chunk_size = chunk_size
        self.pattern = pattern
        self.recursive = recursive

    def split_file(
        self, filepath: Union[str, Path], output_dir: Optional[Union[str, Path]] = None
    ) -> Iterator[etree._Element]:
        """
        Split XML file(s) into chunks based on the target tag.

        Args:
            filepath: Path to XML file, directory containing XML files, or ZIP file.
            output_dir: Optional directory to write chunk files. If None, yields elements.

        Yields:
            XML elements for each chunk.

        Raises:
            FileNotFoundError: If the file or directory does not exist.
            ValueError: If directory/ZIP contains no XML files.
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Path not found: {filepath}")

        chunk = []
        chunk_num = 0

        # Determine source type and get XML sources
        if filepath.is_file() and filepath.suffix.lower() == '.zip':
            # Handle ZIP file
            xml_sources = self._get_zip_xml_sources(filepath)
        elif filepath.is_file():
            # Single XML file
            xml_sources = [(filepath, None)]
        elif filepath.is_dir():
            # Directory with XML files
            if self.recursive:
                xml_files = list(filepath.rglob(self.pattern))
            else:
                xml_files = list(filepath.glob(self.pattern))

            if not xml_files:
                search_type = "recursively" if self.recursive else "in directory"
                raise ValueError(f"No files matching '{self.pattern}' found {search_type}: {filepath}")

            xml_sources = [(f, None) for f in xml_files]
        else:
            raise ValueError(f"Invalid path: {filepath}")

        # Process all XML sources
        for xml_source, zip_ref in xml_sources:
            print(f"Processing: {xml_source}")

            if zip_ref:
                # Stream from ZIP file
                with zip_ref.open(str(xml_source)) as xml_file:
                    context = etree.iterparse(xml_file, events=("end",), tag=self.target_tag)
                    for event, element in context:
                        chunk.append(element)

                        if len(chunk) >= self.chunk_size:
                            if output_dir:
                                self._write_chunk(chunk, output_dir, chunk_num)
                            else:
                                yield self._create_chunk_tree(chunk)

                            chunk = []
                            chunk_num += 1

                        # Clear element to free memory
                        element.clear()
                        while element.getprevious() is not None:
                            del element.getparent()[0]
            else:
                # Regular file
                context = etree.iterparse(str(xml_source), events=("end",), tag=self.target_tag)
                for event, element in context:
                    chunk.append(element)

                    if len(chunk) >= self.chunk_size:
                        if output_dir:
                            self._write_chunk(chunk, output_dir, chunk_num)
                        else:
                            yield self._create_chunk_tree(chunk)

                        chunk = []
                        chunk_num += 1

                    # Clear element to free memory
                    element.clear()
                    while element.getprevious() is not None:
                        del element.getparent()[0]

        # Handle remaining elements
        if chunk:
            if output_dir:
                self._write_chunk(chunk, output_dir, chunk_num)
            else:
                yield self._create_chunk_tree(chunk)

    def _get_zip_xml_sources(self, zip_path: Path) -> list:
        """
        Get XML file sources from ZIP file.

        Args:
            zip_path: Path to ZIP file.

        Returns:
            List of tuples (xml_filename, zipfile_reference).
        """
        try:
            zip_ref = zipfile.ZipFile(zip_path, 'r')
            xml_files = [name for name in zip_ref.namelist()
                        if name.lower().endswith('.xml') and not name.startswith('__')]

            if not xml_files:
                zip_ref.close()
                raise ValueError(f"No XML files found in ZIP: {zip_path}")

            return [(xml_file, zip_ref) for xml_file in xml_files]

        except zipfile.BadZipFile:
            raise ValueError(f"Invalid ZIP file: {zip_path}")

    def _create_chunk_tree(self, elements: list) -> etree._Element:
        """
        Create an XML tree from a list of elements.

        Args:
            elements: List of XML elements.

        Returns:
            Root element containing all elements.
        """
        root = etree.Element("chunk")
        for elem in elements:
            root.append(elem)
        return root

    def _write_chunk(self, elements: list, output_dir: Union[str, Path], chunk_num: int) -> None:
        """
        Write a chunk to a file.

        Args:
            elements: List of XML elements.
            output_dir: Directory to write the chunk file.
            chunk_num: Chunk number for filename.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        root = self._create_chunk_tree(elements)
        tree = etree.ElementTree(root)

        output_file = output_dir / f"chunk_{chunk_num:04d}.xml"
        tree.write(str(output_file), encoding="utf-8", xml_declaration=True, pretty_print=True)
