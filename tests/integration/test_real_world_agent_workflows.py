"""Real-world agent workflow tests.

Tests complete agent workflows as they would run in production, including:
- Multi-step research and analysis
- Document processing pipelines
- Code generation and validation
- Data extraction and transformation
- Error handling and recovery
"""

import asyncio
import json
import pytest
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, Mock, patch

# We'll simulate the agent workflows without importing the actual agents
# to avoid circular dependencies, but the patterns match real usage


class TestRealWorldAgentWorkflows:
    """Test complete agent workflows in production-like scenarios."""

    @pytest.mark.asyncio
    async def test_complete_research_workflow(self):
        """Test a complete research workflow from query to report.

        Simulates: research_assistant_agent conducting full research.
        """
        # Mock the Mirascope-style agent implementation
        class ResearchAgent:
            def __init__(self):
                self.research_state = {
                    "queries_generated": [],
                    "sources_found": [],
                    "content_analyzed": [],
                    "report_sections": []
                }

            async def generate_search_queries(self, topic: str, num_queries: int = 5) -> list[str]:
                """Generate diverse search queries for comprehensive research."""
                # Simulate LLM generating queries
                base_queries = [
                    f"{topic} latest research 2024",
                    f"{topic} implementation best practices",
                    f"{topic} case studies success stories",
                    f"{topic} challenges and limitations",
                    f"{topic} future trends predictions"
                ]

                self.research_state["queries_generated"] = base_queries[:num_queries]
                return self.research_state["queries_generated"]

            async def search_and_collect(self, queries: list[str]) -> list[dict]:
                """Search for and collect relevant sources."""
                sources = []

                with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                    mock_client = Mock()
                    mock_exa.return_value = mock_client

                    for i, query in enumerate(queries):
                        # Mock search results
                        mock_client.search.return_value = Mock(
                            results=[
                                Mock(
                                    id=f"doc_{i}_1",
                                    url=f"https://example.com/article{i}_1",
                                    title=f"Article about {query.split()[0]}",
                                    text=f"Detailed content about {query}...",
                                    score=0.95 - (i * 0.02),
                                    published_date="2024-01-15",
                                    author=f"Expert {i}"
                                ),
                                Mock(
                                    id=f"doc_{i}_2",
                                    url=f"https://research.com/paper{i}",
                                    title=f"Research paper on {query.split()[0]}",
                                    text=f"Academic research about {query}...",
                                    score=0.90 - (i * 0.02),
                                    published_date="2024-02-01",
                                    author=f"Dr. Researcher {i}"
                                )
                            ]
                        )

                        # Import would happen here in real agent
                        from packages.sygaldry_registry.components.tools.exa_search.tool import (
                            SearchArgs,
                            exa_search,
                        )

                        search_args = SearchArgs(query=query, num_results=5)
                        results = await exa_search(search_args)

                        for result in results.results:
                            sources.append({
                                "query": query,
                                "source": {
                                    "id": getattr(result, 'id', result.url),
                                    "url": result.url,
                                    "title": result.title,
                                    "preview": result.snippet[:200] if result.snippet else "",
                                    "score": result.score,
                                    "date": getattr(result, 'published_date', 'Unknown'),
                                    "author": getattr(result, 'author', 'Unknown')
                                }
                            })

                self.research_state["sources_found"] = sources
                return sources

            async def analyze_sources(self, sources: list[dict]) -> dict:
                """Analyze collected sources for key insights."""
                # Simulate content analysis using code interpreter
                from packages.sygaldry_registry.components.tools.code_interpreter.tool import execute_code

                analysis_code = f"""
import json
from collections import Counter, defaultdict
from datetime import datetime

sources = {json.dumps(sources)}

# Analyze source quality
high_quality_sources = [s for s in sources if s['source']['score'] > 0.9]
recent_sources = [s for s in sources if '2024' in s['source']['date']]

# Extract themes from titles
all_words = []
for source in sources:
    title_words = source['source']['title'].lower().split()
    all_words.extend([w for w in title_words if len(w) > 4])

theme_counts = Counter(all_words)
top_themes = [theme for theme, _ in theme_counts.most_common(5)]

# Group by query type
sources_by_query = defaultdict(list)
for source in sources:
    query_type = source['query'].split()[-1]  # Get last word
    sources_by_query[query_type].append(source['source']['title'])

# Generate insights
insights = {{
    "total_sources": len(sources),
    "high_quality_sources": len(high_quality_sources),
    "recent_sources": len(recent_sources),
    "top_themes": top_themes,
    "coverage": {{
        "research": len([s for s in sources if 'research' in s['query']]),
        "practices": len([s for s in sources if 'practices' in s['query']]),
        "case_studies": len([s for s in sources if 'case' in s['query']]),
        "challenges": len([s for s in sources if 'challenges' in s['query']]),
        "trends": len([s for s in sources if 'trends' in s['query']])
    }}
}}

print("=== Source Analysis ===")
print(json.dumps(insights, indent=2))

# Identify key findings
key_findings = []
if insights['recent_sources'] > len(sources) * 0.6:
    key_findings.append("Most sources are recent (2024), indicating active research area")

if insights['high_quality_sources'] > len(sources) * 0.7:
    key_findings.append("High confidence in source quality (>70% high-quality sources)")

for theme in top_themes[:3]:
    key_findings.append(f"Common theme identified: {{theme}}")

analysis_result = {{
    "insights": insights,
    "key_findings": key_findings,
    "recommendation": "Proceed with comprehensive report generation"
}}
"""

                result = await execute_code(
                    code=analysis_code,
                    capture_variables=True,
                    use_subprocess=False
                )

                if result.success and result.variables.get('analysis_result'):
                    self.research_state["content_analyzed"] = result.variables['analysis_result']
                    return result.variables['analysis_result']

                # Fallback
                return {
                    "insights": {"total_sources": len(sources)},
                    "key_findings": ["Analysis completed"],
                    "recommendation": "Proceed with report"
                }

            async def generate_report(self, topic: str, analysis: dict) -> str:
                """Generate final research report."""
                # Simulate report generation
                from packages.sygaldry_registry.components.tools.code_interpreter.tool import execute_code

                report_code = f"""
import json
from datetime import datetime

topic = "{topic}"
analysis = {json.dumps(analysis)}

# Generate structured report
report = f\"\"\"# Research Report: {{topic}}

**Generated:** {{datetime.now().strftime('%B %d, %Y')}}

## Executive Summary

This comprehensive research report analyzes {{analysis['insights']['total_sources']}} sources
to provide insights into {{topic}}. Our analysis reveals several key themes and trends
in the current landscape.

## Key Findings

\"\"\"

for i, finding in enumerate(analysis['key_findings'], 1):
    report += f"{{i}}. {{finding}}\\n"

report += f\"\"\"

## Research Coverage

Our research covered the following areas:
- Latest Research: {{analysis['insights']['coverage'].get('research', 0)}} sources
- Best Practices: {{analysis['insights']['coverage'].get('practices', 0)}} sources
- Case Studies: {{analysis['insights']['coverage'].get('case_studies', 0)}} sources
- Challenges: {{analysis['insights']['coverage'].get('challenges', 0)}} sources
- Future Trends: {{analysis['insights']['coverage'].get('trends', 0)}} sources

## Thematic Analysis

Top themes identified across all sources:
\"\"\"

for theme in analysis['insights'].get('top_themes', [])[:5]:
    report += f"- {{theme.title()}}\\n"

report += f\"\"\"

## Quality Assessment

- High-quality sources (>90% relevance): {{analysis['insights']['high_quality_sources']}}
- Recent sources (2024): {{analysis['insights']['recent_sources']}}
- Overall confidence level: {{'High' if analysis['insights']['high_quality_sources'] > 5 else 'Medium'}}

## Recommendations

Based on our analysis, we recommend:

1. **Immediate Actions**: Focus on implementing best practices identified in high-quality sources
2. **Further Research**: Explore case studies for practical implementation guidance
3. **Risk Mitigation**: Address challenges identified in research before full implementation
4. **Future Planning**: Monitor trends for upcoming developments

## Conclusion

{{topic}} represents a significant area of interest with substantial research coverage.
The high quality and recency of sources indicate this is an active and evolving field.
Organizations should consider the findings and recommendations in this report when
planning their strategy.

---
*This report analyzed {{analysis['insights']['total_sources']}} sources using automated research tools.*
\"\"\"

print(report)
result = report
"""

                result = await execute_code(
                    code=report_code,
                    capture_variables=True,
                    use_subprocess=False
                )

                if result.success:
                    self.research_state["report_sections"].append({
                        "type": "final_report",
                        "content": result.output
                    })
                    return result.output or "Report generation completed"

                return "Report generation failed"

        # Execute complete workflow
        agent = ResearchAgent()
        topic = "Artificial Intelligence in Healthcare"

        # Step 1: Generate queries
        queries = await agent.generate_search_queries(topic, num_queries=5)
        assert len(queries) == 5
        assert all(topic.lower() in q.lower() for q in queries)

        # Step 2: Search and collect sources
        sources = await agent.search_and_collect(queries)
        assert len(sources) >= 10  # At least 2 per query
        assert all('source' in s and 'query' in s for s in sources)

        # Step 3: Analyze sources
        analysis = await agent.analyze_sources(sources)
        assert 'insights' in analysis
        assert 'key_findings' in analysis
        assert analysis['insights']['total_sources'] == len(sources)

        # Step 4: Generate report
        report = await agent.generate_report(topic, analysis)
        assert "Research Report:" in report
        assert topic in report
        assert "Key Findings" in report
        assert "Recommendations" in report

        # Verify complete workflow state
        assert len(agent.research_state["queries_generated"]) == 5
        assert len(agent.research_state["sources_found"]) >= 10
        assert agent.research_state["content_analyzed"] is not None
        assert len(agent.research_state["report_sections"]) > 0

    @pytest.mark.asyncio
    async def test_code_generation_validation_workflow(self):
        """Test complete code generation and validation workflow.

        Simulates: code_generation_execution_agent creating and testing code.
        """
        class CodeGenerationAgent:
            def __init__(self):
                self.generation_state = {
                    "requirements": [],
                    "generated_code": [],
                    "test_results": [],
                    "final_code": None
                }

            async def analyze_requirements(self, task: str) -> list[str]:
                """Analyze task and extract requirements."""
                # Simulate requirement extraction
                requirements = []

                if "api" in task.lower():
                    requirements.extend([
                        "Create REST API endpoints",
                        "Implement request validation",
                        "Add error handling",
                        "Include authentication"
                    ])

                if "database" in task.lower():
                    requirements.extend([
                        "Design database schema",
                        "Implement CRUD operations",
                        "Add connection pooling",
                        "Include migrations"
                    ])

                self.generation_state["requirements"] = requirements
                return requirements

            async def generate_code(self, requirements: list[str]) -> str:
                """Generate code based on requirements."""
                # Simulate code generation
                code = '''"""Generated API with database integration."""

from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field

# Data Models
class UserModel(BaseModel):
    """User data model."""
    id: Optional[int] = None
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$')
    created_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserDB:
    """Simulated database operations."""
    def __init__(self):
        self.users: Dict[int, UserModel] = {}
        self.next_id = 1

    async def create_user(self, user: UserModel) -> UserModel:
        """Create a new user."""
        user.id = self.next_id
        user.created_at = datetime.now()
        self.users[user.id] = user
        self.next_id += 1
        return user

    async def get_user(self, user_id: int) -> Optional[UserModel]:
        """Get user by ID."""
        return self.users.get(user_id)

    async def list_users(self, limit: int = 10) -> List[UserModel]:
        """List all users."""
        return list(self.users.values())[:limit]

    async def update_user(self, user_id: int, user_data: UserModel) -> Optional[UserModel]:
        """Update user."""
        if user_id in self.users:
            user_data.id = user_id
            user_data.created_at = self.users[user_id].created_at
            self.users[user_id] = user_data
            return user_data
        return None

    async def delete_user(self, user_id: int) -> bool:
        """Delete user."""
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False

# API Implementation
class UserAPI:
    """User API with error handling."""
    def __init__(self):
        self.db = UserDB()

    async def create_user_endpoint(self, user_data: dict) -> dict:
        """Create user endpoint."""
        try:
            user = UserModel(**user_data)
            created_user = await self.db.create_user(user)
            return {
                "success": True,
                "data": created_user.dict(),
                "message": "User created successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create user"
            }

    async def get_user_endpoint(self, user_id: int) -> dict:
        """Get user endpoint."""
        user = await self.db.get_user(user_id)
        if user:
            return {
                "success": True,
                "data": user.dict()
            }
        return {
            "success": False,
            "error": "User not found",
            "status_code": 404
        }

# Usage example
async def demo():
    """Demonstrate API usage."""
    api = UserAPI()

    # Create user
    result = await api.create_user_endpoint({
        "username": "testuser",
        "email": "test@example.com"
    })
    print(f"Create result: {result}")

    # Get user
    if result["success"]:
        user_id = result["data"]["id"]
        get_result = await api.get_user_endpoint(user_id)
        print(f"Get result: {get_result}")

    return api

# Run demo
import asyncio
api = asyncio.run(demo())
'''

                self.generation_state["generated_code"].append({
                    "version": len(self.generation_state["generated_code"]) + 1,
                    "code": code,
                    "timestamp": datetime.now().isoformat()
                })

                return code

            async def validate_code(self, code: str) -> dict:
                """Validate generated code."""
                from packages.sygaldry_registry.components.tools.code_interpreter.tool import (
                    execute_code,
                    validate_code as validate_syntax,
                )

                # Syntax validation
                is_valid, error = validate_syntax(code)
                if not is_valid:
                    return {
                        "valid": False,
                        "error": error,
                        "tests_passed": 0
                    }

                # Execute and test
                result = await execute_code(
                    code=code,
                    timeout_seconds=5,
                    capture_variables=True,
                    use_subprocess=False
                )

                if not result.success:
                    return {
                        "valid": False,
                        "error": result.error,
                        "tests_passed": 0
                    }

                # Validate output
                tests_passed = 0
                if result.output and "Create result:" in result.output:
                    tests_passed += 1
                if result.output and "Get result:" in result.output:
                    tests_passed += 1
                if result.output and "'success': True" in result.output:
                    tests_passed += 1

                validation_result = {
                    "valid": True,
                    "tests_passed": tests_passed,
                    "total_tests": 3,
                    "output": result.output,
                    "api_instance": result.variables.get('api') is not None
                }

                self.generation_state["test_results"].append(validation_result)
                return validation_result

            async def refine_code(self, code: str, validation_result: dict) -> str:
                """Refine code based on validation results."""
                if validation_result["valid"] and validation_result["tests_passed"] == validation_result["total_tests"]:
                    # Code is good
                    self.generation_state["final_code"] = code
                    return code

                # In real implementation, would use LLM to refine
                # For now, return the original code
                self.generation_state["final_code"] = code
                return code

        # Execute workflow
        agent = CodeGenerationAgent()
        task = "Create a REST API with database operations for user management"

        # Step 1: Analyze requirements
        requirements = await agent.analyze_requirements(task)
        assert len(requirements) > 0
        assert any("API" in r for r in requirements)

        # Step 2: Generate code
        generated_code = await agent.generate_code(requirements)
        assert "class UserModel" in generated_code
        assert "async def create_user" in generated_code

        # Step 3: Validate code
        validation = await agent.validate_code(generated_code)
        assert validation["valid"] is True
        assert validation["tests_passed"] > 0

        # Step 4: Refine if needed
        final_code = await agent.refine_code(generated_code, validation)
        assert final_code is not None

        # Verify workflow completion
        assert len(agent.generation_state["requirements"]) > 0
        assert len(agent.generation_state["generated_code"]) > 0
        assert len(agent.generation_state["test_results"]) > 0
        assert agent.generation_state["final_code"] is not None

    @pytest.mark.asyncio
    async def test_document_processing_pipeline(self):
        """Test complete document processing pipeline.

        Simulates: document_segmentation_agent processing complex documents.
        """
        class DocumentProcessor:
            def __init__(self):
                self.processing_state = {
                    "document_structure": None,
                    "segments": [],
                    "metadata": {},
                    "embeddings": []
                }

            async def analyze_structure(self, document: str) -> dict:
                """Analyze document structure."""
                from packages.sygaldry_registry.components.tools.code_interpreter.tool import execute_code

                analysis_code = f'''
import re
from collections import defaultdict

document = """{document}"""

# Analyze structure
lines = document.split('\\n')
structure = {{
    "total_lines": len(lines),
    "sections": [],
    "paragraphs": 0,
    "headers": []
}}

current_section = None
for i, line in enumerate(lines):
    # Detect headers
    if line.startswith('#'):
        level = len(line.split()[0])
        header_text = line.strip('#').strip()
        structure["headers"].append({{
            "level": level,
            "text": header_text,
            "line": i
        }})
        current_section = header_text
        structure["sections"].append({{
            "title": header_text,
            "start_line": i,
            "content": []
        }})

    # Count paragraphs
    elif line.strip() and not line.startswith('#'):
        structure["paragraphs"] += 1
        if structure["sections"]:
            structure["sections"][-1]["content"].append(line)

# Calculate statistics
structure["avg_section_length"] = (
    sum(len(s["content"]) for s in structure["sections"]) / len(structure["sections"])
    if structure["sections"] else 0
)

structure["hierarchy"] = {{
    f"Level {{i}}": len([h for h in structure["headers"] if h["level"] == i])
    for i in range(1, 5)
}}

print(f"Document structure analyzed:")
print(f"- Sections: {{len(structure['sections'])}}")
print(f"- Headers: {{len(structure['headers'])}}")
print(f"- Paragraphs: {{structure['paragraphs']}}")

result = structure
'''

                result = await execute_code(
                    code=analysis_code,
                    capture_variables=True,
                    use_subprocess=False
                )

                if result.success and result.variables.get('result'):
                    self.processing_state["document_structure"] = result.variables['result']
                    return result.variables['result']

                return {"sections": [], "headers": [], "paragraphs": 0}

            async def segment_document(self, document: str, structure: dict) -> list[dict]:
                """Segment document based on structure."""
                segments = []
                lines = document.split('\n')

                # Create segments based on sections
                for i, section in enumerate(structure.get("sections", [])):
                    start_line = section["start_line"]

                    # Find end line (next section or end of document)
                    if i + 1 < len(structure["sections"]):
                        end_line = structure["sections"][i + 1]["start_line"]
                    else:
                        end_line = len(lines)

                    segment_content = '\n'.join(lines[start_line:end_line])

                    segments.append({
                        "id": f"segment_{i}",
                        "type": "section",
                        "title": section["title"],
                        "content": segment_content,
                        "metadata": {
                            "start_line": start_line,
                            "end_line": end_line,
                            "word_count": len(segment_content.split()),
                            "char_count": len(segment_content)
                        }
                    })

                self.processing_state["segments"] = segments
                return segments

            async def extract_metadata(self, segments: list[dict]) -> dict:
                """Extract metadata from segments."""
                from packages.sygaldry_registry.components.tools.code_interpreter.tool import execute_code

                metadata_code = f"""
import json
from datetime import datetime

segments = {json.dumps(segments)}

# Extract metadata
metadata = {{
    "document_stats": {{
        "total_segments": len(segments),
        "total_words": sum(s["metadata"]["word_count"] for s in segments),
        "total_chars": sum(s["metadata"]["char_count"] for s in segments),
        "avg_segment_length": sum(s["metadata"]["word_count"] for s in segments) / len(segments) if segments else 0
    }},
    "segment_types": {{
        "sections": len([s for s in segments if s["type"] == "section"]),
        "paragraphs": len([s for s in segments if s["type"] == "paragraph"])
    }},
    "processing_info": {{
        "processed_at": datetime.now().isoformat(),
        "version": "1.0"
    }}
}}

# Identify key segments
key_segments = []
for segment in segments:
    if any(keyword in segment["title"].lower() for keyword in ["introduction", "summary", "conclusion", "abstract"]):
        key_segments.append({{
            "id": segment["id"],
            "title": segment["title"],
            "importance": "high"
        }})

metadata["key_segments"] = key_segments

print("=== Document Metadata ===")
print(json.dumps(metadata, indent=2))

result = metadata
"""

                result = await execute_code(
                    code=metadata_code,
                    capture_variables=True,
                    use_subprocess=False
                )

                if result.success and result.variables.get('result'):
                    self.processing_state["metadata"] = result.variables['result']
                    return result.variables['result']

                return {"document_stats": {}, "segment_types": {}}

            async def generate_embeddings(self, segments: list[dict]) -> list[dict]:
                """Generate embeddings for segments (simulated)."""
                # In production, would use actual embedding model
                embeddings = []

                for segment in segments:
                    # Simulate embedding generation
                    embedding = {
                        "segment_id": segment["id"],
                        "embedding": [0.1 * i for i in range(10)],  # Mock 10-dim embedding
                        "model": "text-embedding-mock",
                        "timestamp": datetime.now().isoformat()
                    }
                    embeddings.append(embedding)

                self.processing_state["embeddings"] = embeddings
                return embeddings

        # Test document
        test_document = """# Research Report on Machine Learning

## Introduction

Machine learning has revolutionized how we approach complex problems in various domains.
This report provides a comprehensive overview of current trends and applications.

## Background

The field of machine learning has evolved significantly over the past decade.
From simple linear models to complex neural networks, the progression has been remarkable.

### Historical Context

Early machine learning algorithms focused on pattern recognition and statistical analysis.
The introduction of deep learning marked a paradigm shift in capabilities.

## Current Applications

### Healthcare

Machine learning is transforming healthcare through:
- Disease prediction and diagnosis
- Drug discovery and development
- Personalized treatment plans

### Finance

Financial institutions leverage ML for:
- Fraud detection
- Risk assessment
- Algorithmic trading

## Future Directions

The future of machine learning looks promising with advances in:
- Explainable AI
- Federated learning
- Quantum machine learning

## Conclusion

Machine learning continues to be a driving force in technological advancement.
Its applications will only expand as the technology matures.
"""

        # Execute pipeline
        processor = DocumentProcessor()

        # Step 1: Analyze structure
        structure = await processor.analyze_structure(test_document)
        assert len(structure["sections"]) > 0
        assert len(structure["headers"]) > 0
        assert structure["paragraphs"] > 0

        # Step 2: Segment document
        segments = await processor.segment_document(test_document, structure)
        assert len(segments) == len(structure["sections"])
        assert all("content" in s for s in segments)

        # Step 3: Extract metadata
        metadata = await processor.extract_metadata(segments)
        assert "document_stats" in metadata
        assert metadata["document_stats"]["total_segments"] == len(segments)

        # Step 4: Generate embeddings
        embeddings = await processor.generate_embeddings(segments)
        assert len(embeddings) == len(segments)
        assert all("embedding" in e for e in embeddings)

        # Verify complete pipeline
        assert processor.processing_state["document_structure"] is not None
        assert len(processor.processing_state["segments"]) > 0
        assert processor.processing_state["metadata"] is not None
        assert len(processor.processing_state["embeddings"]) > 0

    @pytest.mark.asyncio
    async def test_knowledge_extraction_workflow(self):
        """Test knowledge extraction and graph building workflow.

        Simulates: knowledge_graph_agent extracting entities and relationships.
        """
        class KnowledgeExtractor:
            def __init__(self):
                self.extraction_state = {
                    "entities": [],
                    "relationships": [],
                    "graph": None,
                    "insights": []
                }

            async def extract_entities(self, text: str) -> list[dict]:
                """Extract entities from text."""
                from packages.sygaldry_registry.components.tools.code_interpreter.tool import execute_code

                extraction_code = f'''
import re
from collections import defaultdict

text = """{text}"""

# Simple entity extraction (in production would use NER)
entities = []

# Extract company names (capitalized words)
company_pattern = r'\\b[A-Z][a-z]+(?:\\s+[A-Z][a-z]+)*\\b'
companies = re.findall(company_pattern, text)
for company in set(companies):
    if len(company) > 3:  # Filter out short matches
        entities.append({{
            "id": f"company_{{len(entities)}}",
            "type": "Organization",
            "name": company,
            "mentions": text.count(company)
        }})

# Extract technologies (specific keywords)
tech_keywords = ["AI", "machine learning", "deep learning", "neural network",
                 "data science", "cloud computing", "blockchain", "IoT"]
for tech in tech_keywords:
    if tech.lower() in text.lower():
        entities.append({{
            "id": f"tech_{{len(entities)}}",
            "type": "Technology",
            "name": tech,
            "mentions": text.lower().count(tech.lower())
        }})

# Extract metrics/numbers
number_pattern = r'\\b\\d+(?:\\.\\d+)?%?\\b'
numbers = re.findall(number_pattern, text)
for num in set(numbers):
    if len(num) > 1:  # Skip single digits
        entities.append({{
            "id": f"metric_{{len(entities)}}",
            "type": "Metric",
            "value": num,
            "mentions": text.count(num)
        }})

print(f"Extracted {{len(entities)}} entities")
for e in entities[:5]:  # Show first 5
    print(f"- {{e['type']}}: {{e.get('name', e.get('value', 'Unknown'))}}")

result = entities
'''

                result = await execute_code(
                    code=extraction_code,
                    capture_variables=True,
                    use_subprocess=False
                )

                if result.success and result.variables.get('result'):
                    self.extraction_state["entities"] = result.variables['result']
                    return result.variables['result']

                return []

            async def extract_relationships(self, text: str, entities: list[dict]) -> list[dict]:
                """Extract relationships between entities."""
                relationships: list[dict] = []

                # Simple relationship extraction based on proximity
                entity_names = [e.get('name', e.get('value', '')) for e in entities]

                sentences = text.split('.')
                for sentence in sentences:
                    # Find entities mentioned in same sentence
                    mentioned = []
                    for i, entity in enumerate(entities):
                        entity_text = entity.get('name', entity.get('value', ''))
                        if entity_text and entity_text in sentence:
                            mentioned.append(i)

                    # Create relationships for co-mentioned entities
                    if len(mentioned) >= 2:
                        for i in range(len(mentioned)-1):
                            for j in range(i+1, len(mentioned)):
                                relationships.append({
                                    "id": f"rel_{len(relationships)}",
                                    "source": entities[mentioned[i]]["id"],
                                    "target": entities[mentioned[j]]["id"],
                                    "type": "related_to",
                                    "context": sentence.strip()[:100] + "..."
                                })

                self.extraction_state["relationships"] = relationships
                return relationships

            async def build_knowledge_graph(self, entities: list[dict], relationships: list[dict]) -> dict:
                """Build knowledge graph from entities and relationships."""
                from packages.sygaldry_registry.components.tools.code_interpreter.tool import execute_code

                graph_code = f"""
import json
from collections import defaultdict

entities = {json.dumps(entities)}
relationships = {json.dumps(relationships)}

# Build graph structure
graph = {{
    "nodes": entities,
    "edges": relationships,
    "statistics": {{
        "total_entities": len(entities),
        "total_relationships": len(relationships),
        "entity_types": {{}},
        "relationship_types": {{}}
    }}
}}

# Calculate statistics
for entity in entities:
    entity_type = entity.get("type", "Unknown")
    graph["statistics"]["entity_types"][entity_type] = \
        graph["statistics"]["entity_types"].get(entity_type, 0) + 1

for rel in relationships:
    rel_type = rel.get("type", "Unknown")
    graph["statistics"]["relationship_types"][rel_type] = \
        graph["statistics"]["relationship_types"].get(rel_type, 0) + 1

# Find most connected entities
entity_connections = defaultdict(int)
for rel in relationships:
    entity_connections[rel["source"]] += 1
    entity_connections[rel["target"]] += 1

if entity_connections:
    most_connected = max(entity_connections.items(), key=lambda x: x[1])
    most_connected_entity = next(
        (e for e in entities if e["id"] == most_connected[0]),
        None
    )
    graph["insights"] = {{
        "most_connected_entity": most_connected_entity,
        "connection_count": most_connected[1]
    }}

print("=== Knowledge Graph Built ===")
print(json.dumps(graph["statistics"], indent=2))

result = graph
"""

                result = await execute_code(
                    code=graph_code,
                    capture_variables=True,
                    use_subprocess=False
                )

                if result.success and result.variables.get('result'):
                    self.extraction_state["graph"] = result.variables['result']
                    return result.variables['result']

                return {"nodes": entities, "edges": relationships, "statistics": {}}

            async def generate_insights(self, graph: dict) -> list[str]:
                """Generate insights from knowledge graph."""
                insights = []

                # Basic insights
                stats = graph.get("statistics", {})

                if stats.get("total_entities", 0) > 10:
                    insights.append(f"Rich knowledge base with {stats['total_entities']} entities identified")

                if stats.get("total_relationships", 0) > 5:
                    insights.append(f"Complex interconnections with {stats['total_relationships']} relationships")

                # Entity type insights
                entity_types = stats.get("entity_types", {})
                if "Technology" in entity_types and entity_types["Technology"] > 3:
                    insights.append("Strong technology focus in the content")

                if "Organization" in entity_types and entity_types["Organization"] > 2:
                    insights.append("Multiple organizations mentioned, indicating industry relevance")

                # Connectivity insights
                if "insights" in graph and graph["insights"].get("most_connected_entity"):
                    entity = graph["insights"]["most_connected_entity"]
                    insights.append(
                        f"Central concept: {entity.get('name', 'Unknown')} "
                        f"with {graph['insights']['connection_count']} connections"
                    )

                self.extraction_state["insights"] = insights
                return insights

        # Test text
        test_text = """
        Apple and Google are leading the AI revolution with their latest developments.
        Machine learning has become central to their strategies, with investments exceeding 20%.
        Microsoft has also joined the race with their Azure AI platform achieving 95% accuracy.

        The collaboration between OpenAI and Microsoft has resulted in breakthrough technologies.
        Deep learning models are now capable of processing millions of parameters.
        Google's TensorFlow and Facebook's PyTorch remain the most popular frameworks.

        Industry reports show that 75% of enterprises are adopting AI solutions.
        Cloud computing infrastructure supports these massive computational requirements.
        The market is expected to reach $500 billion by 2025.
        """

        # Execute workflow
        extractor = KnowledgeExtractor()

        # Step 1: Extract entities
        entities = await extractor.extract_entities(test_text)
        assert len(entities) > 0
        assert any(e["type"] == "Organization" for e in entities)
        assert any(e["type"] == "Technology" for e in entities)

        # Step 2: Extract relationships
        relationships = await extractor.extract_relationships(test_text, entities)
        assert len(relationships) > 0

        # Step 3: Build knowledge graph
        graph = await extractor.build_knowledge_graph(entities, relationships)
        assert "nodes" in graph
        assert "edges" in graph
        assert "statistics" in graph

        # Step 4: Generate insights
        insights = await extractor.generate_insights(graph)
        assert len(insights) > 0

        # Verify complete workflow
        assert len(extractor.extraction_state["entities"]) > 0
        assert len(extractor.extraction_state["relationships"]) > 0
        assert extractor.extraction_state["graph"] is not None
        assert len(extractor.extraction_state["insights"]) > 0
