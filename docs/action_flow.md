# Action Flow

This document explains how AIOS is used in real work and what happens step by step.

## The Two Main Flows

There are two important flows:

1. project setup flow
2. task execution flow

## Flow 1: Project Setup

This is what happens when you prepare a new project for AI-assisted development.

### Step 1: Run onboarding

```bash
aios onboard --project . --tools codex cursor claude gemini antigravity windsurf
```

### Step 2: AIOS creates project AI files

AIOS creates:

```text
ai/spec.md
ai/design.md
ai/context.md
ai/decisions.md
ai/tasks.md
ai/lessons.md
```

### Step 3: AIOS inspects the project

It tries to detect:

- languages
- frameworks
- package managers
- test commands
- useful source paths

That information is written into `ai/context.md`.

### Step 4: AIOS installs tool instructions

It creates files such as:

- `AGENTS.md`
- `CLAUDE.md`
- `GEMINI.md`
- `.cursor/rules/ai-os.mdc`
- `.windsurf/rules/ai-os.md`

These files tell supported agents how to use AIOS.

### Step 5: AIOS checks readiness

It runs the same checks as:

```bash
aios doctor --project .
```

The result tells you what is ready and what still needs attention.

## Flow 2: Task Execution

This is what happens during normal developer use.

### Step 1: The developer asks the agent to do work

Example:

```text
Add retry logic to the producer handler.
```

### Step 2: The agent reads the project instructions

The agent should see `AGENTS.md` or the tool-specific rule file.

Those instructions tell it to run:

```bash
aios prepare --task "..." --project . --tool <tool>
```

### Step 3: AIOS runs the readiness checks

If `prepare` is using doctor checks, AIOS first looks for problems such as:

- missing `ai/` files
- missing integration files
- template-only context files

If warnings exist, AIOS includes them in the output.

### Step 4: AIOS matches useful skills

AIOS looks at the task and compares it against the skill registry.

The registry may contain:

- local AIOS skills
- installed external skills
- imported vendor skills

### Step 5: AIOS loads standards

It loads the global engineering standards, such as:

- simplicity
- clean architecture
- test-driven development

### Step 6: AIOS loads project context

It reads project AI files such as:

- `ai/spec.md`
- `ai/design.md`
- `ai/context.md`
- `ai/decisions.md`
- `ai/tasks.md`
- `ai/lessons.md`

### Step 7: AIOS builds the task context

It combines:

- operating instructions
- standards
- selected skills
- project files
- the original task

### Step 8: AIOS formats the result for the tool

The output is shaped for the requested tool, such as:

- Codex
- Cursor
- Claude
- Gemini
- Antigravity
- Windsurf

### Step 9: The agent does the actual work

At this point, the coding agent uses the prepared context and starts editing, debugging, reviewing, or designing.

## Flow 3: After The Task

After meaningful work, you may want to save useful knowledge.

Common follow-up actions include:

```bash
aios log-decision --project .
aios capture-lesson --project .
aios add-task --project .
```

This helps future sessions work with better memory.

## Simple End-To-End Example

Here is the normal full flow:

1. onboard the project
2. fill in the `ai/` files
3. open the project in your coding tool
4. ask the agent for a task
5. the agent runs `aios prepare`
6. the agent works with the returned context
7. save decisions and lessons when needed

## What The Developer Normally Runs

In day-to-day use, the developer mainly runs:

- `aios onboard`
- `aios doctor`
- `aios list-skills`
- `aios self-test`

The agent should normally run:

- `aios prepare`

That distinction is important.

The setup and maintenance commands are usually for you.
The task-preparation command is usually for the agent.
