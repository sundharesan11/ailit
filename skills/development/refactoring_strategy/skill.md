# Skill: Refactoring Strategy

Use this skill when improving code structure while preserving behavior.

## Core Guidance

- Define the behavior that must remain unchanged.
- Create or identify tests before restructuring risky code.
- Refactor in small, reviewable steps.
- Rename and extract only when it improves clarity.
- Keep unrelated cleanup out of feature work unless it directly reduces risk.
- Stop when the current task is simpler and safer.

## Agent Checklist

1. Identify the refactoring goal.
2. Identify safety checks or tests.
3. Make one structural change at a time.
4. Run focused validation after meaningful steps.
5. Explain behavior-preserving intent in the summary.

## Pitfalls

- Combining refactor and behavior change without tests.
- Moving code without improving boundaries.
- Chasing perfect structure beyond the current need.
- Touching unrelated files.
