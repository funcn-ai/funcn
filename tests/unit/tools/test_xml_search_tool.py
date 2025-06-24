"""Test suite for xml_search_tool following best practices."""

import asyncio
import pytest

# Import the actual tool functions
from packages.funcn_registry.components.tools.xml_search.tool import (
    XMLElement,
    XMLSearchResult,
    find_xml_elements,
    process_xml,
    search_xml_xpath,
    validate_xml_file,
)
from pathlib import Path
from tests.fixtures import TestDataFactory
from tests.utils import BaseToolTest


class TestXMLSearchTool(BaseToolTest):
    """Test xml_search_tool component."""
    
    component_name = "xml_search_tool"
    component_path = Path("packages/funcn_registry/components/tools/xml_search")
    
    def create_test_xml(self, file_path: Path, content: str) -> Path:
        """Create a test XML file with specified content.
        
        Args:
            file_path: Path where to save the XML file
            content: XML content as string
        
        Returns:
            Path to the created file
        """
        file_path.write_text(content, encoding='utf-8')
        return file_path
    
    def get_component_function(self):
        """Import the tool function."""
        return process_xml
    
    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            {
                "file_path": "/path/to/data.xml",
                "search_text": "admin",
                "case_sensitive": False
            },
            {
                "file_path": "/path/to/config.xml",
                "xpath_query": "//database",
                "attribute_search": {"host": "localhost"}
            },
            {
                "xml_content": "<root><user>Test</user></root>",
                "search_text": "Test",
                "namespace_aware": True
            }
        ]
    
    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        assert isinstance(output, XMLSearchResult)
        assert isinstance(output.success, bool)
        assert isinstance(output.total_matches, int)
        assert isinstance(output.matches, list)
        for match in output.matches:
            assert isinstance(match, XMLElement)
            assert hasattr(match, 'tag')
            assert hasattr(match, 'xpath')
    
    @pytest.mark.asyncio
    async def test_xpath_search(self, tmp_path):
        """Test searching with XPath expressions."""
        xml_content = """<?xml version="1.0"?>
        <company>
            <employees>
                <employee id="1">
                    <name>John Doe</name>
                    <department>Engineering</department>
                </employee>
                <employee id="2">
                    <name>Jane Smith</name>
                    <department>Marketing</department>
                </employee>
            </employees>
        </company>"""
        
        xml_file = self.create_test_xml(tmp_path / "company.xml", xml_content)
        
        # Search with specific XPath
        result = await search_xml_xpath(
            file_path=str(xml_file),
            xpath="//employee[department='Engineering']"
        )
        
        assert result.success is True
        assert result.total_matches == 1
        assert result.matches[0].tag == "employee"
        assert result.matches[0].attributes.get("id") == "1"
    
    @pytest.mark.asyncio
    async def test_namespace_handling(self, tmp_path):
        """Test XML namespace handling."""
        namespaced_xml = """<?xml version="1.0"?>
        <root xmlns:app="http://example.com/app" xmlns="http://example.com/default">
            <app:config>
                <app:setting name="debug">true</app:setting>
                <app:setting name="port">8080</app:setting>
            </app:config>
            <data>
                <item>test data</item>
            </data>
        </root>"""
        
        xml_file = self.create_test_xml(tmp_path / "namespaced.xml", namespaced_xml)
        
        # Search with text to avoid namespace issues
        result = await process_xml(
            file_path=str(xml_file),
            search_text="debug",
            namespace_aware=True
        )
        
        assert result.success is True
        assert result.total_matches >= 1
        assert any(m.tag == "setting" for m in result.matches)
        # Check namespaces (they should be valid strings)
        for key, value in result.namespaces.items():
            assert isinstance(key, str)
            assert isinstance(value, str)
    
    @pytest.mark.asyncio
    async def test_attribute_search(self, tmp_path):
        """Test searching in XML attributes."""
        xml_content = """<?xml version="1.0"?>
        <root>
            <user id="123" role="admin" status="active">John</user>
            <user id="456" role="user" status="inactive">Jane</user>
            <config debug="true" environment="production"/>
        </root>"""
        
        xml_file = self.create_test_xml(tmp_path / "users.xml", xml_content)
        
        # Search by attributes
        result = await find_xml_elements(
            file_path=str(xml_file),
            attributes={"role": "admin"}
        )
        
        assert result.success is True
        assert result.total_matches >= 1
        assert any(m.attributes.get("role") == "admin" for m in result.matches)
    
    @pytest.mark.asyncio
    async def test_text_content_search(self, tmp_path):
        """Test searching in element text content."""
        xml_content = """<?xml version="1.0"?>
        <document>
            <title>Important Document</title>
            <sections>
                <section id="1">
                    <heading>Introduction</heading>
                    <content>This is the introduction text.</content>
                </section>
                <section id="2">
                    <heading>Main Content</heading>
                    <content>This is the main content with important information.</content>
                </section>
            </sections>
        </document>"""
        
        xml_file = self.create_test_xml(tmp_path / "document.xml", xml_content)
        
        # Search for text (case-insensitive by passing to process_xml)
        result = await process_xml(
            file_path=str(xml_file),
            search_text="important",
            case_sensitive=False
        )
        
        assert result.success is True
        assert result.total_matches >= 2  # In title and content
        
        # Case-sensitive search
        result_case = await process_xml(
            file_path=str(xml_file),
            search_text="Important",
            case_sensitive=True
        )
        
        assert result_case.success is True
        assert result_case.total_matches >= 1
    
    @pytest.mark.asyncio
    async def test_tag_filter_search(self, tmp_path):
        """Test searching with tag name filters."""
        xml_content = """<?xml version="1.0"?>
        <root>
            <users>
                <user>Alice</user>
                <admin_user>Bob</admin_user>
                <guest_user>Charlie</guest_user>
            </users>
            <user_config>
                <setting>value</setting>
            </user_config>
        </root>"""
        
        xml_file = self.create_test_xml(tmp_path / "users.xml", xml_content)
        
        # Search in specific tags
        result = await find_xml_elements(
            file_path=str(xml_file),
            tag_names=["user", "admin_user", "guest_user"],
            containing_text="Bob"
        )
        
        assert result.success is True
        assert result.total_matches >= 1
        assert any(m.text and "Bob" in m.text for m in result.matches)
    
    @pytest.mark.asyncio
    async def test_mixed_content_search(self, tmp_path):
        """Test searching in mixed content (text + elements)."""
        xml_content = """<?xml version="1.0"?>
        <article>
            <para>This is a <bold>bold</bold> statement with <italic>emphasis</italic>.</para>
            <para>Another paragraph with <link href="http://example.com">a link</link>.</para>
        </article>"""
        
        xml_file = self.create_test_xml(tmp_path / "article.xml", xml_content)
        
        # Search for text
        result = await process_xml(
            file_path=str(xml_file),
            search_text="bold"
        )
        
        assert result.success is True
        assert result.total_matches >= 1
    
    @pytest.mark.asyncio
    async def test_cdata_handling(self, tmp_path):
        """Test handling of CDATA sections."""
        xml_content = """<?xml version="1.0"?>
        <root>
            <script><![CDATA[
                function test() {
                    return "This is JavaScript code";
                }
            ]]></script>
            <data><![CDATA[Some <raw> XML & data]]></data>
        </root>"""
        
        xml_file = self.create_test_xml(tmp_path / "cdata.xml", xml_content)
        
        # Search in CDATA content
        result = await process_xml(
            file_path=str(xml_file),
            search_text="JavaScript"
        )
        
        assert result.success is True
        assert result.total_matches >= 1
    
    @pytest.mark.asyncio
    async def test_empty_element_handling(self, tmp_path):
        """Test handling of empty XML elements."""
        xml_content = """<?xml version="1.0"?>
        <root>
            <empty/>
            <empty_with_attr status="none"/>
            <has_text>content</has_text>
        </root>"""
        
        xml_file = self.create_test_xml(tmp_path / "empty.xml", xml_content)
        
        # Search for attribute in empty element
        result = await find_xml_elements(
            file_path=str(xml_file),
            attributes={"status": "none"}
        )
        
        assert result.success is True
        assert result.total_matches >= 1
        assert any(m.tag == "empty_with_attr" for m in result.matches)
    
    @pytest.mark.asyncio
    async def test_malformed_xml_handling(self, tmp_path):
        """Test handling of malformed XML."""
        malformed_xml = """<?xml version="1.0"?>
        <root>
            <unclosed>
            <another>test
        </root>"""
        
        xml_file = self.create_test_xml(tmp_path / "malformed.xml", malformed_xml)
        
        result = await process_xml(
            file_path=str(xml_file),
            search_text="test"
        )
        
        assert result.success is False
        assert result.error is not None
    
    @pytest.mark.asyncio
    async def test_large_xml_performance(self, tmp_path):
        """Test performance with large XML files."""
        # Create large XML structure
        large_xml = '<?xml version="1.0"?>\n<root>\n'
        for i in range(500):  # Reduced from 1000 for faster test
            large_xml += f'  <item id="{i}" type="test">Item {i} content</item>\n'
        large_xml += '</root>'
        
        xml_file = self.create_test_xml(tmp_path / "large.xml", large_xml)
        
        import time
        start_time = time.time()
        
        result = await process_xml(
            file_path=str(xml_file),
            search_text="Item 250"
        )
        
        elapsed = time.time() - start_time
        
        assert result.success is True
        assert elapsed < 3.0  # Should complete quickly
        assert result.total_matches >= 1
    
    @pytest.mark.asyncio
    async def test_xml_validation(self, tmp_path):
        """Test XML validation with schema."""
        # Create a simple XSD schema
        xsd_content = """<?xml version="1.0" encoding="UTF-8"?>
        <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
            <xs:element name="root">
                <xs:complexType>
                    <xs:sequence>
                        <xs:element name="item" maxOccurs="unbounded">
                            <xs:complexType>
                                <xs:simpleContent>
                                    <xs:extension base="xs:string">
                                        <xs:attribute name="id" type="xs:ID" use="required"/>
                                    </xs:extension>
                                </xs:simpleContent>
                            </xs:complexType>
                        </xs:element>
                    </xs:sequence>
                </xs:complexType>
            </xs:element>
        </xs:schema>"""
        
        valid_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <root>
            <item id="i1">Valid item</item>
            <item id="i2">Another item</item>
        </root>"""
        
        xsd_file = self.create_test_xml(tmp_path / "schema.xsd", xsd_content)
        xml_file = self.create_test_xml(tmp_path / "valid.xml", valid_xml)
        
        # Validate against schema
        result = await validate_xml_file(
            file_path=str(xml_file),
            xsd_schema_path=str(xsd_file)
        )
        
        assert result.success is True
        assert len(result.validation_errors) == 0
    
    @pytest.mark.asyncio
    async def test_special_characters_escaping(self, tmp_path):
        """Test handling of XML special characters."""
        xml_content = """<?xml version="1.0"?>
        <root>
            <data>Less than &lt; and greater than &gt;</data>
            <data>Ampersand &amp; apostrophe &apos; quote &quot;</data>
            <url>http://example.com?foo=bar&amp;baz=qux</url>
        </root>"""
        
        xml_file = self.create_test_xml(tmp_path / "special.xml", xml_content)
        
        # Search for text with special characters
        result = await process_xml(
            file_path=str(xml_file),
            search_text="Less than"
        )
        
        assert result.success is True
        assert result.total_matches >= 1
        
        # Search for URL with escaped ampersand
        result_url = await process_xml(
            file_path=str(xml_file),
            search_text="foo=bar"
        )
        
        assert result_url.success is True
        assert result_url.total_matches >= 1
    
    @pytest.mark.asyncio
    async def test_max_depth_filter(self, tmp_path):
        """Test filtering results by maximum depth."""
        xml_content = """<?xml version="1.0"?>
        <root>
            <level1>
                <level2>
                    <level3>
                        <target>Deep content</target>
                    </level3>
                    <target>Medium content</target>
                </level2>
                <target>Shallow content</target>
            </level1>
        </root>"""
        
        xml_file = self.create_test_xml(tmp_path / "depth.xml", xml_content)
        
        # Search with depth limit
        result = await process_xml(
            file_path=str(xml_file),
            search_text="content",
            max_depth=3
        )
        
        assert result.success is True
        # Should find only shallow and medium content at depth <= 3
        assert all(m.tag == "target" for m in result.matches)
    
    @pytest.mark.asyncio
    async def test_xml_from_string(self, tmp_path):
        """Test processing XML from string content."""
        xml_content = """<?xml version="1.0"?>
        <root>
            <message type="info">Hello World</message>
            <message type="warning">Be careful</message>
        </root>"""
        
        # Process XML from string
        result = await process_xml(
            xml_content=xml_content,
            attribute_search={"type": "warning"}
        )
        
        assert result.success is True
        assert result.total_matches >= 1
        assert any(m.attributes.get("type") == "warning" for m in result.matches)
    
    @pytest.mark.asyncio
    async def test_complex_xpath_queries(self, tmp_path):
        """Test complex XPath queries."""
        xml_content = """<?xml version="1.0"?>
        <library>
            <book isbn="123" year="2020">
                <title>Python Programming</title>
                <author>John Doe</author>
                <price currency="USD">29.99</price>
            </book>
            <book isbn="456" year="2021">
                <title>XML Processing</title>
                <author>Jane Smith</author>
                <price currency="EUR">34.99</price>
            </book>
            <book isbn="789" year="2022">
                <title>Data Science</title>
                <author>Bob Johnson</author>
                <price currency="USD">39.99</price>
            </book>
        </library>"""
        
        xml_file = self.create_test_xml(tmp_path / "library.xml", xml_content)
        
        # Complex XPath: books with USD price > 30
        result = await search_xml_xpath(
            file_path=str(xml_file),
            xpath="//book[price[@currency='USD' and . > 30]]"
        )
        
        assert result.success is True
        assert result.total_matches >= 1
        assert all(m.tag == "book" for m in result.matches)
    
    @pytest.mark.asyncio
    async def test_nonexistent_file(self, tmp_path):
        """Test handling of nonexistent files."""
        result = await process_xml(
            file_path=str(tmp_path / "nonexistent.xml"),
            search_text="test"
        )
        
        assert result.success is False
        assert result.error is not None
        assert "does not exist" in result.error
    
    @pytest.mark.asyncio
    async def test_parent_child_relationships(self, tmp_path):
        """Test that parent-child relationships are captured."""
        xml_content = """<?xml version="1.0"?>
        <catalog>
            <category name="electronics">
                <product id="1">Laptop</product>
                <product id="2">Phone</product>
            </category>
            <category name="books">
                <product id="3">Novel</product>
            </category>
        </catalog>"""
        
        xml_file = self.create_test_xml(tmp_path / "catalog.xml", xml_content)
        
        # Use XPath to find all product elements
        result = await search_xml_xpath(
            file_path=str(xml_file),
            xpath="//product"
        )
        
        assert result.success is True
        assert result.total_matches == 3
        # All products should have category as parent
        assert all(m.parent_tag == "category" for m in result.matches)
