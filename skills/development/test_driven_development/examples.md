# Test-Driven Development Examples

## Test Name Pattern

```text
test_retries_transient_failure_then_returns_success
test_rejects_invalid_payload_without_calling_downstream
```

## Useful Assertion Style

Assert observable behavior first, then side effects only when they are part of the contract.
