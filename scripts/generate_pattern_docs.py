#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to generate comprehensive pattern documentation for qddate.

This script extracts pattern information from all pattern modules and
generates markdown documentation with detailed tables organized by language.
"""

import sys
import os
import re

# Add parent directory to path to import qddate
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from qddate.patterns import (
    PATTERNS_EN,
    INTEGER_LIKE_PATTERNS,
    PATTERNS_BG,
    PATTERNS_CZ,
    PATTERNS_DE,
    PATTERNS_ES,
    PATTERNS_FR,
    PATTERNS_IT,
    PATTERNS_PL,
    PATTERNS_PT,
    PATTERNS_RU,
    PATTERNS_TR,
)

# Import month and weekday names for example generation
from qddate.patterns import base
from qddate.patterns import ru, de, fr, es, it, pt, bg, cz, pl, tr

# Language mapping
LANGUAGE_NAMES = {
    'en': 'English',
    'ru': 'Russian',
    'de': 'German',
    'fr': 'French',
    'es': 'Spanish',
    'it': 'Italian',
    'pt': 'Portuguese',
    'bg': 'Bulgarian',
    'cz': 'Czech',
    'pl': 'Polish',
    'tr': 'Turkish',
}

# Pattern collections by language
PATTERN_COLLECTIONS = {
    'en': PATTERNS_EN + INTEGER_LIKE_PATTERNS,
    'bg': PATTERNS_BG,
    'cz': PATTERNS_CZ,
    'de': PATTERNS_DE,
    'es': PATTERNS_ES,
    'fr': PATTERNS_FR,
    'it': PATTERNS_IT,
    'pl': PATTERNS_PL,
    'pt': PATTERNS_PT,
    'ru': PATTERNS_RU,
    'tr': PATTERNS_TR,
}


# Language-specific month and weekday data for examples
LANG_MONTHS = {
    'en': {'full': base.ENG_MONTHS, 'lc': base.ENG_MONTHS_LC, 'short': base.ENG_MONTHS_SHORT, 'abbrev': base.ENG_MONTHS_ABBREV},
    'ru': {'full': ru.RUS_MONTHS, 'lc': ru.RUS_MONTHS_LC, 'orig': ru.RUS_MONTHS_ORIG},
    'de': {'full': de.DE_MONTHS, 'lc': de.DE_MONTHS_LC, 'short': de.DE_MONTHS_SHORT, 'short_lc': de.DE_MONTHS_SHORT_LC},
    'fr': {'full': fr.FR_MONTHS, 'lc': fr.FR_MONTHS_LC},
    'es': {'full': es.ES_MONTHS, 'lc': es.ES_MONTHS_LC},
    'it': {'full': it.IT_MONTHS, 'lc': it.IT_MONTHS_LC},
    'pt': {'full': pt.PT_MONTHS, 'lc': pt.PT_MONTHS_LC},
    'bg': {'full': bg.BG_MONTHS, 'lc': bg.BG_MONTHS_LC},
    'cz': {'full': cz.CZ_MONTHS, 'lc': cz.CZ_MONTHS_LC, 'gen': cz.CZ_MONTHS_GEN, 'gen_lc': cz.CZ_MONTHS_GEN_LC},
    'pl': {'full': pl.PL_MONTHS, 'lc': pl.PL_MONTHS_LC, 'gen': pl.PL_MONTHS_GEN, 'gen_lc': pl.PL_MONTHS_GEN_LC},
    'tr': {'full': tr.TR_MONTHS, 'lc': tr.TR_MONTHS_LC},
}

LANG_WEEKDAYS = {
    'en': {'full': base.ENG_WEEKDAYS, 'short': base.ENG_WEEKDAYS_SHORT},
    'ru': {'full': ru.RUS_WEEKDAYS, 'lc': ru.RUS_WEEKDAYS_LC},
    'de': {'full': de.DE_WEEKDAYS, 'lc': de.DE_WEEKDAYS_LC},
    'it': {'full': it.IT_WEEKDAYS, 'lc': it.IT_WEEKDAYS_LC},
    'cz': {'full': cz.CZ_WEEKDAYS, 'lc': cz.CZ_WEEKDAYS_LC},
}


def generate_examples(pattern, lang_code):
    """Generate 2-3 example date strings for a pattern."""
    key = pattern.get('key', '')
    name = pattern.get('name', '').lower()
    fmt = pattern.get('format', '')
    yearshort = pattern.get('yearshort', False)
    noyear = pattern.get('noyear', False)
    
    examples = []
    
    # Sample dates to use
    day1, day2, day3 = '15', '3', '28'
    month_num1, month_num2, month_num3 = '03', '12', '07'
    year_full1, year_full2, year_full3 = '2024', '2023', '2025'
    year_short1, year_short2, year_short3 = '24', '23', '25'
    
    # Determine month names to use based on pattern
    months_to_use = None
    weekdays_to_use = None
    
    if lang_code in LANG_MONTHS:
        lang_months = LANG_MONTHS[lang_code]
        if 'short' in name or 'abbrev' in name:
            months_to_use = lang_months.get('short') or lang_months.get('abbrev') or lang_months.get('full')
        elif 'lc' in name or 'lowcase' in name or 'lowercase' in name:
            months_to_use = lang_months.get('lc') or lang_months.get('full')
        elif 'gen' in name and 'gen' in lang_months:
            months_to_use = lang_months.get('gen') or lang_months.get('full')
        elif 'orig' in name and 'orig' in lang_months:
            months_to_use = lang_months.get('orig') or lang_months.get('full')
        else:
            months_to_use = lang_months.get('full') or lang_months.get('lc')
    
    if lang_code in LANG_WEEKDAYS:
        lang_wdays = LANG_WEEKDAYS[lang_code]
        if 'short' in name:
            weekdays_to_use = lang_wdays.get('short') or lang_wdays.get('full')
        elif 'lc' in name or 'lowcase' in name:
            weekdays_to_use = lang_wdays.get('lc') or lang_wdays.get('full')
        else:
            weekdays_to_use = lang_wdays.get('full')
    
    # Generate examples based on format and pattern characteristics
    if noyear:
        # Patterns without year
        if fmt == '%d.%m':
            examples = ['15.03', '3.12', '28.07']
    elif '%d%m%Y' in fmt or fmt == '%d%m%Y':
        # Compact numeric format
        examples = ['15032024', '03122023', '28072025']
    elif '%Y%m%d' in fmt or fmt == '%Y%m%d':
        # ISO compact format
        examples = ['20240315', '20231203', '20250728']
    elif '%d/%m/%Y' in fmt or fmt == '%d/%m/%Y':
        examples = ['15/03/2024', '3/12/2023', '28/7/2025']
    elif '%d/%m/%y' in fmt or fmt == '%d/%m/%y':
        examples = ['15/03/24', '3/12/23', '28/7/25']
    elif '%d.%m.%Y' in fmt or fmt == '%d.%m.%Y':
        examples = ['15.03.2024', '3.12.2023', '28.07.2025']
    elif '%d.%m.%y' in fmt or fmt == '%d.%m.%y':
        examples = ['15.03.24', '3.12.23', '28.07.25']
    elif '%d-%m-%Y' in fmt or fmt == '%d-%m-%Y':
        examples = ['15-03-2024', '3-12-2023', '28-07-2025']
    elif '%d-%m-%y' in fmt or fmt == '%d-%m-%y' or (yearshort and '%d-%m-%Y' in fmt):
        examples = ['15-03-24', '3-12-23', '28-07-25']
    elif '%Y/%m/%d' in fmt or fmt == '%Y/%m/%d':
        examples = ['2024/03/15', '2023/12/3', '2025/7/28']
    elif '%Y-%m-%d' in fmt or fmt == '%Y-%m-%d':
        examples = ['2024-03-15', '2023-12-03', '2025-07-28']
    elif '%Y.%m.%d' in fmt or fmt == '%Y.%m.%d':
        examples = ['2024.03.15', '2023.12.3', '2025.7.28']
    elif '%m/%d/%Y' in fmt or fmt == '%m/%d/%Y':
        examples = ['03/15/2024', '12/3/2023', '7/28/2025']
    elif '%m/%d/%y' in fmt or fmt == '%m/%d/%y':
        examples = ['03/15/24', '12/3/23', '7/28/25']
    elif '%d-%b-%y' in fmt or fmt == '%d-%b-%y':
        if months_to_use:
            month1 = months_to_use[2][:3] if len(months_to_use) > 2 else months_to_use[0][:3]
            month2 = months_to_use[11][:3] if len(months_to_use) > 11 else months_to_use[1][:3]
            month3 = months_to_use[6][:3] if len(months_to_use) > 6 else months_to_use[2][:3]
            examples = [f'{day1}-{month1}-{year_short1}', f'{day2}-{month2}-{year_short2}', f'{day3}-{month3}-{year_short3}']
    elif '%d.%b.%Y' in fmt or fmt == '%d.%b.%Y':
        if months_to_use:
            month1 = months_to_use[2] if len(months_to_use) > 2 else months_to_use[0]
            month2 = months_to_use[11] if len(months_to_use) > 11 else months_to_use[1]
            month3 = months_to_use[6] if len(months_to_use) > 6 else months_to_use[2]
            examples = [f'{day1}.{month1}.{year_full1}', f'{day2}.{month2}.{year_full2}', f'{day3}.{month3}.{year_full3}']
    elif '%b %d, %Y' in fmt or fmt == '%b %d, %Y':
        if months_to_use:
            month1 = months_to_use[2] if len(months_to_use) > 2 else months_to_use[0]
            month2 = months_to_use[11] if len(months_to_use) > 11 else months_to_use[1]
            month3 = months_to_use[6] if len(months_to_use) > 6 else months_to_use[2]
            examples = [f'{month1} {day1}, {year_full1}', f'{month2} {day2}, {year_full2}', f'{month3} {day3}, {year_full3}']
    elif '%d %b %Y' in fmt or fmt == '%d %b %Y':
        if months_to_use:
            month1 = months_to_use[2] if len(months_to_use) > 2 else months_to_use[0]
            month2 = months_to_use[11] if len(months_to_use) > 11 else months_to_use[1]
            month3 = months_to_use[6] if len(months_to_use) > 6 else months_to_use[2]
            examples = [f'{day1} {month1} {year_full1}', f'{day2} {month2} {year_full2}', f'{day3} {month3} {year_full3}']
    elif '%d %b, %Y' in fmt or fmt == '%d %b, %Y':
        if months_to_use:
            month1 = months_to_use[2] if len(months_to_use) > 2 else months_to_use[0]
            month2 = months_to_use[11] if len(months_to_use) > 11 else months_to_use[1]
            month3 = months_to_use[6] if len(months_to_use) > 6 else months_to_use[2]
            examples = [f'{day1} {month1}, {year_full1}', f'{day2} {month2}, {year_full2}', f'{day3} {month3}, {year_full3}']
    elif '%d %m %Y' in fmt or fmt == '%d %m %Y':
        # Pattern with month name (not numeric)
        if months_to_use:
            month1 = months_to_use[2] if len(months_to_use) > 2 else months_to_use[0]
            month2 = months_to_use[11] if len(months_to_use) > 11 else months_to_use[1]
            month3 = months_to_use[6] if len(months_to_use) > 6 else months_to_use[2]
            
            # Check for articles (de, le)
            article = ''
            if 'article' in name and 'not article' not in name and 'no article' not in name:
                if lang_code in ['es', 'pt', 'it']:
                    article = 'de '
                elif lang_code == 'fr':
                    article = 'le '
            
            # Check for weekday
            weekday_prefix = ''
            if 'weekday' in name and weekdays_to_use:
                weekday1 = weekdays_to_use[0] if len(weekdays_to_use) > 0 else ''
                weekday2 = weekdays_to_use[1] if len(weekdays_to_use) > 1 else ''
                weekday3 = weekdays_to_use[2] if len(weekdays_to_use) > 2 else ''
                weekday_prefix = f'{weekday1}, ' if weekday1 else ''
            
            # Check for year suffix (Russian)
            year_suffix = ''
            if 'year' in name and lang_code == 'ru':
                year_suffix = ' г.'
            
            # Check for Turkish suffix
            tr_suffix = ''
            if lang_code == 'tr' and 'tarihinde' in key or 'tarihli' in key:
                tr_suffix = ' tarihinde'
            
            examples = [
                f'{weekday_prefix}{day1} {article}{month1} {year_full1}{year_suffix}{tr_suffix}'.strip(),
                f'{weekday_prefix}{day2} {article}{month2} {year_full2}{year_suffix}{tr_suffix}'.strip(),
                f'{weekday_prefix}{day3} {article}{month3} {year_full3}{year_suffix}{tr_suffix}'.strip()
            ]
        else:
            # Fallback to numeric
            examples = [f'{day1} {month_num1} {year_full1}', f'{day2} {month_num2} {year_full2}', f'{day3} {month_num3} {year_full3}']
    elif '%m %d %Y' in fmt or fmt == '%m %d %Y':
        # Month-first format
        if months_to_use:
            month1 = months_to_use[2] if len(months_to_use) > 2 else months_to_use[0]
            month2 = months_to_use[11] if len(months_to_use) > 11 else months_to_use[1]
            month3 = months_to_use[6] if len(months_to_use) > 6 else months_to_use[2]
            examples = [f'{month1} {day1}, {year_full1}', f'{month2} {day2}, {year_full2}', f'{month3} {day3}, {year_full3}']
    
    # Fallback: generate simple numeric examples if nothing matched
    if not examples:
        if noyear:
            examples = ['15.03', '3.12', '28.07']
        elif yearshort:
            examples = ['15/03/24', '3/12/23', '28/7/25']
        else:
            examples = ['15/03/2024', '3/12/2023', '28/7/2025']
    
    # Limit to 2-3 examples
    return examples[:3]


def extract_pattern_info(pattern, lang_code):
    """Extract information from a pattern dictionary."""
    info = {
        'key': pattern.get('key', 'N/A'),
        'name': pattern.get('name', 'N/A'),
        'format': pattern.get('format', 'N/A'),
        'min_length': pattern.get('length', {}).get('min', 'N/A'),
        'max_length': pattern.get('length', {}).get('max', 'N/A'),
        'yearshort': pattern.get('yearshort', False),
        'noyear': pattern.get('noyear', False),
        'filter': pattern.get('filter', 'N/A'),
        'lang': lang_code,
        'examples': generate_examples(pattern, lang_code),
    }
    return info


def format_table_value(value):
    """Format a value for table display."""
    if value is False:
        return ''
    if value is True:
        return 'Yes'
    if value == 'N/A':
        return ''
    return str(value)


def generate_markdown_table(patterns_info):
    """Generate a markdown table from pattern information."""
    if not patterns_info:
        return "No patterns available.\n"
    
    # Table header
    lines = []
    lines.append("| Pattern Key | Name | Format | Min Length | Max Length | Year Short | No Year | Filter | Examples |")
    lines.append("|-------------|------|--------|------------|------------|------------|---------|--------|----------|")
    
    # Table rows
    for info in patterns_info:
        notes = []
        if info['yearshort']:
            notes.append("2-digit year")
        if info['noyear']:
            notes.append("No year")
        notes_str = ", ".join(notes) if notes else ""
        
        # Format examples
        examples = info.get('examples', [])
        if examples:
            examples_str = "`" + "`, `".join(examples) + "`"
        else:
            examples_str = ""
        
        row = (
            f"| `{info['key']}` | {info['name']} | `{info['format']}` | "
            f"{format_table_value(info['min_length'])} | {format_table_value(info['max_length'])} | "
            f"{format_table_value(info['yearshort'])} | {format_table_value(info['noyear'])} | "
            f"{format_table_value(info['filter'])} | {examples_str} |"
        )
        lines.append(row)
    
    return "\n".join(lines) + "\n"


def generate_documentation():
    """Generate the complete documentation."""
    lines = []
    
    # Header
    lines.append("# qddate Pattern Documentation")
    lines.append("")
    lines.append("This document provides comprehensive information about all date parsing patterns")
    lines.append("supported by qddate, organized by language.")
    lines.append("")
    
    # Calculate statistics
    total_patterns = sum(len(patterns) for patterns in PATTERN_COLLECTIONS.values())
    total_languages = len([lang for lang, patterns in PATTERN_COLLECTIONS.items() if patterns])
    
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total Patterns**: {total_patterns}")
    lines.append(f"- **Supported Languages**: {total_languages}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Generate sections for each language
    for lang_code in sorted(PATTERN_COLLECTIONS.keys()):
        patterns = PATTERN_COLLECTIONS[lang_code]
        if not patterns:
            continue
        
        lang_name = LANGUAGE_NAMES.get(lang_code, lang_code.upper())
        pattern_count = len(patterns)
        
        lines.append(f"## {lang_name} ({lang_code.upper()})")
        lines.append("")
        lines.append(f"**Pattern Count**: {pattern_count}")
        lines.append("")
        
        # Extract pattern information
        patterns_info = [extract_pattern_info(p, lang_code) for p in patterns]
        
        # Generate table
        lines.append(generate_markdown_table(patterns_info))
        lines.append("")
    
    # Add notes section
    lines.append("---")
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("### Pattern Flags")
    lines.append("")
    lines.append("- **Year Short**: Indicates that the pattern handles 2-digit years (e.g., '99' for 1999)")
    lines.append("- **No Year**: Indicates that the pattern matches dates without a year component")
    lines.append("- **Filter**: Filter level used for pattern matching optimization (1 = stricter filtering)")
    lines.append("")
    lines.append("### Format Strings")
    lines.append("")
    lines.append("Format strings use Python's `strftime` format codes:")
    lines.append("- `%d` - Day of the month (01-31)")
    lines.append("- `%m` - Month as a number (01-12)")
    lines.append("- `%Y` - Year with century (e.g., 2024)")
    lines.append("- `%y` - Year without century (00-99)")
    lines.append("- `%b` - Abbreviated month name")
    lines.append("")
    lines.append("### Length Constraints")
    lines.append("")
    lines.append("Each pattern specifies minimum and maximum string lengths to optimize")
    lines.append("pattern matching performance. Patterns are only tested against strings")
    lines.append("that fall within these length constraints.")
    lines.append("")
    
    return "\n".join(lines)


def main():
    """Main entry point."""
    output_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'PATTERNS.md')
    output_dir = os.path.dirname(output_path)
    
    # Create docs directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate documentation
    doc_content = generate_documentation()
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(doc_content)
    
    print(f"Documentation generated successfully: {output_path}")
    print(f"Total patterns documented: {sum(len(patterns) for patterns in PATTERN_COLLECTIONS.values())}")


if __name__ == '__main__':
    main()

