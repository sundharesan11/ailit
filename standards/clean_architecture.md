# Standard: Clean Architecture

Use this standard when a task touches boundaries, dependencies, data flow, or long-lived business logic.

## Purpose

Clean architecture protects core business behavior from external details such as frameworks, databases, APIs, and user interfaces.

## Principles

- Put business rules near the center of the system.
- Keep infrastructure details behind interfaces or adapters.
- Let dependencies point inward toward stable policy.
- Make side effects visible at the boundary.
- Keep domain concepts independent from transport and storage formats.

## AI Agent Instructions

When applying this standard:

1. Identify the core behavior that should not depend on tooling.
2. Separate orchestration from domain decisions.
3. Place integrations at the edge of the design.
4. Avoid leaking framework types into domain code unless the project already standardizes on that pattern.
5. Prefer explicit contracts over implicit coupling.

## Review Checklist

- Can core behavior be tested without network, database, or UI setup?
- Are adapters thin and easy to replace?
- Do dependency directions match the stability of the code?
- Are external errors translated into domain-level outcomes?
- Is the architecture still proportional to the problem size?

## Common Pitfalls

- Creating too many layers for a small script.
- Treating every class as an interface boundary.
- Letting ORM models become the entire domain model by accident.
- Hiding simple workflows behind abstract names.
