# ETL Pipeline Design Examples

## Pipeline Skeleton

```text
Extract raw records -> validate source shape -> transform -> validate target shape -> load -> audit run
```

## Minimum Audit Fields

- Run id
- Source name
- Started and finished timestamps
- Input row count
- Output row count
- Failure reason, if any
