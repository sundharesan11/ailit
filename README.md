# Personal AI Engineering OS

AIOS is a local developer tool that acts as a cross-tool context and workflow
runtime for coding agents.

It is designed to work with tools such as Codex, Cursor, Claude Code, Gemini CLI,
Antigravity, and Windsurf.

![AIOS overview diagram](docs/assets/ailit-objective-diagram.svg)

## Why This Exists

AI coding tools are useful, but they often start with too little project context.
That leads to repeated prompting, inconsistent code quality, and weak project memory.

AIOS adds a simple runtime layer that helps agents:

- load reusable engineering standards
- load relevant skills for the current task
- read project AI context from the target repository
- prepare a cleaner task context before non-trivial work

AIOS is not only a prompt builder.
Prompt preparation is one part of the system, but AIOS also handles:

- project onboarding
- skill discovery
- agent integration files
- project readiness checks
- reusable project memory

## Quick Start

Install the global command:

```bash
~/engineering_brain/scripts/install_aios_command.sh
```

Check that it works:

```bash
which aios
aios --help
aios self-test
```

Onboard a project:

```bash
cd /path/to/project
aios onboard --project . --tools codex cursor claude gemini antigravity windsurf
aios doctor --project .
```

## Documentation

Start here:

- [Overview](docs/overview.md)
- [Setup](docs/setup.md)
- [How To Use](docs/how_to_use.md)
- [Action Flow](docs/action_flow.md)
- [Skills](docs/skills.md)
- [Architecture](docs/architecture.md)
- [Troubleshooting](docs/troubleshooting.md)

## Common Use Cases

- set up a new project for AI-assisted development
- make sure coding agents use project context before editing
- manage reusable engineering skills in one place
- verify that installed skills are visible to AIOS
- keep project decisions and lessons easy to reuse

## How AIOS Fits With Codex And Claude

Tools like Codex and Claude Code already have native ways to load instructions.
For example, they can read local project instruction files such as `AGENTS.md`
or `CLAUDE.md`.

AIOS does not replace those systems.
Instead, it gives you one local workflow that can support multiple agent tools in
a consistent way.

## Current Status

AIOS is a working local tool and repository. It includes:

- a global `aios` command
- a project onboarding flow
- a project readiness checker
- a prompt preparation runtime
- a local and external skill registry
- integrations for major coding-agent tools

For the full explanation, use the docs linked above.
