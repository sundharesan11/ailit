# Event-Driven Design Examples

## Event Shape

```json
{
  "event_name": "invoice_paid",
  "event_version": 1,
  "event_id": "evt_123",
  "occurred_at": "2026-04-20T10:00:00Z",
  "payload": {
    "invoice_id": "inv_123",
    "account_id": "acct_123"
  }
}
```

## Review Questions

- Can the consumer process the same event twice safely?
- What happens after repeated failure?
- Can old consumers tolerate new event fields?
