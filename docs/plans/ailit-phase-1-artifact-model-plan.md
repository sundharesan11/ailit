---
title: AIlit Phase 1 Artifact Model Plan
created: 2026-05-11
status: active
origin: docs/brainstorms/ailit-phase-1-artifact-model-requirements.md
---

# AIlit Phase 1 Artifact Model Plan

## Scope

This plan covers the first build batch only:

1. create the solution template
2. create the solution layer README
3. update docs so artifact boundaries are clear

## Decisions

1. Use markdown files with YAML frontmatter for shared solutions
2. Keep solutions under `docs/solutions/`
3. Keep the body template simple and human-readable
4. Defer registry and runtime work to the next batch

## Implementation Units

### Unit 1: Shared solution template

Files:

- `docs/solutions/_template.md`

Work:

- define required frontmatter fields
- define standard body sections
- keep the template short enough for normal engineering use

### Unit 2: Solution layer guide

Files:

- `docs/solutions/README.md`

Work:

- explain what a solution is
- explain when to write one
- explain how it differs from skills and lessons
- explain the first-pass folder shape

### Unit 3: Artifact boundary docs

Files:

- `docs/skills.md`
- `docs/overview.md`

Work:

- add the solution layer to the knowledge model
- explain where solutions fit in the compounding workflow

## Test Scenarios

1. a junior developer can tell the difference between:
   - skill
   - solution
   - decision
   - lesson
2. the solution template is complete enough to use after real work
3. the docs remain consistent with the current architecture

## Sequence

1. create `docs/solutions/_template.md`
2. create `docs/solutions/README.md`
3. update `docs/overview.md`
4. update `docs/skills.md`
5. update the tracker status for the first batch
