# AIlit Solution Artifact Options

Created: 2026-05-11
Status: active

## Focus

Choose the first-pass shape for reusable shared solutions in AIlit.

## Grounding

The current repository already has:

- strong markdown-first docs
- simple local registries
- a junior-friendly documentation style
- a need for low-ceremony real project use

That means the solution artifact model should optimize for readability and low
maintenance before optimizing for heavy automation.

## Candidate Ideas

### 1. Single markdown file with YAML frontmatter

Each solution is one markdown file with:

- frontmatter metadata
- a consistent body template

Example:

```text
docs/solutions/backend/retry-worker-failures.md
```

Pros:

- easiest to read in GitHub
- easiest to write by hand
- low ceremony
- simple to index later

Cons:

- weaker structure for attached evidence
- easier for body sections to drift

### 2. Directory per solution with `metadata.json` and `solution.md`

Each solution gets a folder:

```text
docs/solutions/backend/retry-worker-failures/
  metadata.json
  solution.md
  assets/
```

Pros:

- rigid structure
- easier to attach evidence later
- clean machine-readable metadata

Cons:

- more ceremony
- more files to manage
- worse GitHub scanning experience

### 3. Single markdown file plus optional sidecar evidence

Each solution is a markdown file, with optional evidence files nearby only when
needed.

Example:

```text
docs/solutions/backend/retry-worker-failures.md
docs/solutions/backend/retry-worker-failures.assets/
```

Pros:

- keeps the common case simple
- leaves room for richer cases later
- still easy to index

Cons:

- slightly more rules to explain
- sidecar conventions need documentation

## Recommendation

Choose **Option 3** for the first pass.

Reason:

- it keeps the normal case as a single readable markdown file
- it avoids premature directory complexity
- it still leaves a path for richer evidence later

## Rejected Ideas

### Full database-style structured storage

Rejected for now because it adds too much complexity before the capture and
promotion flow is proven useful.

### Forcing solutions into `skills/`

Rejected because skills and solutions serve different purposes.

- skills explain how to approach a class of work
- solutions record how a real problem was solved and when to reuse it

## Decision

The first pass should use:

- one markdown file per solution
- YAML frontmatter metadata
- a consistent body template
- optional sidecar evidence only when needed later
