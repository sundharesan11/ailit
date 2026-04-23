# Skill: Microservice vs Monolith

Use this skill when deciding whether to split a system into services or keep it together.

## Core Guidance

- Prefer a modular monolith until independent deployment, scaling, ownership, or compliance requires separation.
- Separate code boundaries before network boundaries.
- Split services around stable domain ownership, not technical layers.
- Account for operational costs: deploys, tracing, retries, contracts, data consistency, and on-call load.
- Use microservices when the coordination cost is lower than the coupling cost.

## Agent Checklist

1. Identify the reason for considering a split.
2. Evaluate domain boundary stability.
3. Check data ownership and consistency requirements.
4. Compare deployment, scaling, and operational trade-offs.
5. Recommend monolith, modular monolith, or service split with rationale.

## Pitfalls

- Splitting because the code feels messy.
- Sharing one database across services without clear ownership.
- Creating distributed transactions for simple workflows.
- Ignoring the team's operational maturity.
