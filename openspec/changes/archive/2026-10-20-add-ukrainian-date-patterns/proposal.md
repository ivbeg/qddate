# Add Ukrainian date patterns

**Supported languages**
- From: qddate supports thirteen language codes and has no Ukrainian month-name patterns.
- To: qddate SHALL support Ukrainian (`uk`) as a first-class language with nominative, genitive, lowercase, and abbreviated month forms.
- Reason: Ukrainian news dates such as `21 травня 2026` are currently missed or narrowed to unrelated Cyrillic languages.
- Impact: non-breaking; expands parsing and language filtering.

**Language detection and metadata**
- From: automatic detection recognizes Russian/Bulgarian Cyrillic dates but not Ukrainian month names.
- To: Ukrainian month names SHALL identify `uk`, and all Ukrainian patterns SHALL carry `uk` metadata and participate in filtering.
- Reason: ensure unrestricted parsing selects the correct patterns and `languages="uk"` is deterministic.
- Impact: non-breaking; existing Russian/Bulgarian inputs remain supported.

**Documentation and verification**
- From: supported-language documentation and tests cover thirteen languages.
- To: documentation, OpenSpec language requirements, fixtures, and tests SHALL cover Ukrainian and the expanded fourteen-language registry.
- Reason: keep the public contract synchronized with the implementation.
- Impact: non-breaking.
