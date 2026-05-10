# Tracking

This folder stores working project trackers for AIlit maintenance and delivery.

## Current tracker

- `ailit_master_tracker.xlsx`

## What it contains

The current workbook has four sheets:

1. `Summary`
   - high-level status and phase focus
2. `Backlog`
   - the working queue of build items
3. `Knowledge Model`
   - the artifact types AIlit should support
4. `Open Questions`
   - decisions that still need resolution

## Source documents

The current tracker is based on:

- `docs/brainstorms/ailit-compounding-knowledge-requirements.md`
- `docs/plans/ailit-compounding-knowledge-plan.md`

## How to use it

1. update the `Status` column as work moves
2. assign real owners when work is split across worktrees
3. add links to final implementation files in `Target Artifact`
4. move new product or architecture questions into `Open Questions`

## Rebuild

To rebuild the workbook from the current script:

```bash
python3 scripts/build_master_tracker.py
```
