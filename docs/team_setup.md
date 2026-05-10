# Team Setup

This document explains how to use AIlit as a shared team or organization layer.

## The Basic Model

Use two layers:

1. one shared AIlit repository
2. many project repositories

The shared AIlit repository should contain:

- runtime code
- standards
- shared skills
- shared solutions
- tracking and governance docs

Each project repository should contain:

- local `ai/` files
- tool instruction files
- project-specific decisions and lessons

## What Should Stay Shared

Keep these in the shared AIlit repo:

- engineering standards
- approved skills
- shared solved-problem writeups
- team-wide AI workflow guidance

## What Should Stay Local To A Project

Keep these inside the project:

- project design notes
- project context
- repo-specific decisions
- repo-specific lessons
- active task backlog

## Recommended Ownership

At minimum, define:

- one owner for the shared AIlit repo
- one reviewer group for standards and shared solutions
- one expectation for when project lessons should be promoted

## Suggested Review Rules

Use simple defaults first:

1. new shared solutions start as `draft`
2. reviewed solutions must include:
   - `review_status: reviewed`
   - `reviewed_by`
   - `last_reviewed`
3. stale solutions should be reviewed or deprecated

## Suggested Workflow

1. an engineer finishes meaningful work in a project
2. they record the local lesson in `ai/lessons.md`
3. if the lesson is reusable, they run `aios promote-lesson`
4. the shared solution is reviewed
5. if it becomes stable enough, it may later inform a skill or standard

## Useful Commands

```bash
aios list-solutions
aios list-solutions --stale only
aios list-solutions --review-status reviewed
aios list-knowledge --project . --show-items
```

## Practical Rule

Do not try to centralize everything.

Shared AIlit should hold reusable knowledge.

Project repos should hold local context.
