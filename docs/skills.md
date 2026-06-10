# Skills

This document explains what skills are in AIOS, where they come from, and how to
manage them.

It also explains where skills fit relative to the new shared solution layer.

## What A Skill Is

A skill is a reusable piece of guidance that helps an AI agent do a task better.

Examples:

- retry strategy
- debugging strategy
- test-driven development
- marketing ideas
- compound engineering workflows

A skill is not usually code.
It is usually task knowledge written in markdown, plus metadata that helps AIOS discover it.

## Skill Vs Solution

Skills and solutions are related, but they are not the same thing.

### Skill

A skill explains how to approach a class of work.

Examples:

- retry strategy
- debugging strategy
- test-driven development

### Solution

A solution explains how a real problem was solved and when that solution should
be reused.

Examples:

- fixing duplicate processing in a worker pipeline
- handling token refresh races in a frontend session flow

Use a skill when you want general reusable guidance.

Use a solution when you want a practical solved-problem reference.

Shared solutions live under:

```text
docs/solutions/
```

## Where Skills Come From

AIOS can work with three types of skills.

### 1. Local AIOS skills

These live inside this repository:

```text
~/engineering_brain/skills/
```

These are the native AIOS skills.

### 2. Installed external skills

These are discovered automatically from:

```text
~/.agents/skills/
~/.codex/skills/
```

This is how AIOS can see skills installed by other local tool systems.

### 3. Imported vendor skills

These are copied into AIOS on purpose with commands like:

```bash
aios import-skill --source ./some_skill
```

These usually go under:

```text
skills/vendor/
```

## How AIOS Finds Skills

AIOS builds a registry file:

```text
registry/skills.json
```

That registry is built from the current local and external skill sources.

In normal use, commands such as:

- `aios match`
- `aios load`
- `aios prepare`
- `aios index`

refresh the registry first.

That means newly installed skills usually become visible automatically.

## How To See Which Skill Sources Are Active

Run:

```bash
aios list-skill-sources
```

This shows:

- the local AIOS skill folder
- the installed external skill roots
- whether each source exists
- how many skills were found

## How To Check If A Skill Is Available

Run:

```bash
aios list-skills --query retry
aios list-skills --query marketing
aios list-skills --query compound
```

If you want to test loading one directly:

```bash
aios load retry_strategy
aios load marketing_ideas
aios load ce_compound
```

## How Matching Works

When you run:

```bash
aios match "design retry strategy"
```

AIOS looks at the skill registry and scores skills using fields such as:

- name
- title
- description
- tags
- aliases
- keywords

The best matches are returned first.

## How To Add A New Local Skill

Create a folder under `skills/`.

Example:

```text
skills/backend/new_skill/
  metadata.json
  skill.md
```

### Example `metadata.json`

```json
{
  "name": "new_skill",
  "title": "New Skill",
  "description": "What this skill helps with.",
  "path": "skills/backend/new_skill",
  "tags": ["backend", "example"],
  "version": "0.1.0",
  "status": "active",
  "entrypoint": "skill.md"
}
```

### Example `skill.md`

```md
# Skill: New Skill

Explain when to use this skill, the main guidance, and common pitfalls.
```

Then rebuild or refresh the registry:

```bash
aios index
aios validate
aios list-skills --query new_skill
```

## How To Import A Skill Directory

If you have a skill folder from somewhere else, import it with:

```bash
aios import-skill --source ./some_skill --provider community
```

By default, imported skills are safer when treated cautiously.

You can then adjust trust using:

```bash
aios trust-skill some_skill --trust-level reviewed
```

## Trust Levels

AIOS supports several trust labels.

### `local`

Used for native local AIOS skills.

### `reviewed`

Used when a skill has been reviewed and is safe to load.

### `vendor`

Used for trusted vendor-provided skills.

### `untrusted`

Used for skills that should be indexed but not auto-loaded yet.

### `disabled`

Used for skills that should not be used.

## Overriding External Skill Roots

If you want AIOS to read different installed skill roots, set:

```bash
AIOS_SKILL_SOURCES="/some/path:/another/path"
```

Use your shell's path separator between entries.

## Enriching External Skills With The Overlay

Installed external skills often ship with weak metadata, which makes them hard
to match. The overlay file lets you add matching terms without editing any
files under `~/.agents` or `~/.codex`:

```text
skills/external_overlay.json
```

The format is one object per skill, keyed by the slugified skill name shown in
`aios list-skills`:

```json
{
  "skills": {
    "ui_ux_design": {
      "tags": ["website", "portfolio", "landing"],
      "keywords": ["tailwind", "react"],
      "aliases": ["web-design"]
    }
  }
}
```

Rules:

- an optional top-level `description` string can document the file itself
- `tags`, `keywords`, and `aliases` must be lists of strings; all are optional
- values are unioned into the registry entry at index time and tokenized for
  matching, so multiword terms like "core web vitals" become single tokens
- a missing overlay file is fine; an invalid one is ignored with a warning and
  never breaks a command
- aliases are used for matching only; `aios load` still expects the canonical
  skill name
- keys that match no installed skill are reported by `aios doctor` and
  `aios list-skill-sources`, so stale entries stay visible

For testing, `AIOS_SKILL_OVERLAY` points AIOS at an alternative overlay file.

## Good Skill Hygiene

Keep skills simple.

A good skill should clearly explain:

- when to use it
- what problem it solves
- what to do
- what to avoid

Try not to make skills too vague or too broad.

If something is too tied to one real incident, one stack edge case, or one
specific solved problem, it may belong in `docs/solutions/` instead of
`skills/`.

## If A Skill Does Not Show Up

Check these in order:

1. `aios list-skill-sources`
2. `aios list-skills --query <name>`
3. `aios index`
4. `aios validate`

If it is an installed external skill, make sure:

- the source root exists
- the skill has a `SKILL.md`
- the path is inside one of the configured external roots

If it is a local AIOS skill, make sure:

- the folder has `metadata.json`
- the folder has `skill.md`
- metadata fields are valid

For common issues, see [Troubleshooting](troubleshooting.md).
