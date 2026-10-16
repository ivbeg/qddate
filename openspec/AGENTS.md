# OpenSpec Conventions for qddate

This file configures AI agents and contributors working with the OpenSpec spec files
in `openspec/`. Follow these conventions when creating or editing specs or change
proposals.

## Format rules

- **Specs describe WHAT and WHY, not HOW.** Avoid referencing specific function names,
  internal data structures, or implementation files in `specs/<capability>/spec.md`.
  Implementation detail belongs in `design.md`.
- **Requirements use SHALL.** Every `### Requirement:` body is a single normative
  statement using RFC 2119 keywords (SHALL, MUST, SHOULD).
- **Requirement names ≤ 50 chars**, descriptive, unique. They are identifiers.
- **Scenarios use GIVEN/WHEN/THEN.** Every requirement has at least one `#### Scenario:`
  block. `GIVEN` is optional when there is no meaningful precondition.
- **Delta sections only in `changes/`.** A delta `spec.md` uses exactly one of:
  `## ADDED Requirements`, `## MODIFIED Requirements`, `## REMOVED Requirements`,
  `## RENAMED Requirements`. Never paste a full future spec into a delta.
- **`## MODIFIED Requirements`** must reuse the exact current `### Requirement:` header
  text from the canonical spec so it can be matched.

## Proposal format

`proposal.md` uses explicit From/To blocks (no inline diffs):

```markdown
**Behavior or Section Name**
- From: current state
- To: future state
- Reason: why
- Impact: breaking | non-breaking, and who is affected
```

## Files per change

A change in `changes/<change-name>/` contains:

- `proposal.md` — why, what, impact (required)
- `tasks.md` — implementation checklist (required)
- `specs/<capability>/spec.md` — delta only (required if any spec changes)
- `design.md` — HOW / implementation notes (optional)

## Capabilities in this project

| Capability | Spec | Covers |
|---|---|---|
| `date-parsing` | `specs/date-parsing/spec.md` | `parse`, `match`, left-aligned matching, date validation |
| `language-support` | `specs/language-support/spec.md` | `languages=` param, language detection, 12 supported languages |
| `packaging-and-api` | `specs/packaging-and-api/spec.md` | Public API surface, runtime dependencies, packaging |

When proposing a new behavior, file the delta against the matching capability, or
create a new capability folder if none fits.

## Conventions for this repo

- Baseline specs in `specs/` describe **today's** behavior, including known bugs only
  where explicitly noted (a bug is not a spec — it is the target of a MODIFIED delta).
- P0/P1 changes from `IMPROVEMENT_PLAN.md` map 1:1 to change folders under `changes/`.
- Prefer many small, independently archivable changes over one large one.
