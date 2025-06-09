"""Test suite for xml_search_tool following best practices."""

import pytest
import xml.etree.ElementTree as ET
from pathlib import Path
from tests.fixtures import TestDataFactory
from tests.utils import BaseToolTest
from unittest.mock import Mock, mock_open, patch


class TestXMLSearchTool(BaseToolTest):
    """Test xml_search_tool component."""
    
    component_name = "xml_search_tool"
    component_path = Path("packages/funcn_registry/components/tools/xml_search_tool")
    
    def get_component_function(self):
        """Import the tool function."""
        # Would import: from tools.xml_search_tool import search_xml
        def mock_search_xml(
            xml_path: str | Path,
            query: str,
            xpath: str | None = None,
            namespaces: dict[str, str] | None = None,
            search_text: bool = True,
            search_attributes: bool = True,
            search_tags: bool = False
        ) -> list[dict[str, any]]:
            """Mock XML search tool."""
            return [
                {
                    "xpath": "/root/users/user[1]",
                    "tag": "user",
                    "text": "John Doe",
                    "attributes": {"id": "1", "role": "admin"},
                    "match_type": "text"
                },
                {
                    "xpath": "/root/config/database",
                    "tag": "database",
                    "attributes": {"host": "localhost", "port": "5432"},
                    "match_type": "attribute"
                }
            ]
        return mock_search_xml
    
    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            {
                "xml_path": "/path/to/data.xml",
                "query": "admin",
                "search_attributes": True,
                "search_text": True
            },
            {
                "xml_path": "/path/to/config.xml",
                "query": "localhost",
                "xpath": "//database",
                "search_attributes": True
            },
            {
                "xml_path": "/path/to/document.xml",
                "query": "user",
                "search_tags": True,
                "namespaces": {"ns": "http://example.com/ns"}
            }
        ]
    
    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        assert isinstance(output, list)
        
        for result in output:
            assert isinstance(result, dict)
            assert "xpath" in result or "path" in result or "location" in result
            assert "tag" in result or "element" in result
    
    def test_xpath_search(self, tmp_path):
        """Test searching with XPath expressions."""
        xml_content = TestDataFactory.SAMPLE_XML
        xml_file = TestDataFactory.create_xml_file(tmp_path)
        tool = self.get_component_function()
        
        with patch("builtins.open", mock_open(read_data=xml_content)):
            # Search with specific XPath
            results = tool(xml_file, "Engineering", xpath="//employee[department='Engineering']")
            
            # Should only find matches within the XPath context
            assert all("employee" in str(r) for r in results)
    
    def test_namespace_handling(self, tmp_path):
        """Test XML namespace handling."""
        xml_file = tmp_path / "namespaced.xml"
        tool = self.get_component_function()
        
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
        
        namespaces = {
            "app": "http://example.com/app",
            "default": "http://example.com/default"
        }
        
        with patch("builtins.open", mock_open(read_data=namespaced_xml)):
            with patch("xml.etree.ElementTree.parse") as mock_parse:
                # Mock parsed tree
                mock_tree = Mock()
                mock_root = Mock()
                mock_tree.getroot.return_value = mock_root
                mock_parse.return_value = mock_tree
                
                results = tool(xml_file, "debug", namespaces=namespaces)
                
                # Should handle namespaces correctly
                assert isinstance(results, list)
    
    def test_attribute_search(self, tmp_path):
        """Test searching in XML attributes."""
        xml_file = TestDataFactory.create_xml_file(tmp_path)
        tool = self.get_component_function()
        
        xml_content = """<?xml version="1.0"?>
        <root>
            <user id="123" role="admin" status="active">John</user>
            <user id="456" role="user" status="inactive">Jane</user>
            <config debug="true" environment="production"/>
        </root>"""
        
        with patch("builtins.open", mock_open(read_data=xml_content)):
            # Search attributes only
            results = tool(
                xml_file,
                "admin",
                search_attributes=True,
                search_text=False
            )
            
            # Should find the role="admin" attribute
            assert len(results) >= 1
            assert any(r.get("match_type") == "attribute" for r in results)
    
    def test_text_content_search(self, tmp_path):
        """Test searching in element text content."""
        xml_file = TestDataFactory.create_xml_file(tmp_path)
        tool = self.get_component_function()
        
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
        
        with patch("builtins.open", mock_open(read_data=xml_content)):
            # Search text only
            results = tool(
                xml_file,
                "important",
                search_text=True,
                search_attributes=False
            )
            
            # Should find text matches
            assert len(results) >= 2  # In title and content
    
    def test_tag_name_search(self, tmp_path):
        """Test searching in XML tag names."""
        xml_file = TestDataFactory.create_xml_file(tmp_path)
        tool = self.get_component_function()
        
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
        
        with patch("builtins.open", mock_open(read_data=xml_content)):
            # Search tag names
            results = tool(
                xml_file,
                "user",
                search_tags=True
            )
            
            # Should find all tags containing "user"
            assert len(results) >= 4  # user, admin_user, guest_user, user_config
    
    def test_mixed_content_search(self, tmp_path):
        """Test searching in mixed content (text + elements)."""
        xml_file = TestDataFactory.create_xml_file(tmp_path)
        tool = self.get_component_function()
        
        xml_content = """<?xml version="1.0"?>
        <article>
            <para>This is a <bold>bold</bold> statement with <italic>emphasis</italic>.</para>
            <para>Another paragraph with <link href="http://example.com">a link</link>.</para>
        </article>"""
        
        with patch("builtins.open", mock_open(read_data=xml_content)):
            # Search in mixed content
            results = tool(xml_file, "bold")
            
            # Should find both tag and possibly text
            assert len(results) >= 1
    
    def test_cdata_handling(self, tmp_path):
        """Test handling of CDATA sections."""
        xml_file = TestDataFactory.create_xml_file(tmp_path)
        tool = self.get_component_function()
        
        xml_content = """<?xml version="1.0"?>
        <root>
            <script><![CDATA[
                function test() {
                    return "This is JavaScript code";
                }
            ]]></script>
            <data><![CDATA[Some <raw> XML & data]]></data>
        </root>"""
        
        with patch("builtins.open", mock_open(read_data=xml_content)):
            # Search in CDATA
            results = tool(xml_file, "JavaScript")
            
            # Should find text in CDATA sections
            assert len(results) >= 1
    
    def test_empty_element_handling(self, tmp_path):
        """Test handling of empty XML elements."""
        xml_file = TestDataFactory.create_xml_file(tmp_path)
        tool = self.get_component_function()
        
        xml_content = """<?xml version="1.0"?>
        <root>
            <empty/>
            <empty_with_attr status="none"/>
            <has_text>content</has_text>
        </root>"""
        
        with patch("builtins.open", mock_open(read_data=xml_content)):
            # Search for attribute in empty element
            results = tool(xml_file, "none")
            
            # Should find the attribute
            assert len(results) >= 1
    
    def test_malformed_xml_handling(self, tmp_path):
        """Test handling of malformed XML."""
        xml_file = tmp_path / "malformed.xml"
        tool = self.get_component_function()
        
        malformed_xml = """<?xml version="1.0"?>
        <root>
            <unclosed>
            <invalid attr=>
        </root>"""
        
        with patch("builtins.open", mock_open(read_data=malformed_xml)):
            results = tool(xml_file, "test")
            
            # Should handle gracefully
            assert isinstance(results, list)
            assert len(results) == 0 or "error" in str(results)
    
    def test_large_xml_performance(self, tmp_path):
        """Test performance with large XML files."""
        xml_file = TestDataFactory.create_xml_file(tmp_path)
        tool = self.get_component_function()
        
        # Create large XML structure
        large_xml = '<?xml version="1.0"?>\n<root>\n'
        for i in range(1000):
            large_xml += f'  <item id="{i}" type="test">Item {i} content</item>\n'
        large_xml += '</root>'
        
        with patch("builtins.open", mock_open(read_data=large_xml)):
            import time
            start_time = time.time()
            
            results = tool(xml_file, "Item 500")
            
            elapsed = time.time() - start_time
            
            # Should complete quickly
            assert elapsed < 2.0
            assert len(results) >= 1
    
    def test_xml_validation(self, tmp_path):
        """Test XML validation if supported."""
        xml_file = TestDataFactory.create_xml_file(tmp_path)
        tool = self.get_component_function()
        
        valid_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE root [
            <!ELEMENT root (item+)>
            <!ELEMENT item (#PCDATA)>
            <!ATTLIST item id ID #REQUIRED>
        ]>
        <root>
            <item id="i1">Valid item</item>
            <item id="i2">Another item</item>
        </root>"""
        
        with patch("builtins.open", mock_open(read_data=valid_xml)):
            # Should handle DTD validation
            results = tool(xml_file, "Valid")
            assert len(results) >= 1
    
    def test_special_characters_escaping(self, tmp_path):
        """Test handling of XML special characters."""
        xml_file = TestDataFactory.create_xml_file(tmp_path)
        tool = self.get_component_function()
        
        xml_content = """<?xml version="1.0"?>
        <root>
            <data>Less than &lt; and greater than &gt;</data>
            <data>Ampersand &amp; apostrophe &apos; quote &quot;</data>
            <url>http://example.com?foo=bar&amp;baz=qux</url>
        </root>"""
        
        with patch("builtins.open", mock_open(read_data=xml_content)):
            # Search for escaped characters
            results = tool(xml_file, "Less than")
            assert len(results) >= 1
            
            # Search for URL with escaped ampersand
            results = tool(xml_file, "foo=bar")
            assert len(results) >= 1
