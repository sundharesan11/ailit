"""Initialize project-level AI context files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


PROJECT_TEMPLATES: dict[str, str] = {
    "spec.md": """# Project Spec

Use this file to describe what the project is supposed to do.

## Purpose

Describe the product, service, library, or system in a few paragraphs.

## Users

- Who uses this project?
- What jobs are they trying to complete?
- What outcomes matter most?

## Core Workflows

- Workflow 1:
- Workflow 2:
- Workflow 3:

## Requirements

- Functional requirement:
- Non-functional requirement:
- Constraint:

## Out Of Scope

- List work that should not be assumed by AI agents.

## Success Criteria

- How do we know a change is correct?
- Which tests, metrics, or behaviors matter?
""",
    "design.md": """# Project Design

Use this file to document the system structure that AI agents should respect.

## Architecture Overview

Describe the major components and how they communicate.

## Module Boundaries

- Module:
  - Responsibility:
  - Depends on:
  - Should not depend on:

## Data Flow

Describe the important request, event, job, or data paths.

## Persistence

- Database or storage:
- Ownership rules:
- Migration expectations:

## External Integrations

- Integration:
  - Purpose:
  - Failure behavior:

## Testing Strategy

- Unit tests:
- Integration tests:
- End-to-end or manual validation:

## Operational Notes

- Deployment:
- Observability:
- Common failure modes:
""",
    "context.md": """# Project Context

Use this file for practical facts an AI agent needs before editing the repo.

## Tech Stack

- Language:
- Framework:
- Package manager:
- Runtime:
- Database:

## Common Commands

```bash
# Install dependencies

# Run tests

# Run lint or formatting

# Start development server
```

## Repository Conventions

- Naming:
- File organization:
- Testing patterns:
- Error handling:

## Important Paths

- Source:
- Tests:
- Configuration:
- Scripts:

## Agent Notes

- Things agents should always do:
- Things agents should avoid:
""",
    "decisions.md": """# Project Decisions

Use this file to record durable project decisions.

## Decision Template

### YYYY-MM-DD: Decision Title

**Context:** What problem or trade-off led to this decision?

**Decision:** What did we choose?

**Reasoning:** Why is this the right choice for now?

**Consequences:** What gets easier, harder, or constrained?

**Review Date:** When should this be revisited?
""",
    "tasks.md": """# AI Task Backlog

Use this file to keep AI-assisted engineering work explicit and reviewable.

## Active

- [ ] Task:
  - Goal:
  - Context:
  - Validation:

## Next

- [ ] Task:

## Done

- [x] Example completed task:
""",
    "lessons.md": """# Project Lessons

Use this file to capture lessons specific to this repository.

Reusable engineering lessons should move into `~/engineering_brain/updates/`
or become a global skill.

## Lesson Template

### YYYY-MM-DD: Lesson Title

**Situation:** What happened?

**Lesson:** What should agents or developers remember?

**Applies To:** Which modules, workflows, or commands?

**Reusable Globally:** Yes or no.
""",
}


@dataclass(frozen=True)
class InitResult:
    """Result of initializing project AI context."""

    project_root: Path
    created: list[Path]
    skipped: list[Path]
    overwritten: list[Path]


def init_project(project_path: str | Path, overwrite: bool = False) -> InitResult:
    """Create project ai/ context files.

    Existing files are skipped unless overwrite is true.
    """
    project_root = Path(project_path).expanduser().resolve()
    ai_dir = project_root / "ai"
    ai_dir.mkdir(parents=True, exist_ok=True)

    created: list[Path] = []
    skipped: list[Path] = []
    overwritten: list[Path] = []

    for filename, template in PROJECT_TEMPLATES.items():
        path = ai_dir / filename
        content = template.strip() + "\n"

        if path.exists() and not overwrite:
            skipped.append(path)
            continue

        if path.exists() and overwrite:
            overwritten.append(path)
        else:
            created.append(path)

        path.write_text(content, encoding="utf-8")

    return InitResult(
        project_root=project_root,
        created=created,
        skipped=skipped,
        overwritten=overwritten,
    )
