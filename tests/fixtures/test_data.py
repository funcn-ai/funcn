"""Test data fixtures for common file formats and scenarios."""

import base64
import json
from pathlib import Path
from typing import Any

# Sample text content
SAMPLE_TEXT = """# Introduction to Artificial Intelligence

Artificial Intelligence (AI) represents one of the most transformative technologies of our time.
This document explores the fundamental concepts, applications, and implications of AI in modern society.

## Key Concepts

1. **Machine Learning**: The ability of systems to learn from data
2. **Neural Networks**: Computational models inspired by the human brain
3. **Natural Language Processing**: Understanding and generating human language
4. **Computer Vision**: Interpreting and analyzing visual information

## Applications

AI is being applied across numerous domains:
- Healthcare: Disease diagnosis and drug discovery
- Finance: Fraud detection and algorithmic trading
- Transportation: Autonomous vehicles and traffic optimization
- Education: Personalized learning and automated grading

## Future Implications

As AI continues to advance, we must consider both its potential benefits and risks.
Ethical considerations, privacy concerns, and the impact on employment are critical areas of discussion.

## Conclusion

The future of AI is both exciting and challenging, requiring thoughtful development and regulation.
"""

# Sample CSV data
SAMPLE_CSV = """name,age,email,department,salary
John Smith,35,john.smith@company.com,Engineering,95000
Jane Doe,28,jane.doe@company.com,Marketing,75000
Bob Johnson,42,bob.johnson@company.com,Sales,85000
Alice Williams,31,alice.williams@company.com,Engineering,92000
Charlie Brown,39,charlie.brown@company.com,HR,70000
Diana Prince,45,diana.prince@company.com,Executive,150000
Edward Norton,26,edward.norton@company.com,Engineering,80000
Fiona Apple,33,fiona.apple@company.com,Design,78000
George Lucas,50,george.lucas@company.com,Product,110000
Helen Hunt,29,helen.hunt@company.com,Marketing,72000"""

# Sample JSON data
SAMPLE_JSON = {
    "project": {
        "name": "AI Assistant Development",
        "version": "2.1.0",
        "description": "An advanced AI assistant for task automation",
        "team": {
            "lead": "Dr. Sarah Chen",
            "members": [
                {"name": "John Developer", "role": "Senior Engineer"},
                {"name": "Jane Designer", "role": "UX Designer"},
                {"name": "Bob Analyst", "role": "Data Scientist"},
            ],
        },
        "milestones": [
            {
                "id": 1,
                "title": "MVP Release",
                "date": "2024-03-15",
                "status": "completed",
                "features": ["Basic chat", "File upload", "User auth"],
            },
            {
                "id": 2,
                "title": "Advanced Features",
                "date": "2024-06-01",
                "status": "in_progress",
                "features": ["Voice input", "Multi-language", "API integration"],
            },
        ],
        "technologies": {
            "backend": ["Python", "FastAPI", "PostgreSQL"],
            "frontend": ["React", "TypeScript", "TailwindCSS"],
            "ml": ["PyTorch", "Transformers", "LangChain"],
        },
    }
}

# Sample XML data
SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<catalog>
    <book id="bk101">
        <author>Gambardella, Matthew</author>
        <title>XML Developer's Guide</title>
        <genre>Computer</genre>
        <price>44.95</price>
        <publish_date>2000-10-01</publish_date>
        <description>An in-depth look at creating applications with XML.</description>
    </book>
    <book id="bk102">
        <author>Ralls, Kim</author>
        <title>Midnight Rain</title>
        <genre>Fantasy</genre>
        <price>5.95</price>
        <publish_date>2000-12-16</publish_date>
        <description>A former architect battles corporate zombies.</description>
    </book>
    <book id="bk103">
        <author>Corets, Eva</author>
        <title>Maeve Ascendant</title>
        <genre>Fantasy</genre>
        <price>5.95</price>
        <publish_date>2000-11-17</publish_date>
        <description>After the collapse of a nanotechnology society.</description>
    </book>
</catalog>"""

# Sample MDX content
SAMPLE_MDX = """---
title: Getting Started with React Components
author: Jane Developer
date: 2024-01-15
tags: [react, javascript, tutorial]
---

import { CodeBlock } from './components/CodeBlock'
import { Alert } from './components/Alert'

# Getting Started with React Components

React components are the building blocks of any React application. Let's explore how to create and use them effectively.

<Alert type="info">
  This guide assumes basic knowledge of JavaScript and HTML.
</Alert>

## Functional Components

The simplest way to define a component is to write a JavaScript function:

<CodeBlock language="jsx">
{`function Welcome(props) {
  return <h1>Hello, {props.name}!</h1>;
}`}
</CodeBlock>

## Class Components

You can also use ES6 classes to define components:

<CodeBlock language="jsx">
{`class Welcome extends React.Component {
  render() {
    return <h1>Hello, {this.props.name}!</h1>;
  }
}`}
</CodeBlock>

## Next Steps

Now that you understand the basics, try creating your own components!
"""

# Sample Python code
SAMPLE_PYTHON_CODE = '''"""Sample Python module for testing."""

import asyncio
from typing import List, Optional

from pydantic import BaseModel


class User(BaseModel):
    """User model for the application."""

    id: int
    name: str
    email: str
    is_active: bool = True
    tags: List[str] = []


class UserService:
    """Service for managing users."""

    def __init__(self):
        self.users: Dict[int, User] = {}
        self._next_id = 1

    async def create_user(self, name: str, email: str) -> User:
        """Create a new user.

        Args:
            name: User's full name
            email: User's email address

        Returns:
            Created user object
        """
        user = User(
            id=self._next_id,
            name=name,
            email=email
        )
        self.users[user.id] = user
        self._next_id += 1

        # Simulate async operation
        await asyncio.sleep(0.1)
        return user

    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID.

        Args:
            user_id: The user's ID

        Returns:
            User object if found, None otherwise
        """
        await asyncio.sleep(0.05)
        return self.users.get(user_id)

    def list_users(self) -> List[User]:
        """List all users.

        Returns:
            List of all users
        """
        return list(self.users.values())
'''

# Sample YAML data
SAMPLE_YAML = """
name: AI Research Project
version: 1.0.0
description: Advanced AI research and development

team:
  lead: Dr. Sarah Chen
  members:
    - name: John Developer
      role: Senior Engineer
      skills:
        - Python
        - Machine Learning
        - DevOps
    - name: Jane Designer
      role: UX Designer
      skills:
        - Figma
        - User Research
        - Prototyping

environment:
  development:
    database: postgresql://localhost:5432/ai_dev
    redis: redis://localhost:6379/0
    debug: true

  production:
    database: ${DATABASE_URL}
    redis: ${REDIS_URL}
    debug: false

features:
  - name: Natural Language Processing
    status: active
    components:
      - tokenizer
      - embeddings
      - transformer

  - name: Computer Vision
    status: planned
    components:
      - image_processor
      - object_detection
      - segmentation
"""

# Sample Markdown with code blocks
SAMPLE_MARKDOWN_CODE = """# API Documentation

## Authentication

All API requests require authentication using Bearer tokens.

```bash
curl -X GET https://api.example.com/users \\
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Endpoints

### Get User

Retrieve user information by ID.

```python
import requests

response = requests.get(
    "https://api.example.com/users/123",
    headers={"Authorization": f"Bearer {token}"}
)

user = response.json()
print(f"User: {user['name']}")
```

### Create User

Create a new user account.

```javascript
const createUser = async (userData) => {
  const response = await fetch('https://api.example.com/users', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(userData)
  });

  return response.json();
};
```

## Error Handling

The API returns standard HTTP status codes:

| Code | Description |
|------|-------------|
| 200  | Success |
| 400  | Bad Request |
| 401  | Unauthorized |
| 404  | Not Found |
| 500  | Server Error |
"""

# Binary data samples (base64 encoded)
# Small 1x1 pixel PNG
SAMPLE_PNG_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

# Simple PDF content (base64)
SAMPLE_PDF_BASE64 = "JVBERi0xLjMKJeLjz9MKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovT3V0bGluZXMgMiAwIFIKL1BhZ2VzIDMgMCBSCj4+CmVuZG9iagoyIDAgb2JqCjw8Ci9UeXBlIC9PdXRsaW5lcwovQ291bnQgMAo+PgplbmRvYmoKMyAwIG9iago8PAovVHlwZSAvUGFnZXMKL0NvdW50IDEKL0tpZHMgWzQgMCBSXQo+PgplbmRvYmoKNCAwIG9iago8PAovVHlwZSAvUGFnZQovUGFyZW50IDMgMCBSCi9NZWRpYUJveCBbMCAwIDYxMiA3OTJdCi9Db250ZW50cyA1IDAgUgovUmVzb3VyY2VzIDw8Ci9Gb250IDw8Ci9GMSA2IDAgUgo+Pgo+Pgo+PgplbmRvYmoKNSAwIG9iago8PAovTGVuZ3RoIDQ0Cj4+CnN0cmVhbQpCVApxCjcwIDUwIFRECi9GMSAxMiBUZgooSGVsbG8gV29ybGQpIFRqCkVUClEKZW5kc3RyZWFtCmVuZG9iago2IDAgb2JqCjw8Ci9UeXBlIC9Gb250Ci9TdWJ0eXBlIC9UeXBlMQovQmFzZUZvbnQgL0hlbHZldGljYQo+PgplbmRvYmoKeHJlZgowIDcKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNjggMDAwMDAgbiAKMDAwMDAwMDExNyAwMDAwMCBuIAowMDAwMDAwMTc0IDAwMDAwIG4gCjAwMDAwMDAzMTMgMDAwMDAgbiAKMDAwMDAwMDQwNyAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDcKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjQ5MgolJUVPRg=="


class TestDataFactory:
    """Factory for creating test data files."""

    @staticmethod
    def create_text_file(tmp_path: Path, filename: str = "test.txt") -> Path:
        """Create a text file with sample content."""
        file_path = tmp_path / filename
        file_path.write_text(SAMPLE_TEXT)
        return file_path

    @staticmethod
    def create_csv_file(tmp_path: Path, filename: str = "test.csv") -> Path:
        """Create a CSV file with sample data."""
        file_path = tmp_path / filename
        file_path.write_text(SAMPLE_CSV)
        return file_path

    @staticmethod
    def create_json_file(tmp_path: Path, filename: str = "test.json") -> Path:
        """Create a JSON file with sample data."""
        file_path = tmp_path / filename
        with open(file_path, "w") as f:
            json.dump(SAMPLE_JSON, f, indent=2)
        return file_path

    @staticmethod
    def create_xml_file(tmp_path: Path, filename: str = "test.xml") -> Path:
        """Create an XML file with sample data."""
        file_path = tmp_path / filename
        file_path.write_text(SAMPLE_XML)
        return file_path

    @staticmethod
    def create_mdx_file(tmp_path: Path, filename: str = "test.mdx") -> Path:
        """Create an MDX file with sample content."""
        file_path = tmp_path / filename
        file_path.write_text(SAMPLE_MDX)
        return file_path

    @staticmethod
    def create_python_file(tmp_path: Path, filename: str = "test.py") -> Path:
        """Create a Python file with sample code."""
        file_path = tmp_path / filename
        file_path.write_text(SAMPLE_PYTHON_CODE)
        return file_path

    @staticmethod
    def create_yaml_file(tmp_path: Path, filename: str = "test.yaml") -> Path:
        """Create a YAML file with sample data."""
        file_path = tmp_path / filename
        file_path.write_text(SAMPLE_YAML)
        return file_path

    @staticmethod
    def create_markdown_file(tmp_path: Path, filename: str = "test.md") -> Path:
        """Create a Markdown file with code blocks."""
        file_path = tmp_path / filename
        file_path.write_text(SAMPLE_MARKDOWN_CODE)
        return file_path

    @staticmethod
    def create_png_file(tmp_path: Path, filename: str = "test.png") -> Path:
        """Create a PNG image file."""
        file_path = tmp_path / filename
        file_path.write_bytes(base64.b64decode(SAMPLE_PNG_BASE64))
        return file_path

    @staticmethod
    def create_pdf_file(tmp_path: Path, filename: str = "test.pdf") -> Path:
        """Create a PDF file."""
        file_path = tmp_path / filename
        file_path.write_bytes(base64.b64decode(SAMPLE_PDF_BASE64))
        return file_path

    @staticmethod
    def create_directory_structure(tmp_path: Path) -> dict[str, Path]:
        """Create a sample directory structure with various files."""
        # Create directories
        dirs = {
            "root": tmp_path,
            "docs": tmp_path / "docs",
            "src": tmp_path / "src",
            "tests": tmp_path / "tests",
            "data": tmp_path / "data",
            "config": tmp_path / "config",
        }

        for dir_path in dirs.values():
            dir_path.mkdir(exist_ok=True)

        # Create files in different directories
        files = {
            "readme": TestDataFactory.create_markdown_file(dirs["root"], "README.md"),
            "main_py": TestDataFactory.create_python_file(dirs["src"], "main.py"),
            "test_py": TestDataFactory.create_python_file(dirs["tests"], "test_main.py"),
            "config_json": TestDataFactory.create_json_file(dirs["config"], "config.json"),
            "config_yaml": TestDataFactory.create_yaml_file(dirs["config"], "settings.yaml"),
            "data_csv": TestDataFactory.create_csv_file(dirs["data"], "users.csv"),
            "data_json": TestDataFactory.create_json_file(dirs["data"], "products.json"),
            "doc_md": TestDataFactory.create_markdown_file(dirs["docs"], "api.md"),
            "doc_mdx": TestDataFactory.create_mdx_file(dirs["docs"], "guide.mdx"),
        }

        return {**dirs, **files}

    @staticmethod
    def get_sample_search_queries() -> list[dict[str, Any]]:
        """Get sample search queries for testing search tools."""
        return [
            {"query": "artificial intelligence", "expected_in_results": ["AI", "machine learning", "neural networks"]},
            {"query": "user.email", "expected_in_results": ["@company.com", "email"]},
            {"query": "class User", "expected_in_results": ["BaseModel", "pydantic"]},
            {"query": "price > 10", "expected_in_results": ["44.95"]},
        ]
