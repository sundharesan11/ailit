# Skill: Caching Patterns

Use this skill when adding or reviewing caches for performance, cost, or availability.

## Core Guidance

- Cache only after identifying the bottleneck or repeated expensive work.
- Define freshness requirements before choosing a strategy.
- Use clear keys, TTLs, and invalidation rules.
- Prefer read-through or cache-aside for simple backend reads.
- Avoid caching authorization-sensitive data unless the key includes the correct scope.
- Treat cache misses and stale reads as expected behavior.

## Agent Checklist

1. State what is cached and why.
2. Define key format, TTL, and invalidation behavior.
3. Explain stale data tolerance.
4. Add tests for hit, miss, and invalidation paths where possible.
5. Add metrics if the project already tracks cache performance.

## Pitfalls

- Adding cache before measuring need.
- Using incomplete cache keys.
- Forgetting invalidation on writes.
- Letting cache behavior become required for correctness.
