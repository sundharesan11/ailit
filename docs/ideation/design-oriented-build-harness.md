# Design-Oriented Build Harness

Created: 2026-05-29
Status: active

## Focus

Turn the security-audit harness pattern into a generic build harness for
software design and implementation work.

The original insight is useful beyond vulnerability research:

- narrow questions produce better agent output
- independent adversarial review reduces noise
- splitting a reasoning chain across agents improves judgment
- many parallel scoped tasks beat one broad exhaustive prompt

For AIlit, this should become a reusable harness pattern for building software,
not a security-only workflow.

## Problem Frame

AI coding agents often fail in predictable ways during design-heavy builds:

- they treat broad product requests as implementation tasks too early
- they miss constraints because the task surface is too large
- they mix product, UX, architecture, code, and testing questions into one answer
- they validate their own assumptions instead of challenging them
- they produce confident plans without proving user flows, data flow, or edge cases

The harness should make design work more like disciplined research:

1. decompose the build into narrow questions
2. give each question the right context
3. run specialized passes independently
4. challenge the outputs with adversarial reviewers
5. synthesize decisions, open questions, risks, and implementation slices

## Candidate Ideas

### 1. Prompt-only design standard

Create a standard or skill that tells agents to scope narrowly, split reasoning
questions, and self-review before implementing.

Pros:

- very easy to add
- works with the current `aios prepare` flow
- low maintenance
- no new runtime model

Cons:

- still depends on one agent doing too much
- weak enforcement
- no durable coverage tracking
- no structured synthesis or dedupe

This is useful as a baseline, but not enough for the harness goal.

### 2. Design packet mode inside `aios prepare`

Extend `prepare` so a task can be rendered as a set of scoped packets instead of
one prompt. Each packet would focus on one design question, such as user flow,
architecture fit, data model, state handling, accessibility, or tests.

Pros:

- builds on the existing context assembly system
- keeps AIOS as a context runtime rather than a full agent platform
- makes narrow context reusable across Codex, Claude, Cursor, Gemini, and others

Cons:

- `prepare` is currently simple and task-local
- packet planning, execution, and synthesis may make it too large
- harder to track run state cleanly inside a single command

This is a good intermediate step, but the harness probably deserves its own
command surface.

### 3. Dedicated build harness command

Add a separate harness workflow that uses existing context pieces but owns
planning, packet creation, review gates, synthesis, and run artifacts.

Example commands:

```bash
aios design-plan --project . --task "build tenant support dashboard"
aios design-run --project . --plan ai/harness/runs/2026-05-29-support-dashboard/plan.json
aios design-report --project . --run ai/harness/runs/2026-05-29-support-dashboard
```

Pros:

- clear boundary from normal `prepare`
- can support multi-stage reasoning without bloating the existing command
- can write durable design coverage and synthesis artifacts
- can stay generic across product, UX, architecture, and implementation work

Cons:

- more runtime code
- needs a clear artifact model before implementation
- may be overkill for small tasks unless it has a lightweight mode

This is the recommended direction.

### 4. Full autonomous build swarm

Create a harness that plans, runs many agents, edits code, validates the result,
and resolves conflicts automatically.

Pros:

- ambitious end state
- could become a high-leverage automated build system

Cons:

- too much too soon
- high risk of noisy or conflicting changes
- weak fit for AIlit's current local-first context-runtime identity
- needs mature review, sandboxing, and merge semantics

Reject this for the first pass.

## Recommendation

Build a dedicated design-oriented harness, but keep the first version focused on
planning and review artifacts rather than autonomous code edits.

The harness should answer:

```text
What exactly should be built, what could go wrong, what decisions are stable,
what remains uncertain, and how should implementation be sliced?
```

It should not start by writing code. It should produce better context for the
agent or engineer that eventually writes code.

## Core Harness Model

The harness should use five stages.

### Stage 1: Scope Packet Generation

The harness turns a broad build request into narrow packets.

Each packet should contain:

- build goal
- target surface
- question type
- relevant project context
- relevant standards and skills
- known constraints
- explicit out-of-scope items
- expected output schema

Example packet:

```text
Goal: Build a tenant support dashboard.
Question type: User workflow review.
Target surface: support staff triage flow.
Context: ai/spec.md, ai/design.md, existing support routes.
Ask: Identify the primary workflow, missing states, and points where the user
could get stuck.
Out of scope: database schema and visual styling.
Output: findings, required decisions, unresolved questions.
```

### Stage 2: Specialist Passes

Each packet should be handled by a narrow specialist prompt.

Useful generic specialist passes:

- product fit: does the proposed behavior satisfy the actual user goal?
- user flow: can the target user complete the workflow end to end?
- information architecture: are screens, states, and navigation coherent?
- domain model: are entities, relationships, and lifecycle states clear?
- data flow: where does data enter, change, persist, and leave the system?
- API contract: are boundaries, inputs, outputs, and errors explicit?
- implementation slice: what is the smallest useful build increment?
- test strategy: what must be proven before the work is considered done?
- operations: what observability, rollout, and failure handling are needed?
- design quality: does the interface match the product's work context?

The goal is not to run every pass every time. The planner should select the
smallest set that fits the task.

### Stage 3: Adversarial Review Gates

Adversarial reviewers should sit between specialist output and the final queue.

They should not generate new ideas. Their job is to challenge claims already
made by the specialist pass.

Review prompts should ask:

- Is this claim supported by the provided context?
- Is the severity or priority overstated?
- Does the output assume a user, system behavior, or constraint not in evidence?
- Is the proposed implementation slice actually independent?
- Is there a missing edge case that invalidates the conclusion?
- Should this become a decision, an open question, a risk, or be discarded?

This separates generation from validation.

### Stage 4: Synthesis And Dedupe

The harness should merge reviewed outputs into a single build synthesis.

The synthesis should group items into:

- stable decisions
- required user or product questions
- architecture risks
- UX risks
- implementation slices
- test obligations
- discarded or rejected claims

Dedupe should happen after narrow passes have completed. The harness should not
try to avoid overlap too early, because independent overlap is a signal that a
constraint or risk may be important.

### Stage 5: Build-Ready Output

The final artifact should be useful to both humans and coding agents.

Recommended output files:

```text
ai/harness/runs/<run-id>/plan.json
ai/harness/runs/<run-id>/packets.jsonl
ai/harness/runs/<run-id>/specialist-results.jsonl
ai/harness/runs/<run-id>/review-results.jsonl
ai/harness/runs/<run-id>/synthesis.md
ai/harness/coverage.jsonl
```

The human-facing artifact is `synthesis.md`. The machine-facing artifacts allow
future runs to reuse coverage and avoid repeating the same questions.

## Scope Packet Types

The harness should support packet types that apply across generic software
builds.

### Product Packet

Question:

```text
What user problem is being solved, and what behavior is actually required?
```

Good for:

- unclear feature requests
- competing user roles
- hidden business rules
- deciding what not to build

### Flow Packet

Question:

```text
Can the user move through the workflow without missing states or dead ends?
```

Good for:

- dashboards
- onboarding
- support tools
- admin workflows
- multi-step forms

### Interface Packet

Question:

```text
What should the screen structure, density, controls, and feedback states be?
```

Good for design-heavy builds where implementation quality depends on UI shape.

### Domain Packet

Question:

```text
What entities, states, permissions, and lifecycle transitions does this feature require?
```

Good for:

- business logic
- backend models
- workflows with status transitions
- role-based systems

### Boundary Packet

Question:

```text
What are the inputs, outputs, trust boundaries, and integration contracts?
```

Good for:

- APIs
- external services
- file imports
- AI tool calls
- user-generated content

### Implementation Packet

Question:

```text
What is the smallest coherent implementation slice, and what files or modules does it touch?
```

Good for turning design synthesis into buildable work.

### Verification Packet

Question:

```text
What tests, screenshots, assertions, logs, or manual checks prove this works?
```

Good for reducing vague "looks good" validation.

## How The Article Insights Translate

### Narrow scope produces better findings

For generic builds, the harness should replace:

```text
Design and build the dashboard.
```

with:

```text
Review the support dashboard triage flow for missing states. Use ai/spec.md,
existing routes under app/support, and the current role model. Do not discuss
visual styling or database schema.
```

Narrow scope should be treated as a first-class artifact, not just a prompt
writing habit.

### Adversarial review reduces noise

Specialist agents should not be trusted to validate their own output. A separate
reviewer should classify each claim as:

- accept
- accept with weaker wording
- convert to open question
- reject as unsupported
- duplicate of another finding

The reviewer should have no ability to add new findings. That constraint keeps
the review narrow and useful.

### Splitting the chain produces better reasoning

The harness should avoid combined questions like:

```text
Is this a good design and can we implement it?
```

Instead, it should split the chain:

```text
Does the workflow satisfy the user goal?
Are the domain states complete?
Can the system boundaries support it?
What implementation slice is smallest?
What validation proves it works?
```

Each answer feeds the next stage, but each stage remains narrow.

### Parallel narrow tasks beat one exhaustive agent

Coverage should come from many small packets, not one large planning prompt.

For a design-heavy feature, the harness might run:

```text
Product packet: support manager goals
Flow packet: triage and assignment path
Interface packet: table density and empty states
Domain packet: request lifecycle states
Boundary packet: permissions and tenant scope
Verification packet: tests and browser checks
```

The synthesizer then dedupes and prioritizes.

## First Useful Version

The first version should not attempt fully autonomous execution.

It should support:

- one broad task input
- project context loading through existing AIOS files
- packet planning
- specialist prompt generation
- adversarial review prompt generation
- synthesis template output
- durable run artifacts

The first version can require a human or host coding tool to run the generated
prompts. That keeps AIlit aligned with its current role as a local context and
workflow runtime.

## Suggested Command Shape

### `aios design-plan`

Creates packets and a run directory.

```bash
aios design-plan \
  --project . \
  --task "Build a tenant support dashboard" \
  --focus design
```

Output:

```text
ai/harness/runs/2026-05-29-tenant-support-dashboard/plan.json
ai/harness/runs/2026-05-29-tenant-support-dashboard/packets.jsonl
```

### `aios design-prompts`

Renders prompts for each packet and review gate.

```bash
aios design-prompts \
  --project . \
  --run ai/harness/runs/2026-05-29-tenant-support-dashboard \
  --tool codex
```

Output:

```text
ai/harness/runs/<run-id>/prompts/
```

### `aios design-synthesize`

Combines completed packet results into a human-readable synthesis.

```bash
aios design-synthesize \
  --project . \
  --run ai/harness/runs/2026-05-29-tenant-support-dashboard
```

Output:

```text
ai/harness/runs/<run-id>/synthesis.md
```

## Relationship To Existing AIOS Pieces

The harness should reuse existing pieces where possible.

`aios/context_builder.py`:

- continue loading standards, skills, solutions, and project context
- add a packet-aware context builder only if needed

`aios/adapters.py`:

- continue rendering tool-specific prompt formats
- add harness prompt renderers without changing normal `prepare`

`skills/`:

- add reusable specialist skills over time
- examples: product flow review, design implementation review, API contract review

`standards/`:

- add a standard for design-oriented agent work
- keep it brief and cross-tool

`docs/solutions/`:

- store proven harness patterns after real use
- avoid promoting speculative harness ideas into reviewed solutions too early

Project `ai/` folder:

- store harness run artifacts inside the target project
- preserve local project context and run history

## Artifact Schema Sketch

### Packet

```json
{
  "id": "flow-001",
  "type": "flow",
  "title": "Review support request triage flow",
  "goal": "Find missing user states before implementation",
  "target_surface": ["app/support", "ai/design.md"],
  "context_files": ["ai/spec.md", "ai/context.md", "ai/design.md"],
  "in_scope": ["workflow states", "role-specific actions", "empty and error states"],
  "out_of_scope": ["database migration", "visual polish"],
  "expected_output": ["findings", "open_questions", "required_decisions"]
}
```

### Specialist Result

```json
{
  "packet_id": "flow-001",
  "claims": [
    {
      "kind": "missing_state",
      "summary": "Support staff have no explicit path for reassignment failure.",
      "evidence": ["ai/design.md mentions assignment but not failure handling."],
      "recommended_classification": "risk"
    }
  ]
}
```

### Review Result

```json
{
  "packet_id": "flow-001",
  "claim_id": "claim-001",
  "decision": "accept_with_weaker_wording",
  "reason": "The failure path is missing from the design text, but code has not been inspected yet.",
  "final_classification": "open_question"
}
```

## Rejected Directions

### One mega prompt

Rejected because it recreates the exact failure mode the harness is meant to
avoid.

### Security-only audit harness

Rejected as the general model. Security can be one packet family, but the same
architecture should work for design-heavy software builds.

### Automatic code editing in version one

Rejected because the high-value first step is better design context. Editing can
come later after packet quality, review quality, and synthesis quality are proven.

### Heavy database-backed run storage

Rejected for now. JSONL and markdown match the current AIlit style and are easy
to inspect in Git.

## Open Questions

1. Should the first command be named around `design`, `harness`, or `audit`?
2. Should run artifacts live under project `ai/harness/` or shared repo
   `docs/harness/`?
3. Should the first version execute agents, or only generate prompts and collect
   pasted results?
4. Which packet types should ship first: product, flow, interface, domain,
   boundary, implementation, or verification?
5. How strict should adversarial review be before a claim enters the synthesis?

## Recommended First Pass

Start with a prompt-generating design harness:

1. Add a design harness concept doc.
2. Add a packet schema and synthesis schema.
3. Add `aios design-plan` to create packets from a task.
4. Add `aios design-prompts` to render specialist and reviewer prompts.
5. Add `aios design-synthesize` to merge structured results into `synthesis.md`.
6. Use it manually on one real design-heavy feature before adding autonomous
   execution.

This gives AIlit a practical bridge from context preparation to design-aware
software build orchestration without turning it into a full agent platform too
early.
