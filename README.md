# Personal AI Engineering OS

This folder stores reusable engineering knowledge for AI coding tools such as Codex CLI, Claude Code, Cursor, and Gemini CLI.

The goal is to keep global engineering guidance separate from project-specific context. AI tools should load only the standards, skills, prompts, and agent instructions needed for the current task.

## Structure

- `standards/` contains engineering principles that apply across projects.
- `skills/` contains reusable task-specific knowledge modules.
- `prompts/` contains reusable prompts for common workflows.
- `agents/` contains role definitions for AI assistants.
- `integrations/` contains setup guidance for AI coding tools.
- `plugins/` contains imported provider or community capability bundles.
- `registry/` contains indexes that help tools discover available skills.
- `scripts/` contains maintenance utilities for validation and indexing.
- `updates/` records changes, lessons, and improvements over time.

## Daily Workflow

1. Capture project context in the target repository under `ai/`.
2. Install AI tool integrations so agents know how to use the AI OS.
3. In Codex, Claude Code, Cursor, Gemini CLI, Antigravity, or Windsurf, ask for the task normally.
4. The agent runs the AI OS `prepare` command itself before non-trivial work.
5. Review the output, run tests, and update project decisions.
6. Capture reusable lessons back into `engineering_brain`.

## Global Command

Install the `aios` command into `~/.local/bin`:

```bash
~/engineering_brain/scripts/install_aios_command.sh
```

Then use it from any project:

```bash
aios doctor --project .
aios onboard --project . --tools codex cursor claude gemini antigravity windsurf
aios prepare --task "add retry logic" --project . --tool codex
aios list-skill-sources
aios list-skills --query compound
aios self-test
```

`~/.local/bin` must be on your `PATH`. On this machine it already is.

## Skill Runtime

The skill runtime lets AI agents discover and load reusable engineering guidance automatically.

The registry includes:

- local AI OS skills from `~/engineering_brain/skills/`
- installed external skills from `~/.agents/skills/`
- installed external skills from `~/.codex/skills/`

Runtime commands such as `match`, `load`, and `prepare` refresh the registry first,
so newly installed skills in those roots become visible without a separate import step.
To override the default external roots, set `AIOS_SKILL_SOURCES` using your shell's
path separator.

Flow:

```text
User request
-> scripts/skill_matcher.py
-> registry/skills.json
-> relevant skill names
-> scripts/skill_loader.py
-> combined skill context
```

The preferred command surface is now the `aios` package:

```bash
python3 -m aios match "design retry strategy"
python3 -m aios load retry_strategy
python3 -m aios build --task "add retry logic" --project .
python3 -m aios index
python3 -m aios list-skills
python3 -m aios list-skill-sources
python3 -m aios validate
python3 -m aios init-project --project .
python3 -m aios integrate --project .
python3 -m aios import-skill --source ./some_skill
python3 -m aios import-plugin --source ./plugin_pack
python3 -m aios log-decision --project .
python3 -m aios capture-lesson --project .
python3 -m aios capture-update
python3 -m aios doctor --project .
python3 -m aios inspect-project --project .
python3 -m aios onboard --project .
python3 -m aios prepare --task "add retry logic" --project . --tool codex
python3 -m aios self-test
```

Run those commands from the `engineering_brain` directory. When an agent is working
inside another project, use the cross-project wrapper:

```bash
python3 ~/engineering_brain/scripts/aios.py prepare \
  --task "add retry logic" \
  --project . \
  --tool codex
```

The older task-specific `scripts/*.py` commands are still available as compatibility wrappers.

## AI Tool Integrations

Use integrations to connect project-level agent instructions to tools such as
Codex, Cursor, Claude Code, Gemini CLI, Antigravity, and Windsurf.

From any project:

```bash
python3 ~/engineering_brain/scripts/aios.py integrate --project .
```

This creates:

```text
AGENTS.md
CLAUDE.md
GEMINI.md
.cursor/rules/ai-os.mdc
.windsurf/rules/ai-os.md
```

Existing files are skipped by default. To target specific tools:

```bash
python3 ~/engineering_brain/scripts/aios.py integrate --project . --tool codex
python3 ~/engineering_brain/scripts/aios.py integrate --project . --tool claude cursor
python3 ~/engineering_brain/scripts/aios.py integrate --project . --tool gemini antigravity windsurf
```

The generated files tell agents to run the AI OS context builder themselves before
non-trivial engineering work:

```bash
python3 ~/engineering_brain/scripts/aios.py prepare \
  --task "<current user request>" \
  --project . \
  --tool <current-tool>
```

You should not need to manually run `prepare` during normal chat-driven development.
Manual CLI use is mainly for setup, debugging, inspection, and verification.

See [integrations/README.md](integrations/README.md) for tool-specific notes.

## Daily-Use Commands

Check whether a project is ready for AI-assisted development:

```bash
python3 ~/engineering_brain/scripts/aios.py doctor --project .
```

Detect project stack, commands, and important paths:

```bash
python3 ~/engineering_brain/scripts/aios.py inspect-project --project .
```

Append detected project facts to `ai/context.md`:

```bash
python3 ~/engineering_brain/scripts/aios.py inspect-project --project . --write
```

One-command project onboarding:

```bash
python3 ~/engineering_brain/scripts/aios.py onboard \
  --project . \
  --tools codex cursor claude gemini
```

Prepare a task prompt with readiness warnings:

```bash
python3 ~/engineering_brain/scripts/aios.py prepare \
  --task "add retry logic to producer handler" \
  --project . \
  --tool codex
```

Run the AI OS smoke suite:

```bash
python3 ~/engineering_brain/scripts/aios.py self-test
```

Inspect configured skill roots and indexed installed skills:

```bash
python3 ~/engineering_brain/scripts/aios.py list-skill-sources
python3 ~/engineering_brain/scripts/aios.py list-skills --query marketing
python3 ~/engineering_brain/scripts/aios.py list-skills --query compound
```

### Match Skills

Use the matcher to find skills relevant to a task:

```bash
python3 -m aios match "design retry strategy"
```

Compatibility command:

```bash
python3 scripts/skill_matcher.py "design retry strategy"
```

The matcher reads `registry/skills.json` and scores skills using:

- `name`
- `title`
- `description`
- `tags`
- `aliases`
- `keywords`

It returns ranked JSON results with a score and matched terms.

### Load Skills

Use the loader to combine selected skill content:

```bash
python3 -m aios load retry_strategy error_handling
```

Compatibility command:

```bash
python3 scripts/skill_loader.py retry_strategy error_handling
```

The loader uses each skill's `path` and `entrypoint` from the registry. The default entrypoint is `skill.md`.

### Rebuild The Registry

After adding or changing skills, rebuild the registry:

```bash
python3 -m aios index
```

Compatibility command:

```bash
python3 scripts/index_skills.py
```

Validate an individual skill:

```bash
python3 -m aios validate skills/backend/retry_strategy
```

Validate all skills:

```bash
python3 -m aios validate
```

Compatibility command:

```bash
python3 scripts/validate_skill.py skills/backend/retry_strategy
```

## Context Builder

The context builder assembles a ready-to-send prompt for AI coding tools.

Flow:

```text
User task
-> load standards
-> match skills
-> load skill content
-> load optional project ai/ context
-> output final prompt
```

Run it without project context:

```bash
python3 -m aios build \
  --task "implement retry mechanism"
```

Compatibility command:

```bash
python3 scripts/context_builder.py \
  --task "implement retry mechanism"
```

Run it with project context:

```bash
python3 -m aios build \
  --task "add retry logic to producer handler" \
  --project ~/projects/my_project
```

Format it for a specific AI tool:

```bash
python3 -m aios build \
  --task "add retry logic to producer handler" \
  --project ~/projects/my_project \
  --tool codex
```

Supported tool adapters:

- `universal`
- `codex`
- `cursor`
- `claude`
- `gemini`
- `antigravity`
- `windsurf`

Compatibility command:

```bash
python3 scripts/context_builder.py \
  --task "add retry logic to producer handler" \
  --project ~/projects/my_project
```

If a project path is provided, the builder looks for:

- `ai/spec.md`
- `ai/design.md`
- `ai/context.md`
- `ai/decisions.md`
- `ai/tasks.md`
- `ai/lessons.md`

The output is structured as:

- `SYSTEM CONTEXT`
- `SKILLS`
- `PROJECT CONTEXT`
- `USER TASK`

## Project AI Context

Any software repository can be initialized with project-specific AI context:

```bash
python3 ~/engineering_brain/scripts/aios.py init-project --project .
```

This creates:

```text
ai/
  spec.md
  design.md
  context.md
  decisions.md
  tasks.md
  lessons.md
```

Existing files are skipped by default. To recreate the templates, pass
`--overwrite` deliberately:

```bash
python3 ~/engineering_brain/scripts/aios.py init-project --project . --overwrite
```

Use the files this way:

- `spec.md` explains what the project should do.
- `design.md` explains architecture, boundaries, and data flow.
- `context.md` captures stack, commands, conventions, and important paths.
- `decisions.md` records durable project decisions.
- `tasks.md` tracks AI-assisted engineering work.
- `lessons.md` captures lessons specific to this repository.

Rule of thumb:

- Project-specific facts belong in the project `ai/` folder.
- Reusable engineering lessons belong in `~/engineering_brain/updates/` or a global skill.

## Memory Loop

Use memory commands after meaningful AI-assisted work.

Log a durable project decision:

```bash
python3 ~/engineering_brain/scripts/aios.py log-decision \
  --project . \
  --title "Use bounded retries for producer sends" \
  --context "Producer sends can fail on transient network errors." \
  --decision "Use exponential backoff with jitter and max attempts." \
  --reasoning "This handles transient failure without retrying forever." \
  --consequences "Handlers must remain idempotent."
```

Capture a project-specific lesson:

```bash
python3 ~/engineering_brain/scripts/aios.py capture-lesson \
  --project . \
  --title "Producer handlers must be idempotent" \
  --situation "Retry logic can duplicate sends after partial failure." \
  --lesson "Use idempotency keys around producer writes." \
  --applies-to "Producer handlers"
```

Add a project task:

```bash
python3 ~/engineering_brain/scripts/aios.py add-task \
  --project . \
  --title "Add retry tests for producer handler" \
  --goal "Cover transient failure and final failure paths." \
  --validation "Run focused producer handler tests."
```

Capture a reusable global update:

```bash
python3 ~/engineering_brain/scripts/aios.py capture-update \
  --title "Retry skills should require idempotency checks" \
  --context "A producer retry task exposed duplicate-send risk." \
  --change "Update retry guidance to require idempotency before retries." \
  --reason "This prevents agents from adding unsafe retry loops."
```

Rule:

- Project-specific memory goes into `project/ai/`.
- Reusable memory goes into `~/engineering_brain/updates/` or becomes a global skill.

## Skill Format

Each skill should live in its own folder:

```text
skills/backend/retry_strategy/
  metadata.json
  skill.md
  examples.md
```

Minimum metadata shape:

```json
{
  "name": "retry_strategy",
  "tags": ["backend", "resilience", "retry"],
  "path": "skills/backend/retry_strategy",
  "description": "Best practices for retrying failed operations"
}
```

The full metadata used by this system also supports `title`, `version`, `status`, `entrypoint`, `aliases`, `keywords`, `recommended_standards`, and `compatible_tools`.

## External Skills

External skills from providers, GitHub repositories, or the internet should be imported through the skill importer:

```bash
python3 ~/engineering_brain/scripts/aios.py import-skill \
  --source ./downloaded_skill \
  --provider community \
  --source-url "https://example.com/skill"
```

Imported skills are stored under:

```text
skills/vendor/<provider>/<skill_name>/
```

By default, imported skills use:

```text
trust_level: untrusted
status: untrusted
```

Untrusted and disabled skills are indexed but are not automatically matched or loaded by the context builder.

After reviewing a skill, update its `metadata.json`:

```json
{
  "trust_level": "reviewed",
  "status": "reviewed"
}
```

Then rebuild the registry:

```bash
python3 ~/engineering_brain/scripts/aios.py index
```

Trust levels:

- `local`: written by you.
- `reviewed`: imported and manually reviewed.
- `vendor`: from a provider you trust.
- `untrusted`: imported but not approved for auto-loading.
- `disabled`: should not be loaded.

## Plugins And Providers

Skills are reusable knowledge modules. Plugins are larger capability bundles that may include skills, prompts, integrations, commands, adapters, or hooks.

Plugin shape:

```text
plugin_pack/
  plugin.json
  skills/
  prompts/
  integrations/
  commands/
  adapters/
  hooks/
```

Import a plugin:

```bash
python3 ~/engineering_brain/scripts/aios.py import-plugin \
  --source ./plugin_pack \
  --provider community \
  --source-url "https://example.com/plugin"
```

Imported plugins are stored under:

```text
plugins/vendor/<provider>/<plugin_name>/
```

Plugin and provider registries live at:

```text
registry/plugins.json
registry/providers.json
```

Useful commands:

```bash
python3 ~/engineering_brain/scripts/aios.py index-plugins
python3 ~/engineering_brain/scripts/aios.py list-plugins
python3 ~/engineering_brain/scripts/aios.py list-providers
```

Plugin commands are registry metadata only for now. Do not execute imported plugin commands until the plugin has been reviewed.

After reviewing a plugin:

```bash
python3 ~/engineering_brain/scripts/aios.py trust-plugin example_provider_pack \
  --trust-level reviewed
```

## Design Rules

- Start simple and add structure only when it helps repeated work.
- Keep each skill focused on one job.
- Prefer small, explicit files over large generic instructions.
- Treat the registry as generated data when possible.
- Keep project-specific facts out of global skills.
- Never auto-load unreviewed internet skills.
- Never execute imported plugin commands without review.
