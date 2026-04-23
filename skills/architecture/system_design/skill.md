# Skill: System Design

Use this skill when designing a new feature, service, workflow, or integration.

## Core Guidance

- Start with the user-visible behavior and constraints.
- Identify the main components and their responsibilities.
- Define data flow before choosing implementation details.
- Keep domain logic separate from infrastructure details.
- Make trade-offs explicit: complexity, latency, cost, reliability, and maintainability.
- Choose the smallest architecture that can handle the known requirements.

## Agent Checklist

1. Restate the system goal and non-goals.
2. List components and ownership boundaries.
3. Describe request, event, and data flow.
4. Identify persistence, external dependencies, and failure modes.
5. Explain trade-offs and the simplest viable implementation path.
6. Recommend validation: tests, observability, rollout, or review steps.

## Pitfalls

- Designing for imaginary scale.
- Hiding domain decisions in adapters.
- Creating too many layers for a small workflow.
- Ignoring operational failure modes.
