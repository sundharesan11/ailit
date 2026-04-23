# Skill: Example Skill

This is a template for a reusable AI engineering skill. Copy this folder when creating a new skill and replace the example content with task-specific guidance.

## When To Use

Use this skill when:

- The request matches the skill's purpose.
- The task appears repeatedly across projects.
- The agent needs consistent instructions, examples, or review criteria.

Do not use this skill when the task is project-specific and should live in the repository's `ai/` folder instead.

## Inputs

- User request or task description.
- Relevant project files.
- Applicable standards from `engineering_brain/standards/`.
- Known constraints such as runtime, framework, language, or deployment target.

## Process

1. Restate the goal in concrete terms.
2. Inspect local context before making assumptions.
3. Choose the smallest useful implementation path.
4. Apply the relevant standard or checklist.
5. Run focused validation.
6. Summarize changes, risks, and next steps.

## Output Format

The agent should return:

- What changed.
- Which files were touched.
- What validation was run.
- Any risks or follow-up work.

## Examples

### Example Prompt

```text
Use the example_skill guidance to add a small utility function and tests.
Keep the change scoped to the existing module.
```

### Example Result

```text
Added the utility, covered the expected and edge cases, and ran the focused test file.
```

## Pitfalls

- Loading too much unrelated context.
- Treating this template as a real task skill.
- Mixing global reusable guidance with one project's temporary facts.

## Maintenance Notes

Update the skill when:

- A workflow repeats across two or more projects.
- A failure pattern keeps appearing in agent output.
- A new tool or framework changes the recommended approach.
