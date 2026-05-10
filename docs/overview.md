# Overview

This document explains what AIOS is, why it was built, where it fits, and when it is useful.

## What AIOS Is

AIOS started as a personal AI engineering setup, but the model is not limited to
one person.

It is a local-first system that helps AI coding agents work with better context.
Instead of starting from a blank prompt, an agent can use AIOS to load:

- engineering standards
- reusable skills
- reusable solutions
- project-specific AI files
- tool-specific instructions

In simple terms, AIOS is the layer between:

- your coding agent
- your engineering knowledge
- your project context

The best short description is:

```text
AIOS is a cross-tool context and workflow runtime for coding agents.
```

In practice, AIOS can be used in three ways:

- by one developer as a personal setup
- by a team as a shared engineering workflow
- by an organization as a standard AI engineering layer across many repos

## Why It Was Built

Most AI coding tools are strong at generating code, but they often have the same problems:

- they do not know your preferred engineering standards
- they do not know past project decisions
- they do not always use the right context for the current task
- they make you repeat the same instructions again and again

AIOS was built to reduce that friction.

It gives agents a repeatable way to prepare before work starts.

## What Problem It Solves

Without AIOS, a common flow looks like this:

1. you ask the agent to do something
2. the agent reads a few files
3. the agent guesses what matters
4. you correct it or add missing context

With AIOS, the flow becomes:

1. you ask the agent to do something
2. the agent runs `aios prepare`
3. AIOS loads standards, skills, and project context
4. the agent starts with a better task context

This does not make the agent perfect.
It simply gives it a better starting point.

## Is AIOS Just A Prompt Builder

No.

AIOS does build task-ready prompt context, but that is only one part of the system.

AIOS also handles:

- project onboarding
- readiness checks
- skill discovery and indexing
- reusable solution guidance
- local instruction-file setup
- project memory support

So it is more accurate to think of AIOS as:

```text
prompt builder + skill registry + project memory layer + agent integration layer
```

## Who Should Use It

AIOS is useful for:

- solo developers using AI heavily
- engineers working across several repos
- developers who want shared project rules for multiple AI tools
- teams building reusable local AI workflows
- organizations that want one approved setup for AI-assisted development

It is especially useful if you use more than one agent tool and want a single source of truth.

## What AIOS Is Not

AIOS is not:

- a hosted product
- a replacement for your coding agent
- a full plugin marketplace
- a project management system
- a full agent platform like a cloud execution product

It is a local engineering support layer.

## How AIOS Fits With Native Tool Features

Modern coding tools already have their own native instruction systems.

Examples:

- Codex can use `AGENTS.md`
- Claude Code can use `CLAUDE.md`
- other tools use their own local rule or memory files

AIOS is meant to work with those systems, not compete with them.

The idea is simple:

- let each tool keep its native instruction model
- use AIOS as the shared local layer behind them

That gives you one engineering brain that can support several tools.

## Personal To Org-Shareable

AIOS does not need to stay personal.

The same structure can be shared in an organization by treating the repository as
a common runtime and knowledge base.

That usually means:

- shared standards live in one maintained repo
- approved skills are indexed once and reused across projects
- each project keeps its own local `ai/` context
- supported coding tools use the same onboarding and preparation flow

This gives teams a middle ground between two bad extremes:

- every developer invents their own agent workflow
- one rigid central system tries to hide project-level context

AIOS works better as a shared layer with local project context on top.

## Main Ideas Behind AIOS

### 1. Global engineering knowledge

AIOS stores reusable knowledge in one place:

- standards
- skills
- solutions
- prompts
- agent guidance

That knowledge can be maintained by one developer, a team, or a platform group.

### 2. Project-specific context

Each project can keep its own `ai/` folder with files like:

- `spec.md`
- `design.md`
- `context.md`
- `decisions.md`
- `tasks.md`
- `lessons.md`

### 3. Runtime preparation

Before real work starts, AIOS can build a task-ready prompt by combining:

- standards
- matching skills
- matching reusable solutions when relevant
- project AI files
- the user task

### 4. Tool integration

AIOS writes local instruction files so agents know how to use it automatically.

### 5. Cross-tool consistency

AIOS helps keep the workflow similar across:

- Codex
- Claude Code
- Cursor
- Gemini CLI
- Antigravity
- Windsurf

## Typical Use Cases

Here are common ways developers use AIOS:

### Set up a new repo for AI work

Use `aios onboard` to create project AI files and tool integrations.

### Check whether a repo is AI-ready

Use `aios doctor` to find missing files, weak context, or setup gaps.

### Prepare better task context

Use `aios prepare` to assemble the prompt parts an agent should see.

### Reuse one workflow across several coding tools

Use AIOS when you do not want to redesign your setup for each agent separately.

### Manage reusable skills

Use AIOS to index local skills and installed external skills from other tool ecosystems.

### Capture reusable solved problems

Use the solution layer when a real fix or implementation pattern should be
reused across projects or teams without promoting it into a full skill yet.

### Reuse lessons across projects

Store durable knowledge once and let future sessions benefit from it.

## Good First Steps

If you are new to AIOS, read the docs in this order:

1. [Setup](setup.md)
2. [How To Use](how_to_use.md)
3. [Action Flow](action_flow.md)
4. [Skills](skills.md)
5. [Architecture](architecture.md)

If something does not work, go to [Troubleshooting](troubleshooting.md).
