# AIlit Compounding Knowledge Requirements

Created: 2026-05-06
Status: active

## Problem

AIlit can prepare agent context before work starts, but it is still weak at
capturing, organizing, and reusing knowledge after work is done.

That leaves a major gap:

- the agent does not reliably learn from completed work
- the human user does not get a clean solved-problem library
- teams using the same stack cannot easily reuse proven patterns

## Goal

Extend AIlit from a setup and context runtime into a compounding engineering
system that helps both:

- the agent doing the work now
- the next engineer or team working on a similar problem later

## Users

1. Solo developers who want durable learning across projects
2. Teams sharing similar stacks, patterns, and operating rules
3. Organizations that want approved reusable engineering knowledge

## Desired Outcome

After a real project task is completed, AIlit should help convert execution into
reusable knowledge at the right level:

- project-local lesson
- stack-level reusable solution
- org-level reusable skill or standard

## Requirements

### 1. Structured knowledge types

AIlit must separate different kinds of knowledge instead of forcing everything
into `skills/`.

The system should support at least:

- standards
- skills
- solutions
- decisions
- lessons

### 2. Post-work capture

After meaningful work, the system should support structured capture of:

- problem solved
- context
- root cause
- chosen approach
- tradeoffs
- verification
- reuse guidance

### 3. Promotion flow

Knowledge should be able to move through a clear path:

1. task execution
2. project lesson
3. reviewed solution note
4. reusable shared pattern
5. optional skill or standard update

### 4. Shared stack reuse

Teams working with similar stacks should be able to find and reuse prior
patterns.

Examples:

- retry logic for workers
- auth token refresh handling
- ETL partitioning approaches
- background job failure handling

### 5. Unified retrieval

Task preparation should eventually load more than skills.

It should be able to pull relevant:

- skills
- solutions
- project decisions
- lessons
- stack-specific patterns

### 6. Knowledge quality controls

Shared knowledge should support:

- owner
- source
- trust level
- review status
- created date
- updated date
- deprecation or stale status

### 7. Real project usability

The system must remain simple enough for live project use.

That means:

- fast lookup
- lightweight capture
- clear defaults
- no large manual ceremony after every task

## Non-Goals

This phase does not need to build:

- a hosted SaaS product
- a UI dashboard
- deep semantic search on day one
- full enterprise governance

## Success Criteria

This phase is successful when:

1. AIlit has a clear artifact model for knowledge
2. A user can capture a solved problem in a structured way
3. Shared stack patterns can be stored and found again
4. `aios prepare` has a path to load reusable solution knowledge later
5. The backlog is clear enough to split implementation across multiple worktrees

## Open Questions

1. Where should reviewed shared solutions live: `docs/solutions/` or a separate
   top-level `solutions/` tree?
2. Should promotion into shared skills be fully manual at first, or partially
   suggested by the runtime?
3. What is the minimum metadata needed before shared knowledge is considered
   trustworthy?
