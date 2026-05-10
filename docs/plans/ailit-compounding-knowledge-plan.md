---
title: AIlit Compounding Knowledge Plan
created: 2026-05-06
status: active
origin: docs/brainstorms/ailit-compounding-knowledge-requirements.md
---

# AIlit Compounding Knowledge Plan

## Problem Frame

AIlit already handles project onboarding, context preparation, and skill
loading. The next gap is compounding knowledge from real work so agents and
engineers can reuse prior solutions instead of repeating the same discovery.

This plan covers the first implementation pass for that compounding layer.

## Scope

In scope:

- define the knowledge artifact model
- add a solution library structure
- add commands for structured capture and promotion
- add registry and retrieval support for solutions
- make the backlog trackable for parallel execution

Out of scope for this pass:

- semantic vector search
- web UI
- enterprise policy engine
- automatic fully autonomous promotion

## Target Architecture

The knowledge layer should use five artifact classes:

1. `standards/` for stable reusable rules
2. `skills/` for reusable task guidance
3. `docs/solutions/` for solved-problem writeups
4. project `ai/decisions.md` for local decision memory
5. project `ai/lessons.md` for local lessons

Shared solutions should be treated as a first-class retrieval source, not
hidden inside free-form notes.

## Proposed Delivery Phases

### Phase 1: Artifact model and templates

Goal:
- define the structure and metadata for solutions and captured lessons

Deliverables:
- `docs/solutions/README.md`
- `docs/solutions/_template.md`
- metadata rules for solution documents
- documentation describing when to use skills vs solutions vs lessons

Implementation units:
- `docs/solutions/README.md`
- `docs/solutions/_template.md`
- `docs/skills.md`
- `docs/overview.md`

Test scenarios:
- template is readable and complete for junior developers
- metadata fields are explicit and consistent
- docs explain artifact boundaries without overlap

### Phase 2: Solution registry and discovery

Goal:
- allow AIlit to index and find shared solution documents

Deliverables:
- solution index file
- runtime loader for solutions
- list/search commands for solution discovery

Implementation units:
- `aios/solution_registry.py` or `aios/knowledge_registry.py`
- `aios/cli.py`
- `registry/solutions.json`

Test scenarios:
- indexing finds valid solution docs
- invalid solution docs are rejected clearly
- `aios list-solutions` returns usable results
- search by tags and stack terms returns expected matches

### Phase 3: Capture and promotion commands

Goal:
- make post-work knowledge capture practical

Deliverables:
- `aios capture-solution`
- `aios promote-lesson`
- `aios list-knowledge`

Implementation units:
- `aios/cli.py`
- new capture/promotion runtime modules
- docs under `docs/how_to_use.md` and `docs/action_flow.md`

Test scenarios:
- a solution can be created from a template
- a project lesson can be promoted into a shared solution
- metadata is preserved during promotion
- commands fail clearly on missing project context

### Phase 4: Retrieval in prepare

Goal:
- let `aios prepare` include relevant solutions in task context

Deliverables:
- solution matching in runtime preparation
- context output sections for reusable solutions

Implementation units:
- `aios/context_builder.py`
- `aios/prepare.py`
- `aios/matcher.py` or new retrieval helpers

Test scenarios:
- prepare output can include matching solutions
- no-solution cases remain clean
- prompt output stays readable and bounded

### Phase 5: Governance and freshness

Goal:
- avoid low-quality shared knowledge decay

Deliverables:
- trust and review fields
- stale detection rules
- ownership metadata

Implementation units:
- registry builders
- validators
- docs describing governance rules

Test scenarios:
- draft vs reviewed status is visible
- stale solutions are detectable
- invalid metadata is reported during validation

## Dependencies And Sequencing

Recommended sequence:

1. artifact model and templates
2. solution registry
3. capture and promotion commands
4. prepare integration
5. governance and freshness

Phase 4 should not start until the artifact model and registry shape are stable.

## Risks

1. Too much knowledge goes into `skills/` and the system becomes noisy
2. Capture workflow becomes too heavy for normal project use
3. Shared knowledge quality degrades without review metadata
4. Prepare output grows too large if solutions are loaded without limits

## Decisions

1. Use `docs/solutions/` for shared solved-problem writeups in the first pass
2. Keep project-local memory in `ai/decisions.md` and `ai/lessons.md`
3. Treat solutions as separate from skills
4. Build simple keyword-and-metadata retrieval first; defer semantic search

## Parallel Worktree Split

Once Phase 1 is approved, work can be split across worktrees like this:

1. Artifact and docs lane
   - solution templates
   - docs updates

2. Registry and validation lane
   - indexing
   - metadata validation
   - registry output

3. Runtime integration lane
   - capture commands
   - retrieval in `prepare`
   - CLI wiring

## Ready-To-Start Backlog

The first build batch should start with:

1. create the solution template and metadata contract
2. add a solution indexer and registry file
3. add `list-solutions`
4. add `capture-solution`
5. add `promote-lesson`
6. wire solution retrieval into `prepare`
