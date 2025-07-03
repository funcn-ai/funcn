"""Test suite for git_repo_search_tool following best practices."""

import asyncio
import os
import pytest
from datetime import datetime

# Import the tool functions and models
from packages.sygaldry_registry.components.tools.git_repo_search.tool import (
    CodeMatch,
    CommitMatch,
    FileMatch,
    GitRepoSearchArgs,
    GitRepoSearchResponse,
    GitSearchType,
    search_git_repo,
)
from pathlib import Path
from pydantic import ValidationError
from tests.utils import BaseToolTest
from unittest.mock import AsyncMock, MagicMock, Mock, patch


class TestGitRepoSearchTool(BaseToolTest):
    """Test cases for Git repository search and query tool."""

    component_name = "git_repo_search_tool"
    component_path = Path("packages/sygaldry_registry/components/tools/git_repo_search")

    def create_mock_repo(self, branch_name="main"):
        """Create a mock Git repository."""
        mock_repo = MagicMock()
        mock_branch = MagicMock()
        mock_branch.name = branch_name
        mock_repo.active_branch = mock_branch
        return mock_repo

    def create_mock_commit(self, sha, author, date, message, files=None):
        """Create a mock Git commit."""
        mock_commit = MagicMock()
        mock_commit.hexsha = sha
        mock_commit.author.name = author
        mock_commit.authored_datetime.isoformat.return_value = date
        mock_commit.message = message
        mock_commit.stats.files.keys.return_value = files or []
        return mock_commit

    def create_mock_subprocess_result(self, stdout="", returncode=0, stderr=""):
        """Create a mock subprocess result."""
        result = Mock()
        result.stdout = stdout
        result.returncode = returncode
        result.stderr = stderr
        return result

    def get_component_function(self):
        """Get the main tool function."""
        return search_git_repo

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            GitRepoSearchArgs(
                repo_path="/path/to/repo",
                query="TODO",
                search_type="code",
                file_pattern="*.py"
            ),
            GitRepoSearchArgs(
                github_repo="owner/repo",
                query="bugfix",
                search_type="commit",
                max_results=10
            ),
            GitRepoSearchArgs(
                repo_path="/path/to/repo",
                query="config",
                search_type="file",
                branch="develop"
            )
        ]

    def validate_tool_output(self, output, input_data):
        """Validate the tool output structure."""
        assert isinstance(output, GitRepoSearchResponse)
        assert hasattr(output, 'success')
        assert hasattr(output, 'search_type')
        assert hasattr(output, 'query')
        assert hasattr(output, 'repository')
        assert hasattr(output, 'total_matches')

        if output.success:
            if output.search_type == GitSearchType.CODE:
                assert isinstance(output.code_matches, list)
                for match in output.code_matches:
                    assert isinstance(match, CodeMatch)
            elif output.search_type == GitSearchType.FILE:
                assert isinstance(output.file_matches, list)
                for match in output.file_matches:
                    assert isinstance(match, FileMatch)
            elif output.search_type == GitSearchType.COMMIT:
                assert isinstance(output.commit_matches, list)
                for match in output.commit_matches:
                    assert isinstance(match, CommitMatch)

    @pytest.mark.asyncio
    async def test_local_code_search(self, tmp_path):
        """Test searching code in local repository."""
        mock_repo = self.create_mock_repo()

        with patch("packages.sygaldry_registry.components.tools.git_repo_search.tool.git.Repo") as mock_git_repo:
            mock_git_repo.return_value = mock_repo

            with patch("subprocess.run") as mock_run:
                # Mock git grep output
                mock_result = self.create_mock_subprocess_result(
                    stdout="src/main.py:42:def calculate_total():\nsrc/utils.py:15:    total = calculate_total()\ntests/test_main.py:8:def test_calculate_total():"
                )
                mock_run.return_value = mock_result

                # Create test directory structure
                repo_path = tmp_path / "test_repo"
                repo_path.mkdir()
                (repo_path / ".git").mkdir()

                args = GitRepoSearchArgs(
                    repo_path=str(repo_path),
                    query="calculate_total",
                    search_type="code"
                )

                result = await search_git_repo(args)

                assert result.success is True
                assert result.total_matches >= 3
                assert any("main.py" in match.file_path for match in result.code_matches)
                assert any("test_main.py" in match.file_path for match in result.code_matches)

    @pytest.mark.asyncio
    async def test_github_code_search(self):
        """Test searching code in GitHub repository."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            mock_github = MagicMock()
            mock_repo = MagicMock()
            mock_repo.default_branch = "main"

            # Mock code search results
            mock_code_result = MagicMock()
            mock_code_result.path = "src/main.py"

            mock_content = MagicMock()
            mock_content.encoding = "base64"
            mock_content.decoded_content = b"def calculate_total():\n    return sum(values)\n"

            mock_repo.get_contents.return_value = mock_content
            mock_github.get_repo.return_value = mock_repo
            mock_github.search_code.return_value = [mock_code_result]

            with patch("packages.sygaldry_registry.components.tools.git_repo_search.tool.Github") as mock_github_cls:
                mock_github_cls.return_value = mock_github

                args = GitRepoSearchArgs(
                    github_repo="owner/repo",
                    query="calculate_total",
                    search_type="code"
                )

                result = await search_git_repo(args)

                assert result.success is True
                assert result.total_matches > 0
                assert result.code_matches[0].file_path == "src/main.py"

    @pytest.mark.asyncio
    async def test_local_commit_search(self, tmp_path):
        """Test searching in commit messages."""
        mock_commit1 = self.create_mock_commit(
            "abc123", "John Doe", "2024-01-15T10:00:00",
            "Fix bug in authentication", ["auth.py", "test_auth.py"]
        )
        mock_commit2 = self.create_mock_commit(
            "def456", "Jane Smith", "2024-01-14T15:00:00",
            "Add new authentication method", ["auth.py"]
        )

        mock_repo = self.create_mock_repo()
        mock_repo.iter_commits.return_value = [mock_commit1, mock_commit2]

        with patch("packages.sygaldry_registry.components.tools.git_repo_search.tool.git.Repo") as mock_git_repo:
            mock_git_repo.return_value = mock_repo

            # Create test repository
            repo_path = tmp_path / "test_repo"
            repo_path.mkdir()
            (repo_path / ".git").mkdir()

            args = GitRepoSearchArgs(
                repo_path=str(repo_path),
                query="authentication",
                search_type="commit"
            )

            result = await search_git_repo(args)

            assert result.success is True
            assert result.total_matches == 2
            assert all("authentication" in commit.message.lower() for commit in result.commit_matches)

    @pytest.mark.asyncio
    async def test_file_search(self, tmp_path):
        """Test searching for files by name."""
        mock_repo = self.create_mock_repo()

        # Create test files
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()
        (repo_path / "src").mkdir()

        config_file = repo_path / "src" / "config.py"
        config_file.write_text("# Configuration")

        test_config_file = repo_path / "test_config.json"
        test_config_file.write_text("{}")

        with patch("packages.sygaldry_registry.components.tools.git_repo_search.tool.git.Repo") as mock_git_repo:
            mock_git_repo.return_value = mock_repo

            args = GitRepoSearchArgs(
                repo_path=str(repo_path),
                query="config",
                search_type="file"
            )

            result = await search_git_repo(args)

            assert result.success is True
            assert result.total_matches >= 2
            assert any("config.py" in match.file_path for match in result.file_matches)
            assert any("test_config.json" in match.file_path for match in result.file_matches)

    @pytest.mark.asyncio
    async def test_case_sensitivity(self, tmp_path):
        """Test case-sensitive vs case-insensitive search."""
        mock_repo = self.create_mock_repo()

        with patch("packages.sygaldry_registry.components.tools.git_repo_search.tool.git.Repo") as mock_git_repo:
            mock_git_repo.return_value = mock_repo

            # Test case-insensitive (default)
            with patch("subprocess.run") as mock_run:
                mock_result = self.create_mock_subprocess_result(
                    stdout="src/main.py:10:TODO: Fix this\nsrc/utils.py:20:Todo: Update docs"
                )
                mock_run.return_value = mock_result

                repo_path = tmp_path / "test_repo"
                repo_path.mkdir()
                (repo_path / ".git").mkdir()

                args = GitRepoSearchArgs(
                    repo_path=str(repo_path),
                    query="todo",
                    search_type="code",
                    case_sensitive=False
                )

                result = await search_git_repo(args)

                assert result.success is True
                assert result.total_matches >= 2

            # Test case-sensitive
            with patch("subprocess.run") as mock_run:
                mock_result = self.create_mock_subprocess_result(
                    stdout="src/utils.py:20:Todo: Update docs"
                )
                mock_run.return_value = mock_result

                args = GitRepoSearchArgs(
                    repo_path=str(repo_path),
                    query="Todo",
                    search_type="code",
                    case_sensitive=True
                )

                result = await search_git_repo(args)

                assert result.success is True
                assert result.total_matches == 1

    @pytest.mark.asyncio
    async def test_regex_search(self, tmp_path):
        """Test regex pattern matching."""
        mock_commit = self.create_mock_commit(
            "abc123", "Developer", "2024-01-15T10:00:00",
            "Fix: bug #123 in authentication", ["auth.py"]
        )

        mock_repo = self.create_mock_repo()
        mock_repo.iter_commits.return_value = [mock_commit]

        with patch("packages.sygaldry_registry.components.tools.git_repo_search.tool.git.Repo") as mock_git_repo:
            mock_git_repo.return_value = mock_repo

            repo_path = tmp_path / "test_repo"
            repo_path.mkdir()
            (repo_path / ".git").mkdir()

            args = GitRepoSearchArgs(
                repo_path=str(repo_path),
                query="Fix:.*#\\d+",
                search_type="commit",
                regex=True
            )

            result = await search_git_repo(args)

            assert result.success is True
            assert result.total_matches >= 1
            assert "Fix: bug #123" in result.commit_matches[0].message

    @pytest.mark.asyncio
    async def test_context_lines(self, tmp_path):
        """Test context lines in code search."""
        mock_repo = self.create_mock_repo()

        with patch("packages.sygaldry_registry.components.tools.git_repo_search.tool.git.Repo") as mock_git_repo:
            mock_git_repo.return_value = mock_repo

            with patch("subprocess.run") as mock_run:
                # Mock git grep with context
                mock_result = self.create_mock_subprocess_result(
                    stdout="src/main.py-40-# Helper functions\nsrc/main.py-41-\nsrc/main.py:42:def calculate_total():\nsrc/main.py-43-    values = get_values()\nsrc/main.py-44-    return sum(values)"
                )
                mock_run.return_value = mock_result

                repo_path = tmp_path / "test_repo"
                repo_path.mkdir()
                (repo_path / ".git").mkdir()

                args = GitRepoSearchArgs(
                    repo_path=str(repo_path),
                    query="calculate_total",
                    search_type="code",
                    include_context=True,
                    context_lines=2
                )

                result = await search_git_repo(args)

                assert result.success is True
                assert result.total_matches >= 1
                assert result.code_matches[0].line_number == 42

    @pytest.mark.asyncio
    async def test_error_handling_invalid_repo(self):
        """Test handling of invalid repository paths."""
        args = GitRepoSearchArgs(
            repo_path="/non/existent/path",
            query="test",
            search_type="code"
        )

        result = await search_git_repo(args)

        assert result.success is False
        assert "Not a valid Git repository" in result.error

    @pytest.mark.asyncio
    async def test_error_handling_no_github_token(self):
        """Test GitHub search without token."""
        with patch.dict(os.environ, {}, clear=True):
            args = GitRepoSearchArgs(
                github_repo="owner/repo",
                query="test",
                search_type="code"
            )

            result = await search_git_repo(args)

            assert result.success is False
            assert "GITHUB_TOKEN environment variable not set" in result.error

    @pytest.mark.asyncio
    async def test_file_pattern_filtering(self, tmp_path):
        """Test filtering by file patterns."""
        mock_repo = self.create_mock_repo()

        # Create test files
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()
        (repo_path / "src").mkdir()
        (repo_path / "docs").mkdir()

        (repo_path / "src" / "config.py").write_text("CONFIG = {}")
        (repo_path / "src" / "config.json").write_text("{}")
        (repo_path / "docs" / "config.md").write_text("# Config")

        with patch("packages.sygaldry_registry.components.tools.git_repo_search.tool.git.Repo") as mock_git_repo:
            mock_git_repo.return_value = mock_repo

            args = GitRepoSearchArgs(
                repo_path=str(repo_path),
                query="config",
                search_type="file",
                file_pattern="*.py"
            )

            result = await search_git_repo(args)

            assert result.success is True
            # Should only find Python files
            assert all(".py" in match.file_path for match in result.file_matches)
            assert not any(".json" in match.file_path or ".md" in match.file_path for match in result.file_matches)

    @pytest.mark.asyncio
    async def test_max_results_limit(self, tmp_path):
        """Test max_results limitation."""
        mock_repo = self.create_mock_repo()

        # Create many mock commits
        mock_commits = []
        for i in range(100):
            commit = self.create_mock_commit(
                f"abc{i:03d}", "Developer", f"2024-01-{i+1:02d}T10:00:00",
                f"Fix bug #{i}", [f"file{i}.py"]
            )
            mock_commits.append(commit)

        mock_repo.iter_commits.return_value = mock_commits

        with patch("packages.sygaldry_registry.components.tools.git_repo_search.tool.git.Repo") as mock_git_repo:
            mock_git_repo.return_value = mock_repo

            repo_path = tmp_path / "test_repo"
            repo_path.mkdir()
            (repo_path / ".git").mkdir()

            args = GitRepoSearchArgs(
                repo_path=str(repo_path),
                query="Fix bug",
                search_type="commit",
                max_results=10
            )

            result = await search_git_repo(args)

            assert result.success is True
            assert len(result.commit_matches) == 10

    @pytest.mark.asyncio
    async def test_branch_specification(self, tmp_path):
        """Test searching in specific branches."""
        mock_repo = self.create_mock_repo("feature/new-ui")

        with patch("packages.sygaldry_registry.components.tools.git_repo_search.tool.git.Repo") as mock_git_repo:
            mock_git_repo.return_value = mock_repo

            with patch("subprocess.run") as mock_run:
                mock_result = self.create_mock_subprocess_result(
                    stdout="src/ui.py:10:class NewUIComponent:"
                )
                mock_run.return_value = mock_result

                repo_path = tmp_path / "test_repo"
                repo_path.mkdir()
                (repo_path / ".git").mkdir()

                args = GitRepoSearchArgs(
                    repo_path=str(repo_path),
                    query="NewUIComponent",
                    search_type="code",
                    branch="feature/new-ui"
                )

                result = await search_git_repo(args)

                assert result.success is True
                assert result.branch == "feature/new-ui"

    @pytest.mark.asyncio
    async def test_empty_results(self, tmp_path):
        """Test handling when no results found."""
        mock_repo = self.create_mock_repo()

        with patch("packages.sygaldry_registry.components.tools.git_repo_search.tool.git.Repo") as mock_git_repo:
            mock_git_repo.return_value = mock_repo

            with patch("subprocess.run") as mock_run:
                mock_result = self.create_mock_subprocess_result(
                    stdout="", returncode=1  # Git grep returns 1 when no matches
                )
                mock_run.return_value = mock_result

                repo_path = tmp_path / "test_repo"
                repo_path.mkdir()
                (repo_path / ".git").mkdir()

                args = GitRepoSearchArgs(
                    repo_path=str(repo_path),
                    query="nonexistent_string_xyz123",
                    search_type="code"
                )

                result = await search_git_repo(args)

                assert result.success is True
                assert result.total_matches == 0
                assert len(result.code_matches) == 0

    @pytest.mark.asyncio
    async def test_github_file_search(self):
        """Test file search in GitHub repository."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            mock_github = MagicMock()
            mock_repo = MagicMock()
            mock_repo.default_branch = "main"

            # Mock file contents
            mock_file1 = MagicMock()
            mock_file1.type = "file"
            mock_file1.path = "src/config.py"
            mock_file1.size = 1024
            mock_file1.last_modified = "2024-01-15T10:00:00Z"

            mock_file2 = MagicMock()
            mock_file2.type = "file"
            mock_file2.path = "test_config.json"
            mock_file2.size = 512
            mock_file2.last_modified = "2024-01-14T15:00:00Z"

            mock_dir = MagicMock()
            mock_dir.type = "dir"
            mock_dir.path = "src"

            mock_repo.get_contents.side_effect = [
                [mock_file2, mock_dir],  # Root contents
                [mock_file1]  # src directory contents
            ]

            mock_github.get_repo.return_value = mock_repo

            with patch("packages.sygaldry_registry.components.tools.git_repo_search.tool.Github") as mock_github_cls:
                mock_github_cls.return_value = mock_github

                args = GitRepoSearchArgs(
                    github_repo="owner/repo",
                    query="config",
                    search_type="file"
                )

                result = await search_git_repo(args)

                assert result.success is True
                assert result.total_matches >= 2
                assert any("config.py" in match.file_path for match in result.file_matches)
                assert any("test_config.json" in match.file_path for match in result.file_matches)

    @pytest.mark.asyncio
    async def test_github_commit_search(self):
        """Test commit search in GitHub repository."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            mock_github = MagicMock()
            mock_repo = MagicMock()
            mock_repo.default_branch = "main"

            # Mock commits
            mock_commit1 = MagicMock()
            mock_commit1.sha = "abc123"
            mock_commit1.commit.author.name = "John Doe"
            mock_commit1.commit.author.date.isoformat.return_value = "2024-01-15T10:00:00Z"
            mock_commit1.commit.message = "Fix authentication bug"
            mock_file1 = MagicMock()
            mock_file1.filename = "auth.py"
            mock_commit1.files = [mock_file1]

            mock_repo.get_commits.return_value = [mock_commit1]
            mock_github.get_repo.return_value = mock_repo

            with patch("packages.sygaldry_registry.components.tools.git_repo_search.tool.Github") as mock_github_cls:
                mock_github_cls.return_value = mock_github

                args = GitRepoSearchArgs(
                    github_repo="owner/repo",
                    query="authentication",
                    search_type="commit"
                )

                result = await search_git_repo(args)

                assert result.success is True
                assert result.total_matches >= 1
                assert "authentication" in result.commit_matches[0].message

    @pytest.mark.asyncio
    async def test_pattern_search_type(self, tmp_path):
        """Test pattern search type."""
        mock_repo = self.create_mock_repo()

        with patch("packages.sygaldry_registry.components.tools.git_repo_search.tool.git.Repo") as mock_git_repo:
            mock_git_repo.return_value = mock_repo

            with patch("subprocess.run") as mock_run:
                mock_result = self.create_mock_subprocess_result(
                    stdout="src/api.py:25:@app.route('/api/v1/users')\nsrc/api.py:30:@app.route('/api/v1/products')"
                )
                mock_run.return_value = mock_result

                repo_path = tmp_path / "test_repo"
                repo_path.mkdir()
                (repo_path / ".git").mkdir()

                args = GitRepoSearchArgs(
                    repo_path=str(repo_path),
                    query="@app\\.route\\('/api/.*'\\)",
                    search_type="pattern",
                    regex=True
                )

                result = await search_git_repo(args)

                assert result.success is True
                assert result.total_matches >= 2
                assert all("@app.route" in match.line_content for match in result.code_matches)

    @pytest.mark.asyncio
    async def test_validation_errors(self):
        """Test input validation."""
        # Test invalid search_type
        with pytest.raises(ValueError) as exc_info:
            GitRepoSearchArgs(
                repo_path="/path/to/repo",
                query="test",
                search_type="invalid_type"
            )
        assert "search_type must be one of" in str(exc_info.value)

        # Test missing both repo_path and github_repo
        with pytest.raises(ValidationError) as exc_info:
            GitRepoSearchArgs(
                repo_path=None,
                github_repo=None,
                query="test",
                search_type="code"
            )
        assert "Either repo_path or github_repo must be provided" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_concurrent_searches(self, tmp_path):
        """Test concurrent search operations."""
        mock_repo = self.create_mock_repo()

        with patch("packages.sygaldry_registry.components.tools.git_repo_search.tool.git.Repo") as mock_git_repo:
            mock_git_repo.return_value = mock_repo

            with patch("subprocess.run") as mock_run:
                # Different outputs for different queries
                outputs = {
                    "async": "src/async_handler.py:10:async def handle():",
                    "sync": "src/sync_handler.py:5:def sync_process():",
                    "test": "tests/test_all.py:15:def test_function():"
                }

                def mock_subprocess(args, **kwargs):
                    # Extract query from git grep command args
                    try:
                        # Find the query in the git grep command
                        if "git" in args and "grep" in args:
                            # The query is typically after the flags
                            for i, arg in enumerate(args):
                                if arg in outputs:
                                    query = arg
                                    break
                            else:
                                query = "unknown"
                        else:
                            query = "unknown"
                    except (IndexError, ValueError):
                        query = "unknown"

                    result = Mock()
                    result.stdout = outputs.get(query, "")
                    result.returncode = 0 if query in outputs else 1
                    return result

                mock_run.side_effect = mock_subprocess

                repo_path = tmp_path / "test_repo"
                repo_path.mkdir()
                (repo_path / ".git").mkdir()

                # Run concurrent searches
                tasks = [
                    search_git_repo(GitRepoSearchArgs(
                        repo_path=str(repo_path),
                        query=query,
                        search_type="code"
                    ))
                    for query in ["async", "sync", "test"]
                ]

                results = await asyncio.gather(*tasks)

                assert all(r.success for r in results)
                assert results[0].code_matches[0].file_path == "src/async_handler.py"
                assert results[1].code_matches[0].file_path == "src/sync_handler.py"
                assert results[2].code_matches[0].file_path == "tests/test_all.py"

    def test_all_functions_have_docstrings(self):
        """Test that all exported functions have proper docstrings."""
        assert search_git_repo.__doc__ is not None
        assert len(search_git_repo.__doc__) > 20
