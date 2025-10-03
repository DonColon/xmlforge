"""
Example: Basic XML parsing operations
"""

from xmlforge import XMLParser

# Create a parser
parser = XMLParser()

# Example XML string
xml_string = """<?xml version="1.0" encoding="UTF-8"?>
<bookstore>
    <book category="cooking">
        <title lang="en">Everyday Italian</title>
        <author>Giada De Laurentiis</author>
        <year>2005</year>
        <price>30.00</price>
    </book>
    <book category="children">
        <title lang="en">Harry Potter</title>
        <author>J.K. Rowling</author>
        <year>2005</year>
        <price>29.99</price>
    </book>
</bookstore>
"""

# Parse the XML string
root = parser.parse_string(xml_string)

print(f"Root tag: {root.tag}")
print(f"Number of books: {len(root)}")

# Convert to dictionary
data = parser.to_dict(root)
print("\nParsed data:")
print(data)

# Access specific elements
for book in root.findall("book"):
    title = book.find("title").text
    author = book.find("author").text
    print(f"\nTitle: {title}")
    print(f"Author: {author}")
