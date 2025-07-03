"""MDX Search Tool for searching MDX documentation files with JSX component support."""

import aiofiles
import ast
import asyncio
import frontmatter
import markdown
import re
from dataclasses import dataclass
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Any, Literal, Optional


class MDXComponent(BaseModel):
    """Represents a JSX component found in MDX."""

    name: str = Field(..., description="Component name")
    props: dict[str, Any] = Field(default_factory=dict, description="Component props")
    children: str | None = Field(None, description="Component children/content")
    line_number: int = Field(..., description="Line number where component appears")
    raw_content: str = Field(..., description="Raw component content")


class MDXMatch(BaseModel):
    """Represents a match found in MDX documentation."""

    file_path: str = Field(..., description="Path to the MDX file")
    title: str | None = Field(None, description="Document title from frontmatter")
    section: str | None = Field(None, description="Section heading where match was found")
    content: str = Field(..., description="Matched content")
    match_type: Literal["content", "heading", "code", "component", "frontmatter"] = Field(..., description="Type of match")
    line_number: int = Field(..., description="Line number of match")
    relevance_score: float = Field(..., description="Relevance score (0-1)")
    frontmatter: dict[str, Any] = Field(default_factory=dict, description="Document frontmatter")
    context: str | None = Field(None, description="Surrounding context")
    components: list[MDXComponent] = Field(default_factory=list, description="JSX components in matched section")


class MDXSearchResult(BaseModel):
    """Result of MDX search operation."""

    success: bool = Field(..., description="Whether the search was successful")
    query: str = Field(..., description="The search query")
    total_matches: int = Field(..., description="Total number of matches")
    matches: list[MDXMatch] = Field(default_factory=list, description="List of matches")
    files_searched: int = Field(0, description="Number of files searched")
    search_time: float = Field(..., description="Search time in seconds")
    error: str | None = Field(None, description="Error message if search failed")
    unique_components: list[str] = Field(default_factory=list, description="Unique component names found")


def parse_jsx_component(text: str, start_line: int = 0) -> list[MDXComponent]:
    """Parse JSX components from text."""
    components = []

    # Regex patterns for JSX components
    # Self-closing components: <Component prop="value" />
    self_closing_pattern = r'<([A-Z][A-Za-z0-9]*)\s*([^>]*?)\s*/>'
    # Opening tags: <Component prop="value">
    opening_pattern = r'<([A-Z][A-Za-z0-9]*)\s*([^>]*?)>'
    # Closing tags: </Component>
    closing_pattern = r'</([A-Z][A-Za-z0-9]*)>'

    lines = text.split('\n')

    for i, line in enumerate(lines):
        # Find self-closing components
        for match in re.finditer(self_closing_pattern, line):
            component_name = match.group(1)
            props_string = match.group(2)
            props = parse_component_props(props_string)

            components.append(
                MDXComponent(
                    name=component_name, props=props, children=None, line_number=start_line + i + 1, raw_content=match.group(0)
                )
            )

        # Find opening components (simplified - doesn't handle nested components perfectly)
        for match in re.finditer(opening_pattern, line):
            component_name = match.group(1)
            props_string = match.group(2)
            props = parse_component_props(props_string)

            # Try to find the closing tag
            closing_line = i
            component_content = []
            for j in range(i, min(i + 50, len(lines))):  # Look ahead up to 50 lines
                if re.search(f'</{component_name}>', lines[j]):
                    closing_line = j
                    break
                if j > i:
                    component_content.append(lines[j])

            components.append(
                MDXComponent(
                    name=component_name,
                    props=props,
                    children='\n'.join(component_content) if component_content else None,
                    line_number=start_line + i + 1,
                    raw_content=match.group(0),
                )
            )

    return components


def parse_component_props(props_string: str) -> dict[str, Any]:
    """Parse component props from a string."""
    props = {}

    # Pattern for prop="value" or prop={value}
    prop_pattern = r'(\w+)=(?:"([^"]*)"|{([^}]*)}|([^\s>]+))'

    for match in re.finditer(prop_pattern, props_string):
        prop_name = match.group(1)
        # Check which group matched
        if match.group(2) is not None:  # String value in quotes
            props[prop_name] = match.group(2)
        elif match.group(3) is not None:  # Expression in braces
            props[prop_name] = match.group(3)
        elif match.group(4) is not None:  # Unquoted value
            props[prop_name] = match.group(4)

    return props


def extract_sections(content: str) -> list[tuple[str, str, int]]:
    """Extract sections from markdown content.

    Returns list of (heading_level, heading_text, line_number) tuples.
    """
    sections = []
    lines = content.split('\n')

    for i, line in enumerate(lines):
        # Match markdown headings
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if heading_match:
            level = heading_match.group(1)
            text = heading_match.group(2)
            sections.append((level, text, i))

    return sections


async def search_mdx_files(
    query: str,
    search_path: str = ".",
    search_in: list[Literal["content", "headings", "code", "components", "frontmatter"]] | None = None,
    case_sensitive: bool = False,
    max_results: int = 50,
    file_pattern: str = "**/*.mdx",
    exclude_patterns: list[str] | None = None,
) -> MDXSearchResult:
    """Search MDX documentation files.

    Args:
        query: Search query
        search_path: Base path to search in
        search_in: Where to search (content, headings, code blocks, components, frontmatter)
        case_sensitive: Whether search is case sensitive
        max_results: Maximum number of results
        file_pattern: Glob pattern for MDX files
        exclude_patterns: Patterns to exclude from search

    Returns:
        MDXSearchResult with matches
    """
    if search_in is None:
        search_in = ["content"]

    start_time = asyncio.get_event_loop().time()
    matches: list[MDXMatch] = []
    files_searched = 0
    unique_components = set()

    try:
        path = Path(search_path)
        if not path.exists():
            return MDXSearchResult(
                success=False,
                query=query,
                total_matches=0,
                error=f"Search path does not exist: {search_path}",
                search_time=0,
                files_searched=0,
            )

        # Find all MDX files
        mdx_files = list(path.glob(file_pattern))

        # Apply exclusions
        if exclude_patterns:
            filtered_files = []
            for file_path in mdx_files:
                excluded = False
                for pattern in exclude_patterns:
                    if re.search(pattern, str(file_path)):
                        excluded = True
                        break
                if not excluded:
                    filtered_files.append(file_path)
            mdx_files = filtered_files

        # Search each file
        for file_path in mdx_files:
            if len(matches) >= max_results:
                break

            files_searched += 1

            try:
                async with aiofiles.open(file_path, encoding='utf-8') as f:
                    raw_content = await f.read()

                # Parse frontmatter
                post = frontmatter.loads(raw_content)
                content = post.content
                metadata = post.metadata

                # Extract sections
                sections = extract_sections(content)

                # Parse components
                components = parse_jsx_component(content)
                for comp in components:
                    unique_components.add(comp.name)

                # Prepare search text
                search_text = query.lower() if not case_sensitive else query

                # Search in frontmatter
                if "frontmatter" in search_in and metadata:
                    metadata_str = str(metadata).lower() if not case_sensitive else str(metadata)
                    if search_text in metadata_str:
                        matches.append(
                            MDXMatch(
                                file_path=str(file_path),
                                title=metadata.get("title"),
                                section=None,
                                content=str(metadata),
                                match_type="frontmatter",
                                line_number=1,
                                relevance_score=0.9,
                                frontmatter=metadata,
                                context=None,
                            )
                        )

                # Search in content
                lines = content.split('\n')
                current_section = None

                for i, line in enumerate(lines):
                    line_lower = line.lower() if not case_sensitive else line

                    # Update current section
                    for _, heading, line_no in sections:
                        if line_no == i:
                            current_section = heading

                    # Search in headings
                    if "headings" in search_in and line.startswith('#') and search_text in line_lower:
                        matches.append(
                            MDXMatch(
                                file_path=str(file_path),
                                title=metadata.get("title"),
                                section=current_section,
                                content=line,
                                match_type="heading",
                                line_number=i + 1,
                                relevance_score=0.8,
                                frontmatter=metadata,
                                context=get_context(lines, i),
                            )
                        )

                    # Search in code blocks
                    if "code" in search_in and line.strip().startswith('```'):
                        # Collect code block
                        code_lines = []
                        j = i + 1
                        while j < len(lines) and not lines[j].strip().startswith('```'):
                            code_lines.append(lines[j])
                            j += 1

                        code_content = '\n'.join(code_lines)
                        code_lower = code_content.lower() if not case_sensitive else code_content

                        if search_text in code_lower:
                            matches.append(
                                MDXMatch(
                                    file_path=str(file_path),
                                    title=metadata.get("title"),
                                    section=current_section,
                                    content=code_content,
                                    match_type="code",
                                    line_number=i + 1,
                                    relevance_score=0.7,
                                    frontmatter=metadata,
                                    context=get_context(lines, i),
                                )
                            )

                    # Search in regular content
                    if "content" in search_in and search_text in line_lower:
                        # Find components in this line
                        line_components = parse_jsx_component(line, i)

                        matches.append(
                            MDXMatch(
                                file_path=str(file_path),
                                title=metadata.get("title"),
                                section=current_section,
                                content=line,
                                match_type="content",
                                line_number=i + 1,
                                relevance_score=0.6,
                                frontmatter=metadata,
                                context=get_context(lines, i),
                                components=line_components,
                            )
                        )

                # Search in components
                if "components" in search_in:
                    for component in components:
                        comp_str = f"{component.name} {str(component.props)}"
                        comp_lower = comp_str.lower() if not case_sensitive else comp_str

                        if search_text in comp_lower:
                            matches.append(
                                MDXMatch(
                                    file_path=str(file_path),
                                    title=metadata.get("title"),
                                    section=current_section,
                                    content=component.raw_content,
                                    match_type="component",
                                    line_number=component.line_number,
                                    relevance_score=0.8,
                                    frontmatter=metadata,
                                    context=get_context(lines, component.line_number - 1),
                                    components=[component],
                                )
                            )

            except Exception as e:
                # Skip files that can't be read
                continue

        # Sort by relevance
        matches.sort(key=lambda x: x.relevance_score, reverse=True)
        matches = matches[:max_results]

        search_time = asyncio.get_event_loop().time() - start_time

        return MDXSearchResult(
            success=True,
            query=query,
            total_matches=len(matches),
            matches=matches,
            files_searched=files_searched,
            search_time=search_time,
            error=None,
            unique_components=list(unique_components),
        )

    except Exception as e:
        search_time = asyncio.get_event_loop().time() - start_time
        return MDXSearchResult(
            success=False, query=query, total_matches=0, search_time=search_time, error=str(e), files_searched=0
        )


def get_context(lines: list[str], index: int, context_lines: int = 2) -> str:
    """Get context lines around a match."""
    start = max(0, index - context_lines)
    end = min(len(lines), index + context_lines + 1)
    return '\n'.join(lines[start:end])


async def extract_mdx_components(file_path: str, component_names: list[str] | None = None) -> dict[str, list[MDXComponent]]:
    """Extract JSX components from an MDX file.

    Args:
        file_path: Path to MDX file
        component_names: Optional list of component names to filter by

    Returns:
        Dictionary mapping component names to lists of component instances
    """
    components_by_name: dict[str, list[MDXComponent]] = {}

    try:
        async with aiofiles.open(file_path, encoding='utf-8') as f:
            content = await f.read()

        # Parse frontmatter
        post = frontmatter.loads(content)
        content = post.content

        # Extract components
        components = parse_jsx_component(content)

        # Group by name
        for component in components:
            if component_names and component.name not in component_names:
                continue

            if component.name not in components_by_name:
                components_by_name[component.name] = []

            components_by_name[component.name].append(component)

    except Exception:
        pass

    return components_by_name


async def find_documentation_sections(
    search_path: str = ".",
    heading_pattern: str | None = None,
    min_level: int = 1,
    max_level: int = 3,
    include_content: bool = True,
) -> list[dict[str, Any]]:
    """Find documentation sections by heading pattern.

    Args:
        search_path: Base path to search
        heading_pattern: Regex pattern to match headings
        min_level: Minimum heading level (1-6)
        max_level: Maximum heading level (1-6)
        include_content: Whether to include section content

    Returns:
        List of sections with metadata
    """
    sections = []
    path = Path(search_path)

    for file_path in path.glob("**/*.mdx"):
        try:
            async with aiofiles.open(file_path, encoding='utf-8') as f:
                content = await f.read()

            # Parse frontmatter
            post = frontmatter.loads(content)
            lines = post.content.split('\n')

            # Extract sections
            doc_sections = extract_sections(post.content)

            for level, heading, line_no in doc_sections:
                heading_level = len(level)

                if heading_level < min_level or heading_level > max_level:
                    continue

                if heading_pattern and not re.search(heading_pattern, heading):
                    continue

                section_data = {
                    "file_path": str(file_path),
                    "heading": heading,
                    "level": heading_level,
                    "line_number": line_no + 1,
                    "frontmatter": post.metadata,
                }

                if include_content:
                    # Find content until next heading of same or higher level
                    content_lines = []
                    for i in range(line_no + 1, len(lines)):
                        line = lines[i]
                        if re.match(f'^#{{{1},{heading_level}}}\\s+', line):
                            break
                        content_lines.append(line)

                    section_data["content"] = '\n'.join(content_lines).strip()

                sections.append(section_data)

        except Exception:
            continue

    return sections


async def search_mdx_with_metadata(
    query: str,
    search_path: str = ".",
    metadata_filters: dict[str, Any] | None = None,
    tags_filter: list[str] | None = None,
    date_after: str | None = None,
    date_before: str | None = None,
) -> MDXSearchResult:
    """Search MDX files with metadata filtering.

    Args:
        query: Search query
        search_path: Base path to search
        metadata_filters: Frontmatter fields to filter by
        tags_filter: Tags to filter by (if frontmatter has tags)
        date_after: Only include files with date after this (ISO format)
        date_before: Only include files with date before this (ISO format)

    Returns:
        MDXSearchResult with filtered matches
    """
    # First do a regular search
    result = await search_mdx_files(query, search_path, search_in=["content", "frontmatter"])

    if not result.success:
        return result

    # Filter by metadata
    filtered_matches = []

    for match in result.matches:
        # Check metadata filters
        if metadata_filters:
            match_metadata = True
            for key, value in metadata_filters.items():
                if match.frontmatter.get(key) != value:
                    match_metadata = False
                    break
            if not match_metadata:
                continue

        # Check tags
        if tags_filter:
            match_tags = match.frontmatter.get("tags", [])
            if not any(tag in match_tags for tag in tags_filter):
                continue

        # Check dates
        if date_after or date_before:
            file_date = match.frontmatter.get("date")
            if file_date and isinstance(file_date, str):
                # Assume ISO format
                if date_after and file_date < date_after:
                    continue
                if date_before and file_date > date_before:
                    continue

        filtered_matches.append(match)

    result.matches = filtered_matches
    result.total_matches = len(filtered_matches)

    return result
