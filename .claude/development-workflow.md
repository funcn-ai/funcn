# Development Workflow

This document outlines the standard workflow for making code changes in the Funcn project, ensuring proper issue tracking, branch management, and safe development practices.

## Workflow Overview

**NEVER make changes directly on the main branch.** Always follow this workflow:

1. Create a Linear issue
2. Create and checkout the topic branch
3. Make changes in the feature branch
4. Create a pull request
5. Merge after review

## Step-by-Step Workflow

### 1. Create Linear Issue with Sub-Issues

Before starting any work, create an issue in Linear and break it down into sub-issues for complex tasks:

```python
# Create main issue
main_issue = mcp_linear.create_issue(
    title="Add new PDF parsing tool component",
    description="Implement a tool that can parse PDFs and extract text content",
    teamId="TEAM_ID"  # Optional, defaults to your team
)

# Break down into sub-issues for better organization
sub_issues = [
    mcp_linear.create_issue(
        title="Create PDF parser tool structure",
        description="Set up component.json, tool.py, and basic structure",
        parentId=main_issue.id
    ),
    mcp_linear.create_issue(
        title="Implement PDF text extraction",
        description="Add core functionality to extract text from PDFs",
        parentId=main_issue.id
    ),
    mcp_linear.create_issue(
        title="Add error handling and validation",
        description="Handle corrupted PDFs, encrypted files, etc.",
        parentId=main_issue.id
    ),
    mcp_linear.create_issue(
        title="Write tests for PDF parser",
        description="Add unit tests and test fixtures",
        parentId=main_issue.id
    ),
    mcp_linear.create_issue(
        title="Update documentation",
        description="Add funcn.md and update component registry",
        parentId=main_issue.id
    )
]

# Get the git branch name for the main issue
branch_name = mcp_linear.get_issue_git_branch_name(issueId=main_issue.id)
# Returns: jayscambler/issue-123
```

#### Why Use Sub-Issues?

1. **Smaller, Focused Commits**: Each sub-issue represents a logical commit
2. **Progress Tracking**: See completion percentage on main issue
3. **Parallel Work**: Multiple developers can work on different sub-issues
4. **Code Review**: Easier to review smaller, focused changes
5. **Rollback Safety**: Can revert specific features without affecting others

#### Available Linear MCP Commands

**Issue Management:**
- `create_issue` - Create a new Linear issue
- `get_issue` - Get details of a specific issue
- `update_issue` - Update an existing issue
- `list_issues` - List all issues
- `list_my_issues` - List issues assigned to you
- `get_issue_git_branch_name` - Get the git branch name for an issue

**Issue Metadata:**
- `list_issue_statuses` - List available issue statuses
- `get_issue_status` - Get details of a specific status
- `list_issue_labels` - List available issue labels

**Comments:**
- `create_comment` - Add a comment to an issue
- `list_comments` - List comments on an issue

**Organization:**
- `list_projects` - List all projects
- `get_project` - Get project details
- `create_project` - Create a new project
- `update_project` - Update a project
- `get_team` - Get team information
- `list_users` - List team users
- `get_user` - Get user details

**Help:**
- `search_documentation` - Search Linear documentation

Example issue titles:
- "Add new web scraping agent component"
- "Fix type hints in component manager"
- "Update documentation for MCP integration"

### 2. Create and Checkout Branch

After creating the Linear issue, create the corresponding branch:

```bash
# The branch name format from Linear: username/issue-number
git checkout -b jayscambler/issue-123

# Push the branch to set up tracking
git push -u origin jayscambler/issue-123
```

### 3. Make Changes with Sub-Issue Commits

Work through sub-issues systematically, making focused commits:

```bash
# Work on first sub-issue
# Update sub-issue status
mcp_linear.update_issue(issueId=sub_issues[0].id, stateId="in_progress")

# Make changes for "Create PDF parser tool structure"
# ... edit files ...

# Commit with sub-issue reference
git add .
git commit -m "feat: Create PDF parser tool structure #SUB-123

- Set up component.json with metadata
- Create tool.py with basic structure
- Add __init__.py for exports"

# Update sub-issue to completed
mcp_linear.update_issue(issueId=sub_issues[0].id, stateId="completed")

# Continue with next sub-issue
mcp_linear.update_issue(issueId=sub_issues[1].id, stateId="in_progress")
# ... make changes ...
git commit -m "feat: Implement PDF text extraction #SUB-124"
```

#### Best Practices for Sub-Issue Commits

1. **One Sub-Issue = One Commit** (when possible)
2. **Reference Sub-Issue ID** in commit message
3. **Update Status** as you progress
4. **Test After Each Sub-Issue** before moving to next
5. **Push Regularly** to save progress

### 4. Create Pull Request

When changes are ready:

```bash
# Ensure all changes are committed
git status

# Push latest changes
git push

# Create PR using GitHub CLI
gh pr create --title "Fix type hints in component manager" --body "Fixes #123

## Summary
- Updated deprecated type hints to modern syntax
- Fixed mypy warnings
- Added missing type annotations

## Test Plan
- [ ] Run mypy: `task lint`
- [ ] Run tests: `task test`
- [ ] Verify no regressions"
```

### 5. Handle Multiple Implementations with Git Worktrees

When exploring different approaches or working on multiple features simultaneously, use git worktrees:

```bash
# List current worktrees
git worktree list

# Add a new worktree for a different implementation
git worktree add ../funcn-feature-123 jayscambler/issue-123
git worktree add ../funcn-feature-124 jayscambler/issue-124

# Navigate between worktrees
cd ../funcn-feature-123  # Work on issue 123
cd ../funcn-feature-124  # Work on issue 124
cd ../funcn              # Main worktree

# Remove a worktree when done
git worktree remove ../funcn-feature-123
```

Benefits of worktrees:
- Work on multiple features without stashing/switching
- Compare different implementations side-by-side
- Keep dependencies isolated between features
- Faster context switching

## Best Practices

### Branch Naming
- Always use Linear-generated branch names: `username/issue-number`
- This maintains traceability between issues and code

### Commit Messages
- Reference the Linear issue: "Fix type hints #123"
- Use conventional commits when applicable:
  - `feat:` for new features
  - `fix:` for bug fixes
  - `docs:` for documentation
  - `refactor:` for code refactoring
  - `test:` for test additions/changes

### Before Creating PR
1. Ensure all tests pass: `task test`
2. Run linting: `task lint`
3. Update documentation if needed
4. Rebase on latest main if needed:
   ```bash
   git fetch origin
   git rebase origin/main
   ```

### Worktree Guidelines
- Name worktrees descriptively: `funcn-feature-description`
- Keep worktrees in a parallel directory to main repo
- Clean up worktrees after PR is merged
- Don't create worktrees inside the main repository

## Emergency Procedures

### Reverting Changes
If you need to quickly revert changes:

```bash
# On feature branch - reset to previous commit
git reset --hard HEAD~1

# On main branch (if accidentally committed)
git revert <commit-hash>
```

### Switching Context
If you need to quickly switch to another task:

```bash
# Option 1: Stash current changes
git stash push -m "WIP: feature description"
git checkout other-branch
# Later: git stash pop

# Option 2: Use worktrees (preferred)
git worktree add ../funcn-urgent-fix main
cd ../funcn-urgent-fix
# Make urgent fix
```

## Integration with Claude Code

When working with Claude Code:
1. Always start by asking to create a Linear issue
2. Remind Claude to checkout the feature branch
3. Use worktrees when comparing implementations
4. Ask Claude to create PR when changes are complete

### Example Claude Code Workflow with Sub-Issues

```python
# 1. Create main Linear issue
main_issue = mcp_linear.create_issue(
    title="Add PDF parsing tool component",
    description="Create a new tool component for parsing PDF files"
)

# 2. Create sub-issues for organization (like TODOs)
sub_tasks = [
    {"title": "Set up component structure", "desc": "Create component.json and basic files"},
    {"title": "Implement PDF parsing", "desc": "Core PDF text extraction logic"},
    {"title": "Add error handling", "desc": "Handle edge cases and invalid PDFs"},
    {"title": "Write tests", "desc": "Unit tests with test fixtures"},
    {"title": "Documentation", "desc": "Create funcn.md and examples"}
]

sub_issues = []
for task in sub_tasks:
    sub = mcp_linear.create_issue(
        title=task["title"],
        description=task["desc"],
        parentId=main_issue.id
    )
    sub_issues.append(sub)

# 3. Get branch name and checkout
branch_name = mcp_linear.get_issue_git_branch_name(issueId=main_issue.id)
# git checkout -b jayscambler/fun-123

# 4. Work through sub-issues systematically
for i, sub_issue in enumerate(sub_issues):
    # Update status
    mcp_linear.update_issue(issueId=sub_issue.id, stateId="in_progress")
    
    # Make focused changes for this sub-issue
    # ... implement specific feature ...
    
    # Commit with sub-issue reference
    # git commit -m "feat: {sub_issue.title} #{sub_issue.identifier}"
    
    # Mark complete
    mcp_linear.update_issue(issueId=sub_issue.id, stateId="completed")
    
    # Add progress comment on main issue
    mcp_linear.create_comment(
        issueId=main_issue.id,
        body=f"Completed: {sub_issue.title} ({i+1}/{len(sub_issues)})"
    )
```

#### Parallel TODOs and Linear Sub-Issues

Use both systems together:
- **Linear Sub-Issues**: For commits and external tracking
- **Claude TODOs**: For fine-grained task management during coding

```python
# Linear sub-issue: "Implement PDF parsing"
# Claude TODOs for this sub-issue:
todos = [
    "Research PDF parsing libraries",
    "Install and configure PyPDF2",
    "Create basic text extraction function",
    "Handle multi-page documents",
    "Test with sample PDFs"
]
```

Example interaction:
```
User: "I need to add a new PDF parsing tool"
Claude: "I'll help you add a PDF parsing tool. Let me first create a Linear issue for this work, then checkout the appropriate branch before making changes."
```

## Checklist for Every Change

- [ ] Linear issue created with sub-issues for complex tasks
- [ ] Feature branch created from main issue
- [ ] Changes made on feature branch (not main)
- [ ] Each sub-issue completed with focused commit
- [ ] Sub-issue IDs referenced in commit messages
- [ ] Tests written/updated for each sub-issue
- [ ] Linting passes after each commit
- [ ] Documentation updated
- [ ] PR created with proper description
- [ ] All sub-issues marked as completed
- [ ] Linear issue referenced in PR
- [ ] Worktrees cleaned up (if used)

## Common Commands Reference

### Linear MCP Commands (Quick Reference)

```python
# Create issue and get branch
issue = mcp_linear.create_issue(title="Feature X", description="Details...")
branch = mcp_linear.get_issue_git_branch_name(issueId=issue.id)

# List and update issues
my_issues = mcp_linear.list_my_issues()
mcp_linear.update_issue(issueId="ID", stateId="in_progress")

# Add comments
mcp_linear.create_comment(issueId="ID", body="Progress update...")
```

### Git Workflow Commands

```bash
# Linear + Git workflow
git checkout -b username/issue-123
git push -u origin username/issue-123

# Worktree management
git worktree list
git worktree add ../funcn-feature feature-branch
git worktree remove ../funcn-feature

# PR creation
gh pr create --title "Title" --body "Description"

# Status checks
task lint
task test
git status
git log --oneline -5
```