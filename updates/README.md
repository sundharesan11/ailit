# Updates

Use this folder to record reusable lessons, changes, and improvements to the Personal AI Engineering OS.

## Entry Template

```markdown
# YYYY-MM-DD: Short Title

## Context

What happened, and where did the lesson come from?

## Change

What standard, skill, prompt, agent, or script changed?

## Reason

Why does this improve future AI-assisted engineering work?

## Follow-Up

What should be revisited later?
```

## Usage Notes

- Keep entries short and action-oriented.
- Capture reusable knowledge, not project-specific status updates.
- Link to project decisions only when they contain a broadly useful lesson.

## CLI

Create a reusable update:

```bash
python3 ~/engineering_brain/scripts/aios.py capture-update \
  --title "Short title" \
  --context "Where the lesson came from" \
  --change "What should change" \
  --reason "Why this improves future AI-assisted engineering"
```
