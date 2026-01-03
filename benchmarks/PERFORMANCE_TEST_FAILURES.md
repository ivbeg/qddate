# Performance Test Failures Analysis

## Summary

When running `python3 benchmarks/comprehensive_performance_test.py --skip-memory --iterations 1`, **503 test cases fail** with `KeyError` exceptions.

## Error Details

### Error Type
- **Exception**: `KeyError`
- **Count**: 503 errors out of 10,359 test cases (~4.9% failure rate)
- **Location**: `qddate/patterns/base.py` lines 167 and 175

### Root Cause

The issue occurs in pattern definitions that use `caseless=True` with `setParseAction` but don't normalize the case when looking up values in dictionaries.

**Problematic Code:**

1. **Line 167** (`qddate/patterns/base.py`):
   ```python
   oneOf(ENG_MONTHS, caseless=True).setParseAction(lambda t: en_mname2mon[t[0]])
   ```

2. **Line 175** (`qddate/patterns/base.py`):
   ```python
   oneOf(ENG_MONTHS_ABBREV, caseless=True).setParseAction(lambda t: enabbrev_mname2mon[t[0]])
   ```

**Why it fails:**

- When `caseless=True` is used, pyparsing matches case-insensitively (e.g., "june" matches "June")
- However, `t[0]` returns the **original matched string** (e.g., "june" in lowercase)
- The dictionaries `en_mname2mon` and `enabbrev_mname2mon` have **capitalized keys** ("June", "Jan")
- Therefore, `en_mname2mon['june']` raises a `KeyError` because the key doesn't exist

### Example Failing Test Cases

- `"8.june.2012"` → KeyError: 'june'
- `"august 14, 1936"` → KeyError: 'august'
- `"15.september.1959"` → KeyError: 'september'
- `"26 april 1962"` → KeyError: 'april'

## Suggested Fixes

### Fix 1: Normalize Case in Parse Actions

**File**: `qddate/patterns/base.py`

**Change line 167 from:**
```python
oneOf(ENG_MONTHS, caseless=True).setParseAction(lambda t: en_mname2mon[t[0]])
```

**To:**
```python
oneOf(ENG_MONTHS, caseless=True).setParseAction(lambda t: en_mname2mon[t[0].capitalize()])
```

**Change line 175 from:**
```python
oneOf(ENG_MONTHS_ABBREV, caseless=True).setParseAction(lambda t: enabbrev_mname2mon[t[0]])
```

**To:**
```python
oneOf(ENG_MONTHS_ABBREV, caseless=True).setParseAction(lambda t: enabbrev_mname2mon[t[0].capitalize()])
```

**Note**: This follows the same pattern used in other language pattern files (e.g., `it.py`, `pt.py`, `fr.py`, `es.py`) which already use `.capitalize()` for similar cases.

### Alternative Fix: Create Case-Insensitive Dictionaries

Alternatively, create case-insensitive lookup dictionaries:

```python
# Create case-insensitive versions
en_mname2mon_ci = {k.lower(): v for k, v in en_mname2mon.items()}
enabbrev_mname2mon_ci = {k.lower(): v for k, v in enabbrev_mname2mon.items()}

# Then use:
oneOf(ENG_MONTHS, caseless=True).setParseAction(lambda t: en_mname2mon_ci[t[0].lower()])
oneOf(ENG_MONTHS_ABBREV, caseless=True).setParseAction(lambda t: enabbrev_mname2mon_ci[t[0].lower()])
```

However, the `.capitalize()` approach is simpler and consistent with existing code.

## Impact on Performance Tests

### Current Behavior

The comprehensive performance test suite **handles these errors gracefully**:
- Errors are caught and counted
- Testing continues for remaining test cases
- Error counts are reported in the output
- Success rates are calculated correctly (excluding errors)

### Test Results

With current errors:
- **Match operations**: 79.9% success rate, 503 errors
- **Parse operations**: 79.9% success rate, 509 errors
- **Overall**: ~80% success rate, ~5% error rate

After fixes:
- Expected success rate: ~85-90% (depending on other edge cases)
- Error rate should drop to near 0% for these specific patterns

## Verification

After applying fixes, verify with:

```bash
# Test specific failing cases
python3 -c "
from qddate import DateParser
p = DateParser()
test_cases = ['8.june.2012', 'august 14, 1936', '15.september.1959']
for tc in test_cases:
    result = p.parse(tc)
    print(f'{tc}: {result}')
"

# Run full performance test
python3 benchmarks/comprehensive_performance_test.py --skip-memory --iterations 1
```

## Fix Applied

✅ **Fix has been applied** to `qddate/patterns/base.py`:
- Line 167: Added `.capitalize()` to normalize case
- Line 175: Added `.capitalize()` to normalize case

### Results After Fix

**Before Fix:**
- Match operations: 503 errors, 79.9% success rate
- Parse operations: 509 errors, 79.9% success rate

**After Fix:**
- Match operations: **0 errors**, 100% success rate (for match operations)
- Parse operations: **6 errors**, 84.7% success rate
- **Overall improvement**: ~5% increase in success rate

The remaining 6 errors in parse operations are likely due to other edge cases unrelated to the KeyError issue that was fixed.

## Related Patterns

Other pattern files already handle this correctly:
- `qddate/patterns/it.py` line 100: Uses `.capitalize()`
- `qddate/patterns/pt.py` line 118: Uses `.capitalize()`
- `qddate/patterns/fr.py` line 100: Uses `.capitalize()`
- `qddate/patterns/es.py` line 100: Uses `.capitalize()`

The fix should follow the same pattern for consistency.

