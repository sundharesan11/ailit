# Troubleshooting

This document covers the most common AIOS problems and the fastest checks to run.

## `aios` Command Not Found

### Symptom

```bash
zsh: command not found: aios
```

### What To Check

Run:

```bash
~/engineering_brain/scripts/install_aios_command.sh
which aios
```

If `which aios` still shows nothing, check whether `~/.local/bin` is on your `PATH`.

## `aios self-test` Fails

### What To Check

Run:

```bash
aios self-test
```

If any step fails, read the failing line first.
That usually tells you whether the issue is:

- registry-related
- project setup-related
- plugin-related
- path-related

## `aios doctor` Shows Warnings

### This Is Often Normal

A new project often has warnings because the `ai/` files still contain starter text.

### What To Do

Open and improve:

- `ai/spec.md`
- `ai/design.md`
- `ai/context.md`
- `ai/decisions.md`
- `ai/tasks.md`
- `ai/lessons.md`

Then run:

```bash
aios doctor --project .
```

again.

## A Skill Does Not Show Up

### What To Check

Run:

```bash
aios list-skill-sources
aios list-skills --query <skill_name>
aios index
```

### If It Is A Local AIOS Skill

Make sure the skill folder contains:

- `metadata.json`
- `skill.md`

Then run:

```bash
aios validate
```

### If It Is An Installed External Skill

Make sure:

- the skill is inside `~/.agents/skills` or `~/.codex/skills`
- the skill contains `SKILL.md`
- the source root exists

### If You Use Custom External Roots

Check:

```bash
echo $AIOS_SKILL_SOURCES
```

## `aios prepare` Looks Too Generic

### Cause

This usually means the project AI files are too empty.

### What To Do

Improve:

- `ai/spec.md`
- `ai/design.md`
- `ai/context.md`

Also try a more specific task prompt.

Bad:

```text
fix stuff
```

Better:

```text
add retry logic to the producer handler and include tests
```

## The Agent Did Not Use AIOS

### What To Check

Run:

```bash
aios doctor --project .
```

Make sure the project contains:

- `AGENTS.md`
- tool-specific instruction files where needed

### Important Note

Some tools only follow local instructions well when:

- the file exists in the project
- the agent has shell access
- the tool is actually running in agent mode

If needed, ask the agent to report the exact command it ran before editing.

## `aios prepare` Works Manually But The Agent Does Not Run It

This usually means one of these things:

1. the integration files are missing
2. the tool is not respecting local instruction files
3. the tool cannot run shell commands in the current environment

### What To Do

Reinstall integrations:

```bash
aios integrate --project . --overwrite
```

Then check the generated files.

## The Project Context Is Missing Useful Facts

If `ai/context.md` is weak, regenerate it:

```bash
aios inspect-project --project . --write --overwrite
```

Then edit the result manually if needed.

Automatic inspection helps, but it does not replace project knowledge.

## Registry Looks Out Of Date

Run:

```bash
aios index
```

Then inspect:

```bash
aios list-skills
aios list-skill-sources
```

## When You Are Not Sure What Is Broken

Run these in order:

```bash
which aios
aios --help
aios self-test
aios doctor --project .
aios list-skill-sources
```

That usually tells you whether the problem is:

- AIOS installation
- repo onboarding
- skill discovery
- tool integration

If the issue still is not clear, inspect the prepared output directly:

```bash
aios prepare --task "debug AIOS setup" --project . --tool codex
```
