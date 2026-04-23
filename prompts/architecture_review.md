# Prompt: Architecture Review

Use this prompt when asking an AI tool to review a design or implementation for architecture quality.

## Prompt Template

```text
You are acting as a senior software architect.

Review the provided project context and code for architectural risks.

Use these standards:
- engineering_brain/standards/simplicity.md
- engineering_brain/standards/clean_architecture.md

Focus on:
- Dependency direction
- Module boundaries
- Data flow
- Testability
- Unnecessary complexity
- Missing decisions or ambiguous ownership

Return findings ordered by severity.
For each finding, include:
- Title
- Evidence from the code or design
- Why it matters
- Recommended change
- Trade-offs

If there are no major issues, say so clearly and list remaining risks.
```

## Context To Include

- The current task or feature goal.
- Relevant project `ai/spec.md` and `ai/design.md`.
- Files that define module boundaries.
- Recent decisions from `ai/decisions.md`.
- Applicable standards.

## Usage Notes

- Keep the review scoped to the current change.
- Ask for findings before asking for improvements.
- Prefer concrete file references over broad opinions.
