# System Design Examples

## Prompt

```text
Design a service that accepts upload jobs, validates files, and stores normalized records.
```

## Useful Output Shape

```text
Components:
- API handler
- Job queue
- Worker
- Validation module
- Storage adapter

Data Flow:
Client -> API -> queue -> worker -> validator -> database/object storage

Trade-offs:
- Queue adds operational overhead but isolates long-running work from request latency.
```
