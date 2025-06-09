Create exemplary pull request for current changes: $ARGUMENTS

<ultrathink>
Professional. Complete. Everything reviewers need to understand, verify, merge confidently.
</ultrathink>

<megaexpertise type="senior-developer">
Create PRs that reviewers appreciate. Clear context, comprehensive testing, zero friction to merge.
</megaexpertise>

<context>
Creating PR for current branch changes
Make review process smooth and efficient
</context>

<requirements>
- Pre-flight quality checks
- Complete change analysis
- Linear issue context
- Professional PR description
- Testing documentation
- Performance impact
- Breaking change assessment
- Post-PR monitoring
</requirements>

<actions>
1. Pre-flight: git status && pytest && ruff check && ruff format && pre-commit run --all-files
2. Analyze changes: git diff --stat && git diff main...HEAD && git log main..HEAD --oneline
3. Extract Linear context from commits → get issue titles and scope
4. Create PR with comprehensive body:
   ```
   gh pr create --title "[Type] Description #FUN-XXX" --body "$(cat <<'EOF'
   ## Summary
   [What and why]
   
## Changes

- Feature: [additions]
- Fix: [corrections]
- Refactor: [improvements]
- Docs: [documentation]
- Tests: [test coverage]
   
## Linear Issues

   Resolves: #FUN-XXX, #FUN-YYY
   
## Testing

- How to test: [steps]
- Coverage: X% → Y%
- Critical paths: [steps]
   
## Performance

- Benchmarks: [results]
- Impact: [assessment]
   
## Breaking Changes

- [ ] None / [migration path]
   
## Checklist

- [x] Tests pass
- [x] Standards met
- [x] Docs updated
- [x] Ready for review
   EOF)"

   ```

5. Update Linear: link PR, set "In Review", add PR link to issues
6. Set up success: request reviews, add labels, enable auto-merge
7. Monitor CI/CD → respond to feedback → keep updated with main
</actions>

Create PR that makes review a pleasure. Complete, clear, ready to merge. This is your work's presentation layer - make it shine.

Take a deep breath in, count 1... 2... 3... and breathe out. You are now centered. Don't hold back. Give it your all.