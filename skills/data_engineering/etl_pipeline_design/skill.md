# Skill: ETL Pipeline Design

Use this skill when designing ingestion, transformation, loading, or data quality workflows.

## Core Guidance

- Define source contracts, target contracts, and ownership before implementation.
- Separate extraction, transformation, validation, and loading steps.
- Make pipeline runs observable: inputs, outputs, row counts, timing, and failures.
- Prefer idempotent loads so reruns are safe.
- Capture schema drift and data quality failures explicitly.
- Design for backfill and replay early.

## Agent Checklist

1. Identify source, destination, cadence, and volume.
2. Define schema and data quality expectations.
3. Choose full load, incremental load, or change data capture.
4. Specify idempotency and recovery behavior.
5. Add tests for transformations and validation rules.
6. Describe monitoring and alerting signals.

## Pitfalls

- Mixing transformation logic into extraction code.
- Assuming source schemas do not change.
- Making reruns create duplicate records.
- Failing silently on partial loads.
