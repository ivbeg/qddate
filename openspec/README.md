# OpenSpec index for qddate

This directory is the [OpenSpec](https://github.com/Fission-AI/OpenSpec)-formatted
specification layer for qddate. It was generated from the code review in
[`../IMPROVEMENT_PLAN.md`](../IMPROVEMENT_PLAN.md).

## Layout

```
openspec/
├── project.md                 # What qddate is, in/out of scope, principles
├── AGENTS.md                  # Conventions for editing these specs (read me first)
├── specs/                     # Canonical specs — TODAY's behavior
│   ├── date-parsing/
│   ├── language-support/
│   └── packaging-and-api/
└── changes/                   # Proposed changes (delta specs)
    ├── fix-correctness-regressions/
    ├── cleanup-project-hygiene/
    ├── refactor-pattern-metadata/
    ├── add-datetime-semantics/
    ├── modernize-api-surface/
    └── add-advanced-parsing/
```

## How to read this

- **`specs/`** describes the *current, shipped* behavior. It is the contract that
  refactors must preserve. Baseline: **18 requirements, 28 scenarios** across 3
  capabilities.
- **`changes/<name>/proposal.md`** states *why* a change is needed and its impact,
  using explicit From/To blocks.
- **`changes/<name>/specs/<capability>/spec.md`** is a *delta* — only the
  `## ADDED Requirements` / `## MODIFIED Requirements` it introduces or changes.
- **`changes/<name>/tasks.md`** is the implementation checklist.

## Changes → roadmap mapping

Each change maps to one or more sections of `IMPROVEMENT_PLAN.md` and is sized to be
independently archivable.

| Change | Priority | Plan § | Breaking? | Capability touched |
|---|---|---|---|---|
| `fix-correctness-regressions` | **P0** | 3.1–3.4 | No | language-support |
| `cleanup-project-hygiene` | **P1** | 4.3, 4.5–4.10 | No | packaging-and-api |
| `refactor-pattern-metadata` | P1 | 4.1, 4.2, 6.1, 6.2 | No (internal) | — (no delta) |
| `add-datetime-semantics` | P2 | 3.4, 7.1, 7.2 | No (opt-in) | date-parsing |
| `modernize-api-surface` | P2 | 4.8, 7.4, 7.5 | No (additive) | date-parsing |
| `add-advanced-parsing` | P3 | 6.3, 7.3, 7.6, 7.7, 8 | No (additive) | date-parsing |

## Suggested milestone sequencing

1. **v1.0.11 — Stabilize:** `fix-correctness-regressions` + `cleanup-project-hygiene`.
   Green tests, lean deps, honest docs. No API change.
2. **v1.1.0 — Refactor:** `refactor-pattern-metadata`. Internal cleanup that
   unblocks everything after it; no external change.
3. **v1.2.0 — Capabilities:** `add-datetime-semantics` + `modernize-api-surface`.
   Timezone, pivot year, typed results, bulk API — all opt-in/additive.
4. **v2.0.0 — Scale & coverage:** `add-advanced-parsing` (relative dates,
   ambiguity, compiled matcher); flip the 2-digit-year default.

## Notes

- `refactor-pattern-metadata` is behavior-preserving, so it ships **no delta spec** —
  only a `proposal.md`, `tasks.md`, and a `design.md` (the *how*).
- `add-advanced-parsing` is a thematic roadmap; at implementation time it should be
  split into one change folder per sub-feature so each can be archived independently,
  per OpenSpec conventions.
- Two baseline requirements explicitly flag shipped-but-broken behavior (language
  auto-detection; the `dateparser` runtime dep) and point at the change that fixes
  them. A known bug is not a spec — it is the target of a MODIFIED delta.
