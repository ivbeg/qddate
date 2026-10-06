# OpenSpec Change: Harden pattern mutation safety

`DateParser.__generate()` currently mutates the base pattern dicts in
`ALL_PATTERNS` when stamping `required_chars`, `no_prefix`, etc. The defensive
shallow copy in `DateParser.__init__` saves end users, but the mutation hazard
is a real footgun for anyone constructing a parser during import. This change
moves the stamping into `annotate_patterns()` (already import-time) so
`__generate()` becomes read-only against `ALL_PATTERNS`.

## Why

`qdparser.py::__generate()` does, on first use:

```python
for pat in patterns:                          # patterns IS ALL_PATTERNS
    pat["required_chars"] = ...               # mutates ALL_PATTERNS[i]
    ...
    yield {**pat, "right": True, "basekey": ...}
```

The `__init__` defensive `self.patterns = [dict(p) for p in patterns]` saves
end users because it copies every entry by then. But:

- Anyone who reads `ALL_PATTERNS` *during* construction sees the mutation.
- Multiple `DateParser()` constructions call `__generate()` again (it's
  idempotent for the data fields but not zero cost).
- If `__generate` is ever moved outside `__init__` (e.g. as a module-level
  call) the hazard becomes real.

`annotate_patterns(ALL_PATTERNS)` already runs at import time and stamps the
same metadata fields on the patterns. The right home for the stamping is
there — `__generate()` then becomes pure.

## What changes

**Move stamping from `__generate` to `annotate_patterns`**
- From: `__generate` mutates each base pattern dict (`pat["required_chars"]`,
  `pat["no_prefix"]`, `pat["format"]`) on first invocation.
- To: `annotate_patterns()` stamps the same fields once at import time;
  `__generate()` reads them and emits a copy.
- Reason: `__generate()` should be read-only against `ALL_PATTERNS`.
- Impact: Non-breaking — the fields stamped are the same.

**Add a snapshot test for immutability**
- New: assert `ALL_PATTERNS` is structurally unchanged across N
  `DateParser()` constructions.
- Reason: Lock in the safety net.
- Impact: Test-only.

## Impact

- **Breaking?** No.
- **Affected:** Anyone who reads `ALL_PATTERNS` directly (the change makes
  their reads more reliable).
- **Risk:** If `annotate_patterns()` and `__generate()` produce different
  field sets for the same pattern, the parser would lose some patterns. The
  existing reachability oracle and bucket-coverage tests will catch this.
- **Rollback:** Self-contained revert.