"""XML Search Tool for XML data processing and XPath queries."""

import aiofiles
import asyncio
import re
import xml.etree.ElementTree as ET
from lxml import etree
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Literal, Optional, Union


class XMLElement(BaseModel):
    """Represents an XML element found in search."""

    tag: str = Field(..., description="Element tag name")
    text: str | None = Field(None, description="Element text content")
    attributes: dict[str, str] = Field(default_factory=dict, description="Element attributes")
    xpath: str = Field(..., description="XPath to this element")
    line_number: int | None = Field(None, description="Line number in source file")
    children_count: int = Field(0, description="Number of child elements")
    parent_tag: str | None = Field(None, description="Parent element tag")
    namespace: str | None = Field(None, description="Element namespace")

    class Config:
        arbitrary_types_allowed = True


class XMLSearchResult(BaseModel):
    """Result of XML search operation."""

    success: bool = Field(..., description="Whether the search was successful")
    file_path: str | None = Field(None, description="Path to the XML file")
    total_matches: int = Field(..., description="Total number of matches found")
    matches: list[XMLElement] = Field(default_factory=list, description="Matching XML elements")
    namespaces: dict[str, str] = Field(default_factory=dict, description="Namespaces found in XML")
    root_element: str | None = Field(None, description="Root element tag")
    error: str | None = Field(None, description="Error message if search failed")
    search_time: float = Field(..., description="Time taken to search in seconds")
    validation_errors: list[str] = Field(default_factory=list, description="XML validation errors if any")


def validate_xml_input(file_path: str | None, xml_content: str | None) -> str | None:
    """Ensure either file_path or xml_content is provided."""
    if file_path is None and xml_content is None:
        raise ValueError("Either file_path or xml_content must be provided")
    if file_path is not None:
        path = Path(file_path)
        if not path.exists():
            raise ValueError(f"File does not exist: {file_path}")
    return file_path


def build_element_info(
    element: etree._Element,
    parent_map: dict,
    tree: etree.ElementTree,
    xpath: str = ""
) -> XMLElement:
    """Build XMLElement from lxml element."""
    parent = parent_map.get(element)

    # Get namespace
    namespace = None
    if element.tag.startswith('{'):
        namespace = element.tag[1:element.tag.index('}')]
        tag = element.tag[element.tag.index('}')+1:]
    else:
        tag = element.tag

    # Get line number if available
    line_number = None
    if hasattr(element, 'sourceline'):
        line_number = element.sourceline

    return XMLElement(
        tag=tag,
        text=element.text.strip() if element.text else None,
        attributes=dict(element.attrib),
        xpath=xpath or tree.getpath(element),
        line_number=line_number,
        children_count=len(element),
        parent_tag=parent.tag if parent is not None else None,
        namespace=namespace
    )


async def load_xml(file_path: str | None, xml_content: str | None) -> etree._Element:
    """Load XML from file or string."""
    parser = etree.XMLParser(remove_blank_text=True)

    if file_path:
        async with aiofiles.open(file_path, encoding='utf-8') as f:
            content = await f.read()
        return etree.fromstring(content.encode('utf-8'), parser)
    else:
        return etree.fromstring(xml_content.encode('utf-8'), parser)


async def validate_xml_against_schema(
    root: etree._Element,
    xsd_schema_path: str | None
) -> list[str]:
    """Validate XML against schema if provided."""
    errors = []

    if xsd_schema_path:
        try:
            async with aiofiles.open(xsd_schema_path, encoding='utf-8') as f:
                schema_content = await f.read()

            schema_doc = etree.fromstring(schema_content.encode('utf-8'))
            schema = etree.XMLSchema(schema_doc)

            if not schema.validate(root):
                errors = [str(error) for error in schema.error_log]
        except Exception as e:
            errors.append(f"Schema validation error: {str(e)}")

    return errors


def search_by_xpath(
    root: etree._Element,
    xpath_query: str,
    namespace_aware: bool
) -> list[etree._Element]:
    """Execute XPath query."""
    if not xpath_query:
        return []

    # Extract namespaces
    namespaces = {}
    if namespace_aware:
        for prefix, uri in root.nsmap.items():
            if prefix is not None:
                namespaces[prefix] = uri

    try:
        if namespaces:
            results = root.xpath(xpath_query, namespaces=namespaces)
        else:
            results = root.xpath(xpath_query)

        # Ensure results are elements
        return [r for r in results if isinstance(r, etree._Element)]
    except Exception as e:
        return []


def search_by_text(
    root: etree._Element,
    search_text: str,
    tag_filter: list[str] | None,
    case_sensitive: bool
) -> list[etree._Element]:
    """Search for elements containing specific text."""
    if not search_text:
        return []

    matches = []
    search_str = search_text.lower() if not case_sensitive else search_text

    for element in root.iter():
        # Skip if tag filter is specified and doesn't match
        if tag_filter:
            tag = element.tag.split('}')[-1] if '}' in element.tag else element.tag
            if tag not in tag_filter:
                continue

        # Check element text
        if element.text:
            element_text = element.text.lower() if not case_sensitive else element.text
            if search_str in element_text:
                matches.append(element)
                continue

        # Check attribute values
        for attr_value in element.attrib.values():
            attr_text = attr_value.lower() if not case_sensitive else attr_value
            if search_str in attr_text:
                matches.append(element)
                break

    return matches


def search_by_attributes(
    root: etree._Element,
    attribute_search: dict[str, str],
    tag_filter: list[str] | None,
    case_sensitive: bool
) -> list[etree._Element]:
    """Search for elements with specific attributes."""
    if not attribute_search:
        return []

    matches = []

    for element in root.iter():
        # Skip if tag filter is specified and doesn't match
        if tag_filter:
            tag = element.tag.split('}')[-1] if '}' in element.tag else element.tag
            if tag not in tag_filter:
                continue

        # Check if element has all required attributes
        element_matches = True
        for attr_name, attr_value in attribute_search.items():
            if attr_name not in element.attrib:
                element_matches = False
                break

            # If attr_value is provided, check it matches
            if attr_value:
                actual_value = element.attrib[attr_name]
                if not case_sensitive:
                    actual_value = actual_value.lower()
                    attr_value = attr_value.lower()

                if attr_value not in actual_value:
                    element_matches = False
                    break

        if element_matches:
            matches.append(element)

    return matches


def filter_by_depth(
    elements: list[etree._Element],
    root: etree._Element,
    max_depth: int | None
) -> list[etree._Element]:
    """Filter elements by maximum depth."""
    if max_depth is None:
        return elements

    filtered = []
    for element in elements:
        depth = 0
        current = element
        while current is not None and current != root:
            depth += 1
            current = current.getparent()

        if depth <= max_depth:
            filtered.append(element)

    return filtered


async def process_xml(
    xml_content: str | None = None,
    file_path: str | None = None,
    xpath_query: str | None = None,
    search_text: str | None = None,
    attribute_search: dict[str, str] | None = None,
    tag_filter: list[str] | None = None,
    namespace_aware: bool = True,
    validate: bool = False,
    xsd_schema_path: str | None = None,
    case_sensitive: bool = True,
    include_children: bool = True,
    max_depth: int | None = None,
    pretty_print: bool = False
) -> XMLSearchResult:
    """Process XML data with various search and validation options.

    Args:
        xml_content: XML content as string
        file_path: Path to XML file
        xpath_query: XPath query to execute
        search_text: Text to search for in elements
        attribute_search: Attributes to search for
        tag_filter: Filter results to specific tags
        namespace_aware: Whether to handle namespaces
        validate: Whether to validate XML
        xsd_schema_path: Path to XSD schema for validation
        case_sensitive: Whether text search is case sensitive
        include_children: Whether to include child elements in results
        max_depth: Maximum depth to search
        pretty_print: Whether to pretty print XML in results

    Returns:
        XMLSearchResult with matching elements
    """
    start_time = asyncio.get_event_loop().time()

    try:
        # Validate input
        validate_xml_input(file_path, xml_content)

        # Load XML
        root = await load_xml(file_path, xml_content)
        tree = etree.ElementTree(root)

        # Create parent map for element relationships
        parent_map = {c: p for p in tree.iter() for c in p}

        # Extract namespaces
        namespaces = dict(root.nsmap) if root.nsmap else {}

        # Validate if requested
        validation_errors = []
        if validate:
            validation_errors = await validate_xml_against_schema(root, xsd_schema_path)

        # Perform search
        all_matches = set()

        # XPath search
        if xpath_query:
            xpath_results = search_by_xpath(root, xpath_query, namespace_aware)
            all_matches.update(xpath_results)

        # Text search
        if search_text:
            text_results = search_by_text(root, search_text, tag_filter, case_sensitive)
            all_matches.update(text_results)

        # Attribute search
        if attribute_search:
            attr_results = search_by_attributes(root, attribute_search, tag_filter, case_sensitive)
            all_matches.update(attr_results)

        # If no search criteria, return root info
        if not any([xpath_query, search_text, attribute_search]):
            all_matches.add(root)

        # Convert to list and filter by depth
        matches_list = list(all_matches)
        matches_list = filter_by_depth(matches_list, root, max_depth)

        # Build element info
        matches = []
        for element in matches_list:
            try:
                xpath = tree.getpath(element)
                element_info = build_element_info(element, parent_map, tree, xpath)
                matches.append(element_info)
            except:
                continue

        # Sort by xpath for consistent ordering
        matches.sort(key=lambda x: x.xpath)

        search_time = asyncio.get_event_loop().time() - start_time

        # Get root element tag
        root_tag = root.tag.split('}')[-1] if '}' in root.tag else root.tag

        return XMLSearchResult(
            success=True,
            file_path=file_path,
            total_matches=len(matches),
            matches=matches,
            namespaces=namespaces,
            root_element=root_tag,
            search_time=search_time,
            validation_errors=validation_errors
        )

    except Exception as e:
        search_time = asyncio.get_event_loop().time() - start_time
        return XMLSearchResult(
            success=False,
            file_path=file_path,
            total_matches=0,
            error=str(e),
            search_time=search_time
        )


# Convenience functions
async def search_xml_xpath(
    file_path: str | None = None,
    xml_content: str | None = None,
    xpath: str = "//",
    namespaces: bool = True
) -> XMLSearchResult:
    """Execute XPath query on XML.

    Args:
        file_path: Path to XML file
        xml_content: XML content as string
        xpath: XPath query
        namespaces: Whether to handle namespaces

    Returns:
        XMLSearchResult with matching elements
    """
    return await process_xml(
        file_path=file_path,
        xml_content=xml_content,
        xpath_query=xpath,
        namespace_aware=namespaces
    )


async def find_xml_elements(
    file_path: str | None = None,
    xml_content: str | None = None,
    tag_names: list[str] = None,
    containing_text: str | None = None,
    attributes: dict[str, str] | None = None
) -> XMLSearchResult:
    """Find XML elements by tag, text, or attributes.

    Args:
        file_path: Path to XML file
        xml_content: XML content as string
        tag_names: Tag names to filter by
        containing_text: Text to search for
        attributes: Attributes to match

    Returns:
        XMLSearchResult with matching elements
    """
    return await process_xml(
        file_path=file_path,
        xml_content=xml_content,
        tag_filter=tag_names,
        search_text=containing_text,
        attribute_search=attributes
    )


async def validate_xml_file(
    file_path: str,
    xsd_schema_path: str | None = None
) -> XMLSearchResult:
    """Validate XML file against schema.

    Args:
        file_path: Path to XML file
        xsd_schema_path: Path to XSD schema

    Returns:
        XMLSearchResult with validation results
    """
    return await process_xml(
        file_path=file_path,
        validate=True,
        xsd_schema_path=xsd_schema_path
    )
