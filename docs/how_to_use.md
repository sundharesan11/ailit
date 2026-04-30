# How To Use

This document explains how to use AIOS in normal day-to-day development.

## The Simple Rule

Use AIOS in two ways:

- you run setup and maintenance commands
- the agent runs `aios prepare` before non-trivial work

AIOS works with the native instruction system of the coding tool.
It does not replace files like `AGENTS.md` or `CLAUDE.md`.
Instead, it uses those files as the way to trigger the shared AIOS runtime.

## Most Common Commands

### Setup commands

Use these when starting a new project or fixing setup:

```bash
aios onboard --project . --tools codex cursor claude gemini antigravity windsurf
aios doctor --project .
aios inspect-project --project .
aios inspect-project --project . --write
```

### Task preparation command

This is the main runtime command:

```bash
aios prepare --task "add retry logic" --project . --tool codex
```

In normal use, the coding agent should run this command itself.

### Skill discovery commands

Use these to inspect the registry:

```bash
aios list-skill-sources
aios list-skills
aios list-skills --query marketing
aios list-skills --query compound
aios match "design retry strategy"
aios load retry_strategy
```

### Maintenance commands

Use these when checking or rebuilding the system:

```bash
aios index
aios validate
aios self-test
```

### Memory commands

Use these to store useful project knowledge:

```bash
aios log-decision --project .
aios capture-lesson --project .
aios add-task --project .
aios capture-update
```

## Normal Workflows

## Workflow 1: Start Using AIOS In A New Repo

Run:

```bash
cd /path/to/project
aios onboard --project . --tools codex cursor claude gemini antigravity windsurf
aios doctor --project .
```

Then:

1. open the `ai/` files
2. replace the template text with real project information
3. ask your agent to work in the repo

## Workflow 2: Check Whether A Skill Is Available

Run:

```bash
aios list-skills --query retry
aios list-skills --query marketing
aios list-skills --query compound
```

If needed, test a direct load:

```bash
aios load marketing_ideas
```

## Workflow 3: Debug AIOS Setup

Run:

```bash
aios doctor --project .
aios list-skill-sources
aios self-test
```

This tells you whether the issue is:

- the project setup
- the skill registry
- the local AIOS installation

## Workflow 4: Manually Inspect What The Agent Would See

If you want to inspect the prepared context yourself, run:

```bash
aios prepare --task "refactor the order sync worker" --project . --tool codex
```

This is useful for debugging or improving project AI files.

## Using AIOS With Different Tools

### Codex

AIOS writes `AGENTS.md` for shared instructions.
Codex should read it and run `aios prepare` before non-trivial work.

### Cursor

AIOS writes both:

- `AGENTS.md`
- `.cursor/rules/ai-os.mdc`

### Claude Code

AIOS writes:

- `AGENTS.md`
- `CLAUDE.md`

### Gemini CLI and Antigravity

AIOS writes:

- `AGENTS.md`
- `GEMINI.md`

### Windsurf

AIOS writes:

- `AGENTS.md`
- `.windsurf/rules/ai-os.md`

## What You Should Fill In Manually

AIOS can create the files, but it cannot know your project intent on its own.

The most important files to improve are:

- `ai/spec.md`
- `ai/design.md`
- `ai/context.md`

If these files stay generic, the agent context will also stay generic.

## Good Habits

These habits make AIOS much more useful:

- keep `ai/spec.md` current
- record important architecture decisions
- review `ai/context.md` after major project changes
- check whether useful new skills are visible in the registry
- run `aios doctor` when something feels wrong

## When To Use Manual Commands

You do not need to run every command all the time.

Use manual commands mainly for:

- initial setup
- troubleshooting
- checking skills
- previewing prompt output
- storing durable project knowledge

For the full runtime behavior, see [Action Flow](action_flow.md).
