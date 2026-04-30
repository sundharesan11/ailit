# Skills

This document explains what skills are in AIOS, where they come from, and how to manage them.

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

## Good Skill Hygiene

Keep skills simple.

A good skill should clearly explain:

- when to use it
- what problem it solves
- what to do
- what to avoid

Try not to make skills too vague or too broad.

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
