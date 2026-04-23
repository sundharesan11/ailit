# Retry Strategy Examples

## Basic Policy

```text
Retry:
- Connection reset
- Timeout
- HTTP 429 or 503 when allowed by the API contract

Do Not Retry:
- Validation errors
- Authentication failures
- Business rule rejections
```

## Test Cases

- Succeeds on second attempt after one transient error.
- Stops immediately on a non-retryable error.
- Raises or records final failure after max attempts.
