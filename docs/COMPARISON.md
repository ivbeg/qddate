# Repository Comparison: `dateparser` vs `qddate` vs `dateutil`

## Overview

This report provides a comparative analysis of three Python date parsing libraries: `dateparser` (ScriptingHub), `qddate` (Ivan Begtin), and `dateutil` (Gustavo Niemeyer et al.). The analysis covers architectural approaches, feature sets, and intended use cases.

| Feature | `dateutil` | `dateparser` | `qddate` |
| :--- | :--- | :--- | :--- |
| **Primary Goal** | **Standard Extension**: Powerful extensions to the standard `datetime` module. | **Universal Coverage**: Parse almost any human-readable date in any language. | **High Performance**: Parse dates from massive datasets (web scraping) as fast as possible. |
| **Philosophy** | "Generic & Robust" | "It just works" (Magic / Heuristics) | "Fast and Good Enough" (Pragmatic / Patterns) |
| **Approach** | Tokenization + Heuristics (Rule-based) | Wrapper + Heuristics (Locale-based) | Pattern Matching + Pre-filtering |
| **Language Support** | Limited (English + customizable `parserinfo`). | Extensive (~200+ locales via data files). | Limited (~13 languages focused on scraping). |
| **Dependencies** | Minimal (`six`). | Heavy (`regex`, `tzlocal`, `dateutil`, `pytz`). | Light (`pyparsing` + stdlib). |

---

## 1. Architectural Approach

### `dateutil`: The "Smart" Tokenizer
**Mechanism:**
1.  **Lexical Analysis (`_timelex`)**: Splits the string into tokens (words, numbers, separators) based on character types.
2.  **Heuristic Evaluation**: Iterates through tokens and assigns them to date components (`_ymd` struct) based on context and `parserinfo`.
3.  **Conflict Resolution**: Uses logic (like `yearfirst`, `dayfirst` parameters) to resolve ambiguities (e.g., 10/11/12).
4.  **Backend**: Solves for missing components using a `default` datetime.

**Pros:**
*   **Standard Implementation**: The logic is battle-tested and predictable for standard formats.
*   **Extensible**: `parserinfo` class allows customizing month names, day names, etc.
*   **No "Magic" Database**: Does not rely on a massive database of regexes, making it lighter.

**Cons:**
*   **English-Centric**: Default logic assumes English month names/structure unless heavily customized.
*   **Generic**: Struggles with very noisy text or complex natural language ("3 days after next Friday").

### `dateparser`: The "Universal" Interpreter
**Mechanism:**
1.  **Layered Approach**: Built *on top* of `dateutil`. It essentially prepares the ground for `dateutil` or standard parsers.
2.  **Locale Detection**: Aggressively detects language/locale first.
3.  **Preprocessing**: Translates foreign terms (months, relative words) into a common format or uses specific locale-aware patterns.
4.  **Relative Parsing**: Has specific logic for "2 weeks ago", "in 1 year".

**Pros:**
*   **Maximum Coverage**: Handles almost anything you throw at it: "12th of January", "2020.01.12", "il y a 2 jours" (French).
*   **Zero-Config**: You don't need to tell it the language; it figures it out.

**Cons:**
*   **Performance**: The slowest of the three. It does a lot of work (regex, language detection, translation) before even parsing.
*   **Complexity**: Debugging can be hard due to the many layers of abstraction.

### `qddate`: The "Speed" Pattern Matcher
**Mechanism:**
1.  **Pre-computation**: Generates a massive list of `pyparsing` patterns for supported formats.
2.  **Aggressive Filtering**: Uses metadata (length, charsets, separators) to filter 1000+ patterns down to <10 matching candidates in O(1) time.
3.  **Try-Match**: Explicitly tries the filtered patterns in order.

**Pros:**
*   **Speed**: Faster than `dateparser` and likely competitive with `dateutil` for known patterns (due to avoiding heuristic guessing games).
*   **Dirty Data**: Handles "12/01/2020 some text" explicitly.
*   **Determinism**: If a pattern is in the list, it works.

**Cons:**
*   **Rigid**: If the format isn't in the list, it fails.
*   **Evaluation**: Adding languages is manual work.

---

## 2. Feature Deep Dive

### Parsing Capabilities
*   **`dateutil`**: Excellent for ISO 8601, RFC strings, and standard "10 Oct 2020" formats. It also includes `rrule` (recurrence) and `relativedelta` (powerful date math), which the others lack.
*   **`dateparser`**: The king of "Natural Language". Can interpret "tomorrow", "yesterday", "next Friday".
*   **`qddate`**: Purely absolute date extraction. No relative dates.

### Performance & Overhead
1.  **`qddate`**: Fastest for bulk processing of "messy" but pattern-conforming data (e.g., scraping news sites).
2.  **`dateutil`**: Fast for standard strings. Generally faster than `dateparser` because it skips the locale detection/translation layer.
3.  **`dateparser`**: Slowest due to overhead. Not recommended for tight loops processing millions of records unless strict language detection is needed.

### Maintainability
*   **`dateutil`**: Extremely stable, widely used, mature.
*   **`dateparser`**: Mature, data-driven.
*   **`qddate`**: Specialized, requires code changes for new patterns.

---

## 3. Comparison Summary table

| Feature | `dateutil` | `dateparser` | `qddate` |
| :--- | :--- | :--- | :--- |
| **Parsing method** | Lexer + Heuristics | Translation + Heuristics | Pattern Matching |
| **Relative Dates** | No (but supports math via `relativedelta`) | **Yes** (Native logic) | No |
| **Language Detection** | No (Assumes or Explicit) | **Yes** (Automatic) | Limited (Implied by pattern) |
| **Dependencies** | Light | Heavy | Light |
| **Best For...** | General apps, Calendar apps, Standard formats | User Input, Chatbots, "Lazy" parsing | **Web Scraping**, Mass Data Processing |

## 4. Recommendation

*   Use **`dateutil`** if you are building a standard application and dealing with mostly computer-generated or standard English dates. Definitely use it if you need recurrence rules (`rrule`) or complex delta calculations (`relativedelta`).
*   Use **`dateparser`** if you are dealing with user input in a chatbot, search bar, or international application where you have zero control over the input format or language.
*   Use **`qddate`** if you are explicitly scraping web pages (news, blogs) at scale and need to extract dates from typical HTML bylines (e.g., "12 Oct, 2020 | by Author") with maximum speed and minimal false positives.
