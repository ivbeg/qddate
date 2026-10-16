#!/usr/bin/env python
"""Generate the README pattern-counts block from the canonical pattern table.

Idempotent: running the script twice on a clean README produces no diff
beyond the delimited block itself.

The script reads `qddate.patterns.ALL_PATTERNS` and
`qddate.patterns.SUPPORTED_LANGUAGES`, builds a small markdown fragment, and
prints it. To update the README in place, run with `--write`.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Ensure the repo root is on sys.path so `import qddate` works regardless of
# the working directory from which the script is invoked.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import qddate  # noqa: E402
from qddate.patterns import ALL_PATTERNS, SUPPORTED_LANGUAGES  # noqa: E402

BEGIN = "<!-- BEGIN qddate-stats -->"
END = "<!-- END qddate-stats -->"


def build_fragment() -> str:
    """Compute the markdown stats block from the canonical pattern table."""
    base_count = len(ALL_PATTERNS)
    # A fresh DateParser() generates the time/trailing-text variants — that's
    # the count the README reports.
    parser = qddate.DateParser()
    generated = len(parser.patterns)
    lang_count = len(SUPPORTED_LANGUAGES)

    fragment = (
        f"{BEGIN}\n"
        f"- {generated:,} generated date patterns (from {base_count} base patterns)\n"
        f"- {lang_count} supported languages\n"
        f"{END}"
    )
    return fragment


def update_readme(readme_path: Path, fragment: str) -> bool:
    """Replace the delimited block in `readme_path` with `fragment`.

    Returns True if the file was modified.
    """
    text = readme_path.read_text()
    pattern = re.compile(
        re.escape(BEGIN) + r".*?" + re.escape(END),
        re.DOTALL,
    )
    if pattern.search(text):
        new_text = pattern.sub(fragment, text)
    else:
        # No block yet; append at end (or could be inserted at a marker).
        new_text = text.rstrip() + "\n\n" + fragment + "\n"
    if new_text != text:
        readme_path.write_text(new_text)
        return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--readme",
        type=Path,
        default=ROOT / "README.md",
        help="Path to the README to update (default: ./README.md)",
    )
    ap.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if the README needs an update",
    )
    args = ap.parse_args()

    fragment = build_fragment()
    if args.check:
        text = args.readme.read_text()
        needs_update = BEGIN not in text or END not in text
        if not needs_update:
            # Compare to current contents
            current = re.search(
                re.escape(BEGIN) + r".*?" + re.escape(END),
                text,
                re.DOTALL,
            )
            needs_update = current.group(0) != fragment
        return 1 if needs_update else 0

    if update_readme(args.readme, fragment):
        print(f"Updated {args.readme}")
    else:
        print(f"{args.readme} is up to date.")
    # Always print the fragment so CI can `git diff` if it leaks.
    print(fragment)
    return 0


if __name__ == "__main__":
    sys.exit(main())
