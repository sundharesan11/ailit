# AIlit Phase 1 Artifact Model Requirements

Created: 2026-05-11
Status: active
Origin: docs/ideation/ailit-solution-artifact-options.md

## Problem

AIlit needs a reusable shared knowledge format that sits between:

- raw project lessons
- fully promoted skills or standards

Without that middle layer, solved problems stay buried in local project notes or
are forced into `skills/`, which is the wrong abstraction.

## Goal

Define the first-pass solution artifact model for shared solved-problem
documentation.

## Requirements

### 1. The artifact must be markdown-first

The common case should be readable directly in GitHub and easy for engineers to
edit by hand.

### 2. Metadata must live in frontmatter

The first pass should use YAML frontmatter so the runtime can index solutions
without requiring a second metadata file.

Required fields:

- `title`
- `slug`
- `status`
- `owner`
- `created`
- `updated`
- `tags`
- `stack`
- `summary`
- `source_type`
- `source_refs`
- `trust`

### 3. The body must follow one standard template

Every solution should explain:

- the problem
- the context
- the root cause
- the chosen solution
- tradeoffs
- verification
- when to reuse it
- when not to reuse it

### 4. Solutions must stay separate from skills

The docs must clearly explain:

- a skill is reusable guidance
- a solution is a solved-problem writeup
- a lesson is project-local learning

### 5. The format must be low ceremony

An engineer should be able to create a useful solution note quickly after
finishing real work.

### 6. The format must be indexable later

The chosen shape should be easy for AIlit to validate and index in later
phases.

## Non-Goals

This phase does not need:

- attached evidence automation
- semantic search
- registry code
- promotion commands

## Success Criteria

This phase is successful when:

1. `docs/solutions/_template.md` exists
2. `docs/solutions/README.md` explains how to use the layer
3. docs clearly explain the boundary between solutions and skills
4. the metadata contract is stable enough for a future registry pass

## Decision

Use:

- one markdown file per solution
- YAML frontmatter
- optional richer evidence later, not in the first pass
