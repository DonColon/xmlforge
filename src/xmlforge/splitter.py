"""
XML Splitter module for splitting large XML files.
"""

from pathlib import Path
from typing import Iterator, Optional, Union

from lxml import etree


class XMLSplitter:
    """
    A class for splitting large XML files into smaller chunks.

    Attributes:
        chunk_size (int): The number of elements per chunk.
        target_tag (str): The tag name to split on.
    """

    def __init__(self, target_tag: str, chunk_size: int = 1000) -> None:
        """
        Initialize the XMLSplitter.

        Args:
            target_tag: The XML tag to use as split points.
            chunk_size: Number of elements per chunk. Defaults to 1000.
        """
        self.target_tag = target_tag
        self.chunk_size = chunk_size

    def split_file(
        self, filepath: Union[str, Path], output_dir: Optional[Union[str, Path]] = None
    ) -> Iterator[etree._Element]:
        """
        Split an XML file into chunks based on the target tag.

        Args:
            filepath: Path to the XML file to split.
            output_dir: Optional directory to write chunk files. If None, yields elements.

        Yields:
            XML elements for each chunk.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        context = etree.iterparse(str(filepath), events=("end",), tag=self.target_tag)
        chunk = []
        chunk_num = 0

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
