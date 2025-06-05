from __future__ import annotations

import asyncio
import git
import os
import re
import subprocess
from github import Github, GithubException
from pathlib import Path

# FUNCN_LILYPAD_IMPORT_PLACEHOLDER
# FUNCN_LILYPAD_CONFIGURE_PLACEHOLDER
from pydantic import BaseModel, Field, validator
from typing import Any, Optional
from urllib.parse import urlparse


class GitSearchType(str):
    """Enumeration of search types."""

    CODE = "code"
    FILE = "file"
    COMMIT = "commit"
    PATTERN = "pattern"


class GitRepoSearchArgs(BaseModel):
    """Arguments for Git repository search operations."""

    repo_path: str | None = Field(None, description="Path to local git repository")
    github_repo: str | None = Field(None, description="GitHub repository in format 'owner/repo'")
    query: str = Field(..., description="Search query or pattern")
    search_type: str = Field(default=GitSearchType.CODE, description="Type of search: 'code', 'file', 'commit', or 'pattern'")
    file_pattern: str | None = Field(None, description="File pattern to filter by (e.g., '*.py', '*.js')")
    branch: str | None = Field(
        None, description="Branch to search in (default: current branch for local, default branch for GitHub)"
    )
    max_results: int = Field(default=50, description="Maximum number of results to return")
    case_sensitive: bool = Field(default=False, description="Whether the search should be case sensitive")
    regex: bool = Field(default=False, description="Whether to use regex for pattern matching")
    include_context: bool = Field(default=True, description="Include context lines around matches")
    context_lines: int = Field(default=3, description="Number of context lines to include")

    @validator('repo_path', 'github_repo')
    def validate_repo_input(cls, v, values):
        if 'repo_path' in values and values['repo_path'] is None and v is None:
            raise ValueError("Either repo_path or github_repo must be provided")
        return v

    @validator('search_type')
    def validate_search_type(cls, v):
        valid_types = {GitSearchType.CODE, GitSearchType.FILE, GitSearchType.COMMIT, GitSearchType.PATTERN}
        if v not in valid_types:
            raise ValueError(f"search_type must be one of: {', '.join(valid_types)}")
        return v


class CodeMatch(BaseModel):
    """A code match result."""

    file_path: str = Field(..., description="Path to the file containing the match")
    line_number: int = Field(..., description="Line number of the match")
    line_content: str = Field(..., description="Content of the matching line")
    context_before: list[str] = Field(default_factory=list, description="Lines before the match")
    context_after: list[str] = Field(default_factory=list, description="Lines after the match")


class FileMatch(BaseModel):
    """A file path match result."""

    file_path: str = Field(..., description="Path to the matching file")
    file_size: int | None = Field(None, description="Size of the file in bytes")
    last_modified: str | None = Field(None, description="Last modification timestamp")


class CommitMatch(BaseModel):
    """A commit match result."""

    commit_hash: str = Field(..., description="Git commit hash")
    author: str = Field(..., description="Commit author")
    date: str = Field(..., description="Commit date")
    message: str = Field(..., description="Commit message")
    files_changed: list[str] = Field(default_factory=list, description="Files changed in this commit")


class GitRepoSearchResponse(BaseModel):
    """Response from Git repository search."""

    success: bool = Field(..., description="Whether the search was successful")
    search_type: str = Field(..., description="Type of search performed")
    query: str = Field(..., description="The search query used")
    repository: str = Field(..., description="Repository searched (path or GitHub repo)")
    branch: str | None = Field(None, description="Branch searched")
    total_matches: int = Field(..., description="Total number of matches found")
    code_matches: list[CodeMatch] = Field(default_factory=list, description="Code search results")
    file_matches: list[FileMatch] = Field(default_factory=list, description="File search results")
    commit_matches: list[CommitMatch] = Field(default_factory=list, description="Commit search results")
    error: str | None = Field(None, description="Error message if search failed")


# FUNCN_LILYPAD_DECORATOR_PLACEHOLDER
async def search_git_repo(args: GitRepoSearchArgs) -> GitRepoSearchResponse:
    """Search within a Git repository for code, files, commits, or patterns.

    This function supports both local Git repositories and GitHub repositories,
    providing various search capabilities including code search, file search,
    commit history search, and pattern matching.
    """
    try:
        if args.github_repo:
            # Search GitHub repository
            return await _search_github_repo(args)
        else:
            # Search local repository
            return await _search_local_repo(args)

    except Exception as e:
        return GitRepoSearchResponse(
            success=False,
            search_type=args.search_type,
            query=args.query,
            repository=args.github_repo or args.repo_path or "unknown",
            branch=None,
            total_matches=0,
            error=f"Error searching repository: {str(e)}",
        )


async def _search_github_repo(args: GitRepoSearchArgs) -> GitRepoSearchResponse:
    """Search a GitHub repository using the GitHub API."""
    try:
        # Get GitHub token from environment
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            return GitRepoSearchResponse(
                success=False,
                search_type=args.search_type,
                query=args.query,
                repository=args.github_repo or "unknown",
                branch=None,
                total_matches=0,
                error="GITHUB_TOKEN environment variable not set",
            )

        g = Github(github_token)
        repo = g.get_repo(args.github_repo)

        # Get branch
        branch = args.branch or repo.default_branch

        if args.search_type == GitSearchType.CODE:
            # Search code using GitHub search API
            query_parts = [f'repo:{args.github_repo}', args.query]
            if args.file_pattern:
                # Convert glob to GitHub search syntax
                ext = args.file_pattern.replace('*', '').replace('.', '')
                query_parts.append(f'extension:{ext}')

            search_query = ' '.join(query_parts)
            code_results = g.search_code(search_query)

            code_matches = []
            for i, result in enumerate(code_results):
                if i >= args.max_results:
                    break

                # Get file content to extract context
                try:
                    content = repo.get_contents(result.path, ref=branch)
                    if content.encoding == 'base64':
                        file_content = content.decoded_content.decode('utf-8')
                        lines = file_content.split('\n')

                        # Find matching lines
                        pattern = re.compile(
                            args.query if args.regex else re.escape(args.query), 0 if args.case_sensitive else re.IGNORECASE
                        )

                        for line_num, line in enumerate(lines, 1):
                            if pattern.search(line):
                                context_start = max(0, line_num - 1 - args.context_lines)
                                context_end = min(len(lines), line_num + args.context_lines)

                                code_matches.append(
                                    CodeMatch(
                                        file_path=result.path,
                                        line_number=line_num,
                                        line_content=line.strip(),
                                        context_before=lines[context_start : line_num - 1] if args.include_context else [],
                                        context_after=lines[line_num:context_end] if args.include_context else [],
                                    )
                                )
                except Exception:
                    # If we can't get content, just add basic info
                    code_matches.append(
                        CodeMatch(
                            file_path=result.path,
                            line_number=0,
                            line_content="[Content unavailable]",
                            context_before=[],
                            context_after=[],
                        )
                    )

            return GitRepoSearchResponse(
                success=True,
                search_type=args.search_type,
                query=args.query,
                repository=args.github_repo or "unknown",
                branch=branch,
                total_matches=len(code_matches),
                code_matches=code_matches[: args.max_results],
                error=None,
            )

        elif args.search_type == GitSearchType.FILE:
            # Search for files
            contents = repo.get_contents("", ref=branch)
            file_matches = []

            while contents:
                file_content = contents.pop(0)
                if file_content.type == "dir":
                    contents.extend(repo.get_contents(file_content.path, ref=branch))
                else:
                    # Check if file matches
                    if args.query.lower() in file_content.path.lower() and (
                        not args.file_pattern or Path(file_content.path).match(args.file_pattern)
                    ):
                        file_matches.append(
                            FileMatch(
                                file_path=file_content.path, file_size=file_content.size, last_modified=file_content.last_modified
                            )
                        )

            return GitRepoSearchResponse(
                success=True,
                search_type=args.search_type,
                query=args.query,
                repository=args.github_repo or "unknown",
                branch=branch,
                total_matches=len(file_matches),
                file_matches=file_matches[: args.max_results],
                error=None,
            )

        elif args.search_type == GitSearchType.COMMIT:
            # Search commits
            commits = repo.get_commits()
            commit_matches = []

            pattern = re.compile(args.query if args.regex else re.escape(args.query), 0 if args.case_sensitive else re.IGNORECASE)

            for i, commit in enumerate(commits):
                if i >= args.max_results * 2:  # Check more commits than max_results
                    break

                if pattern.search(commit.commit.message):
                    commit_matches.append(
                        CommitMatch(
                            commit_hash=commit.sha,
                            author=commit.commit.author.name,
                            date=commit.commit.author.date.isoformat(),
                            message=commit.commit.message,
                            files_changed=[f.filename for f in commit.files] if commit.files else [],
                        )
                    )

                    if len(commit_matches) >= args.max_results:
                        break

            return GitRepoSearchResponse(
                success=True,
                search_type=args.search_type,
                query=args.query,
                repository=args.github_repo or "unknown",
                branch=branch,
                total_matches=len(commit_matches),
                commit_matches=commit_matches,
                error=None,
            )

        else:
            return GitRepoSearchResponse(
                success=False,
                search_type=args.search_type,
                query=args.query,
                repository=args.github_repo or "unknown",
                branch=None,
                total_matches=0,
                error=f"Search type {args.search_type} not supported for GitHub repositories",
            )

    except GithubException as e:
        return GitRepoSearchResponse(
            success=False,
            search_type=args.search_type,
            query=args.query,
            repository=args.github_repo or "unknown",
            branch=None,
            total_matches=0,
            error=f"GitHub API error: {str(e)}",
        )
    except Exception as e:
        return GitRepoSearchResponse(
            success=False,
            search_type=args.search_type,
            query=args.query,
            repository=args.github_repo or "unknown",
            branch=None,
            total_matches=0,
            error=f"Error searching GitHub repository: {str(e)}",
        )


async def _search_local_repo(args: GitRepoSearchArgs) -> GitRepoSearchResponse:
    """Search a local Git repository."""
    try:
        # Validate repository path
        if args.repo_path is None:
            return GitRepoSearchResponse(
                success=False,
                search_type=args.search_type,
                query=args.query,
                repository="",
                branch=None,
                total_matches=0,
                error="repo_path is required for local repository search",
            )

        repo_path = Path(args.repo_path)
        if not repo_path.exists() or not (repo_path / '.git').exists():
            return GitRepoSearchResponse(
                success=False,
                search_type=args.search_type,
                query=args.query,
                repository=str(repo_path),
                branch=None,
                total_matches=0,
                error="Not a valid Git repository",
            )

        # Run search in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, _perform_local_search, repo_path, args)
        return result

    except Exception as e:
        return GitRepoSearchResponse(
            success=False,
            search_type=args.search_type,
            query=args.query,
            repository=args.repo_path or "unknown",
            branch=None,
            total_matches=0,
            error=f"Error searching local repository: {str(e)}",
        )


def _perform_local_search(repo_path: Path, args: GitRepoSearchArgs) -> GitRepoSearchResponse:
    """Perform search in local repository (sync function for thread pool)."""
    try:
        repo = git.Repo(repo_path)
        branch = args.branch or repo.active_branch.name

        if args.search_type in [GitSearchType.CODE, GitSearchType.PATTERN]:
            # Use git grep for code/pattern search
            grep_args = ['git', 'grep', '-n']  # -n for line numbers

            if not args.case_sensitive:
                grep_args.append('-i')
            if args.regex:
                grep_args.extend(['-E'])
            else:
                grep_args.extend(['-F'])

            if args.include_context:
                grep_args.extend([f'-C{args.context_lines}'])

            grep_args.append(args.query)

            if args.file_pattern:
                grep_args.extend(['--', args.file_pattern])

            try:
                result = subprocess.run(grep_args, cwd=repo_path, capture_output=True, text=True)

                code_matches = []
                if result.returncode == 0:
                    # Parse git grep output
                    lines = result.stdout.strip().split('\n')
                    current_file = None
                    current_matches: dict[str, list[dict[str, Any]]] = {}

                    for line in lines:
                        if not line:
                            continue

                        # Parse line format: filename:line_number:content
                        parts = line.split(':', 2)
                        if len(parts) >= 3:
                            file_path = parts[0]
                            try:
                                line_num = int(parts[1])
                                content = parts[2]
                            except ValueError:
                                continue

                            if file_path not in current_matches:
                                current_matches[file_path] = []

                            current_matches[file_path].append({'line_number': line_num, 'content': content})

                    # Convert to CodeMatch objects
                    for file_path, matches in current_matches.items():
                        for match in matches[: args.max_results // max(len(current_matches), 1)]:
                            code_matches.append(
                                CodeMatch(
                                    file_path=file_path,
                                    line_number=match['line_number'],
                                    line_content=match['content'].strip(),
                                    context_before=[],
                                    context_after=[],
                                )
                            )

                return GitRepoSearchResponse(
                    success=True,
                    search_type=args.search_type,
                    query=args.query,
                    repository=str(repo_path),
                    branch=branch,
                    total_matches=len(code_matches),
                    code_matches=code_matches[: args.max_results],
                    error=None,
                )

            except subprocess.SubprocessError as e:
                return GitRepoSearchResponse(
                    success=False,
                    search_type=args.search_type,
                    query=args.query,
                    repository=str(repo_path),
                    branch=None,
                    total_matches=0,
                    error=f"Git grep error: {str(e)}",
                )

        elif args.search_type == GitSearchType.FILE:
            # Search for files
            file_matches = []
            pattern = re.compile(args.query if args.regex else re.escape(args.query), 0 if args.case_sensitive else re.IGNORECASE)

            for item in repo_path.rglob('*'):
                if (
                    item.is_file()
                    and '.git' not in str(item)
                    and pattern.search(str(item.relative_to(repo_path)))
                    and (not args.file_pattern or item.match(args.file_pattern))
                ):
                    file_matches.append(
                        FileMatch(
                            file_path=str(item.relative_to(repo_path)),
                            file_size=item.stat().st_size,
                            last_modified=str(item.stat().st_mtime),
                        )
                    )

            return GitRepoSearchResponse(
                success=True,
                search_type=args.search_type,
                query=args.query,
                repository=str(repo_path),
                branch=branch,
                total_matches=len(file_matches),
                file_matches=file_matches[: args.max_results],
                error=None,
            )

        elif args.search_type == GitSearchType.COMMIT:
            # Search in commit history
            commit_matches = []
            pattern = re.compile(args.query if args.regex else re.escape(args.query), 0 if args.case_sensitive else re.IGNORECASE)

            for commit in repo.iter_commits(branch, max_count=args.max_results * 2):
                if pattern.search(commit.message):
                    commit_matches.append(
                        CommitMatch(
                            commit_hash=commit.hexsha,
                            author=commit.author.name,
                            date=commit.authored_datetime.isoformat(),
                            message=commit.message,
                            files_changed=list(commit.stats.files.keys()),
                        )
                    )

                    if len(commit_matches) >= args.max_results:
                        break

            return GitRepoSearchResponse(
                success=True,
                search_type=args.search_type,
                query=args.query,
                repository=str(repo_path),
                branch=branch,
                total_matches=len(commit_matches),
                commit_matches=commit_matches,
                error=None,
            )

        # Default return if search_type doesn't match any condition
        return GitRepoSearchResponse(
            success=False,
            search_type=args.search_type,
            query=args.query,
            repository=str(repo_path),
            branch=None,
            total_matches=0,
            error=f"Unsupported search type: {args.search_type}",
        )

    except Exception as e:
        return GitRepoSearchResponse(
            success=False,
            search_type=args.search_type,
            query=args.query,
            repository=str(repo_path),
            branch=None,
            total_matches=0,
            error=f"Error performing search: {str(e)}",
        )
