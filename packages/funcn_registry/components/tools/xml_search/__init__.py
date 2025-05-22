"""XML Search Tool for XML data processing and XPath queries."""

from .tool import XMLElement, XMLSearchResult, find_xml_elements, process_xml, search_xml_xpath, validate_xml_file

__all__ = [
    "process_xml",
    "search_xml_xpath",
    "find_xml_elements",
    "validate_xml_file",
    "XMLSearchResult",
    "XMLElement"
]
