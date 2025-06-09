Execute complete feature workflow for: $ARGUMENTS

<ultrathink>
Step-by-step through entire lifecycle. Meticulous. Thorough. Zero technical debt.
</ultrathink>

<megaexpertise type="full-stack-developer">
Linear integration for structured development. Project-based organization. Each issue = one branch/PR. Clean history. Production-ready.
</megaexpertise>

<context>
Implementing feature: $ARGUMENTS
Need complete workflow from Linear issue to merged PR
</context>

<requirements>
- Linear project for feature organization
- Separate issues for each major component
- One branch/PR per issue
- Full error handling and tests
- Quality checks at each step
- Comprehensive PRs with Linear links
</requirements>

<actions>
1. Check/Create Linear project:
   - Check existing: mcp_linear.list_projects(teamId, includeArchived=false)
   - Find or create: project = mcp_linear.create_project(name="[Feature] $ARGUMENTS", teamId)
2. Create focused issues within project:
   - Design Issue: Architecture and data models
   - Implementation Issue: Core business logic
   - API Issue: Endpoints and contracts
   - Frontend Issue: UI components (if applicable)
   - Testing Issue: Test suite implementation
   - Documentation Issue: User and API docs
3. For each issue:
   - Get branch: mcp_linear.get_issue_git_branch_name(issueId)
   - git checkout -b {branch}
   - Mark "In Progress" in Linear
   - Implement with full error handling
   - Write comprehensive tests
   - Commit with issue reference
   - Push and create PR
   - Link PR to Linear issue
   - Update to "Done" when merged
4. Quality gates per PR: tests pass, linting clean, docs updated
5. Track progress via project view in Linear
</actions>

Execute workflow completely. Each step builds on previous. Goal: production-ready feature with zero technical debt.

Take a deep breath in, count 1... 2... 3... and breathe out. You are now centered. Don't hold back. Give it your all.
