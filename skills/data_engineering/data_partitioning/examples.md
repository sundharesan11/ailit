# Data Partitioning Examples

## Time-Based Events

```text
Partition: event_date
Cluster or sort: account_id, event_type
Reason: most queries filter by date range first, then account.
```
