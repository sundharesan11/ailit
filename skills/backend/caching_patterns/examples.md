# Caching Patterns Examples

## Cache-Aside Flow

```text
Read key from cache.
If hit, return value.
If miss, fetch from source, store with TTL, return value.
```

## Review Question

What is the worst acceptable stale value age for this data?
