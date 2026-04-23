# Skill: Event-Driven Design

Use this skill when designing producers, consumers, queues, topics, workflows, or asynchronous processing.

## Core Guidance

- Use events to decouple producers from consumers when timing or ownership differs.
- Name events after facts that happened, not commands to perform.
- Make consumers idempotent whenever delivery can repeat.
- Define retry, dead-letter, and replay behavior before production use.
- Decide ordering requirements explicitly.
- Treat schema evolution as part of the design.

## Agent Checklist

1. Identify producers, consumers, and event ownership.
2. Define event schema and versioning expectations.
3. State delivery guarantees and duplicate handling.
4. Describe retry, dead-letter, replay, and monitoring strategy.
5. Add tests for idempotency and failure paths where practical.

## Pitfalls

- Using events when a direct call is simpler.
- Publishing vague events such as `data_updated`.
- Assuming exactly-once delivery without infrastructure proof.
- Forgetting replay safety.
