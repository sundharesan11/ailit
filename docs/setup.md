# Setup

This document shows how to install AIOS, check that it works, and onboard a new project.

## Before You Start

Make sure you have:

- `python3`
- this repository available at `~/engineering_brain`
- a shell with `~/.local/bin` on the `PATH`

## Install The Global Command

Run:

```bash
~/engineering_brain/scripts/install_aios_command.sh
```

This creates a global `aios` command in:

```text
~/.local/bin/aios
```

## Verify The Installation

Run these commands:

```bash
which aios
aios --help
aios self-test
```

What success looks like:

- `which aios` prints a path
- `aios --help` shows the CLI commands
- `aios self-test` ends with `0 fail`

## Set Up A New Project

Go to the project you want to use with AIOS:

```bash
cd /path/to/project
```

Run onboarding:

```bash
aios onboard --project . --tools codex cursor claude gemini antigravity windsurf
```

This does four things:

1. creates the `ai/` folder and starter files
2. detects project context and writes `ai/context.md`
3. installs AI tool instruction files such as `AGENTS.md`
4. runs the AIOS readiness checks

## Check Project Readiness

Run:

```bash
aios doctor --project .
```

This tells you whether the project has:

- the `ai/` folder
- the expected AI context files
- the tool instruction files
- a valid AIOS setup

Warnings are normal for a new project.
They usually mean the files exist but still need real content.

## Fill In The Project AI Files

After onboarding, review these files:

```text
ai/spec.md
ai/design.md
ai/context.md
ai/decisions.md
ai/tasks.md
ai/lessons.md
```

At minimum, fill in:

- what the project does
- important architecture boundaries
- important commands and workflows
- things agents should avoid assuming

The more accurate these files are, the more useful AIOS becomes.

## Run A Simple Smoke Test

Run:

```bash
aios prepare \
  --task "smoke test AIOS setup for this project" \
  --project . \
  --tool codex
```

What success looks like:

- you see a task context block
- standards are included
- project AI files are included
- readiness warnings appear only if setup is incomplete

## Check That Skills Are Available

To see which skill sources AIOS knows about:

```bash
aios list-skill-sources
```

To check whether a skill is visible:

```bash
aios list-skills --query retry
aios list-skills --query marketing
aios list-skills --query compound
```

## When Setup Is Complete

You are ready to use AIOS when:

- `aios self-test` passes
- `aios doctor --project .` has no failures
- the project `ai/` files exist
- the tool instruction files exist
- `aios prepare` returns useful context

Next, read [How To Use](how_to_use.md).
