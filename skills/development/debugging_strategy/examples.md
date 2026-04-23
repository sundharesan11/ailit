# Debugging Strategy Examples

## Investigation Note

```text
Observed:
The parser drops rows with empty optional fields.

Hypothesis:
The normalization step treats empty string as invalid for all fields.

Validation:
Add a focused parser test with an empty optional field.
```
