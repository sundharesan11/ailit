# Skill: Data Partitioning

Use this skill when choosing table, file, or dataset partitioning strategy.

## Core Guidance

- Partition by the most common high-selectivity filter when it matches lifecycle needs.
- Time-based partitions are usually a good default for event and fact data.
- Avoid partitions that are too small or too numerous.
- Match partition strategy to query patterns, retention, and backfill needs.
- Consider clustering, sorting, or bucketing when partitioning alone is insufficient.

## Agent Checklist

1. Identify query patterns and retention rules.
2. Estimate data volume and growth rate.
3. Choose partition key and granularity.
4. Check skew and small-file risk.
5. Describe backfill and retention operations.
6. Add validation for partition coverage where useful.

## Pitfalls

- Partitioning on high-cardinality IDs.
- Choosing daily partitions for tiny datasets.
- Forgetting late-arriving data.
- Optimizing for one query while harming common reads.
