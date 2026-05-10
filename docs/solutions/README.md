# Solutions

This folder is for shared solved-problem writeups.

## What A Solution Is

A solution is a reusable note about how a real engineering problem was solved.

It is meant to help:

- the next engineer facing a similar problem
- the next agent preparing context for similar work

## When To Write A Solution

Write a solution when the work produced something worth reusing beyond one
project.

Good examples:

- a retry pattern that worked well for worker failures
- a safe way to handle auth token refresh races
- a practical ETL partitioning approach
- a debugging pattern for a recurring production issue

Do not write a solution for every tiny task.

## How Solutions Differ From Other Knowledge

### Standard

A standard is a stable rule.

Example:

- prefer small, testable modules

### Skill

A skill is reusable guidance for how to approach a class of work.

Example:

- retry strategy
- debugging strategy

### Solution

A solution is a writeup of how a real problem was solved and when that solution
should be reused.

Example:

- how we fixed duplicate processing in a queue worker

### Decision

A decision is project-local memory about why one project chose a direction.

### Lesson

A lesson is project-local learning from work, incidents, or mistakes.

## First-Pass Structure

In the first pass, each shared solution is one markdown file with YAML
frontmatter.

Example:

```text
docs/solutions/backend/retry-worker-failures.md
```

The normal case should stay simple:

- one file
- clear metadata
- one body template

If richer evidence is needed later, it can be added in a future phase.

## Template

Use:

```text
docs/solutions/_template.md
```

Copy the template, rename it for the problem, then fill in the sections with
real information.

## Current Commands

Phase 2 adds the first solution-registry commands:

```bash
aios index-solutions
aios list-solutions
aios list-solutions --query retry
aios validate-solutions
aios capture-solution --title "..." --owner "..." --summary "..." --problem "..." --context "..." --solution "..."
aios promote-lesson --project . --title "..." --owner "..." --summary "..." --solution "..."
```

## Naming Guidance

Use descriptive file names that match the problem being solved.

Good examples:

- `retry-worker-failures.md`
- `token-refresh-race-handling.md`
- `etl-partitioning-for-large-backfills.md`

## Metadata Rules

Each solution should include frontmatter fields for:

- title
- slug
- status
- owner
- created
- updated
- tags
- stack
- summary
- source_type
- source_refs
- trust

These fields make later indexing and filtering possible.

Additional governance fields:

- review_status
- reviewed_by
- last_reviewed

## Review And Trust

Use these fields consistently:

- `trust: draft`
  - normal starting state
- `trust: reviewed`
  - reviewed and safe for broader reuse
- `trust: vendor`
  - trusted shared or provider-approved pattern
- `trust: untrusted`
  - indexed, but not trusted for normal reuse

Use these review states:

- `review_status: draft`
- `review_status: needs_review`
- `review_status: reviewed`

If a solution is marked as `reviewed`, it should also include:

- `reviewed_by`
- `last_reviewed`

## Freshness

Solutions can go stale.

The registry marks a solution as stale when its `updated` date is older than the
current freshness threshold.

You can inspect this with:

```bash
aios list-solutions --stale only
aios list-solutions --review-status reviewed
```

## Writing Guidance

Keep the writeup practical.

A good solution should answer:

- what problem happened?
- what was the root cause?
- what did we do?
- what tradeoffs did we accept?
- how did we verify it?
- when should someone reuse this?
- when should they not reuse it?
