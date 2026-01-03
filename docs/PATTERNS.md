# qddate Pattern Documentation

This document provides comprehensive information about all date parsing patterns
supported by qddate, organized by language.

## Summary

- **Base Patterns**: 89 (expands to 712+ patterns at runtime with time variants and text-after variants)
- **Supported Languages**: 11

---

## Bulgarian (BG)

**Pattern Count**: 2

| Pattern Key | Name | Format | Min Length | Max Length | Year Short | No Year | Filter | Examples |
|-------------|------|--------|------------|------------|------------|---------|--------|----------|
| `dt:date:bg_base` | Base bulgarian date with month name | `%d %m %Y` | 11 | 22 |  |  | 1 | `15 Мapт 2024`, `3 Дeкeмвpи 2023`, `28 Юли 2025` |
| `dt:date:bg_base_lc` | Base bulgarian date with month name and lowcase | `%d %m %Y` | 11 | 22 |  |  | 1 | `15 мapт 2024`, `3 дeкeмвpи 2023`, `28 юли 2025` |


## Czech (CZ)

**Pattern Count**: 4

| Pattern Key | Name | Format | Min Length | Max Length | Year Short | No Year | Filter | Examples |
|-------------|------|--------|------------|------------|------------|---------|--------|----------|
| `dt:date:cz_base` | Base Czech date with month name (nominative) | `%d %m %Y` | 11 | 22 |  |  | 1 | `15 Březen 2024`, `3 Prosinec 2023`, `28 Červenec 2025` |
| `dt:date:cz_base_lc` | Base Czech date with month name lowercase (nominative) | `%d %m %Y` | 11 | 22 |  |  | 1 | `15 březen 2024`, `3 prosinec 2023`, `28 červenec 2025` |
| `dt:date:cz_gen` | Czech date with month name in genitive form | `%d %m %Y` | 11 | 22 |  |  | 1 | `15 Března 2024`, `3 Prosince 2023`, `28 Července 2025` |
| `dt:date:cz_gen_lc` | Czech date with month name in genitive form (lowercase) | `%d %m %Y` | 11 | 22 |  |  | 1 | `15 březen 2024`, `3 prosinec 2023`, `28 červenec 2025` |


## German (DE)

**Pattern Count**: 8

| Pattern Key | Name | Format | Min Length | Max Length | Year Short | No Year | Filter | Examples |
|-------------|------|--------|------------|------------|------------|---------|--------|----------|
| `dt:date:de_base` | Base german date with month name | `%d %m %Y` | 11 | 22 |  |  | 1 | `15 März 2024`, `3 Dezember 2023`, `28 Juli 2025` |
| `dt:date:de_base_lc` | Base german date with month name and lowcase | `%d %m %Y` | 11 | 22 |  |  | 1 | `15 märz 2024`, `3 dezember 2023`, `28 juli 2025` |
| `dt:date:de_weekday` | German date with weekday | `%d %m %Y` | 15 | 32 |  |  | 1 | `Montag, 15 März 2024`, `Montag, 3 Dezember 2023`, `Montag, 28 Juli 2025` |
| `dt:date:de_weekday_lc` | German date with weekday lowercase | `%d %m %Y` | 15 | 32 |  |  | 1 | `Montag, 15 märz 2024`, `Montag, 3 dezember 2023`, `Montag, 28 juli 2025` |
| `dt:date:de_short` | German date with abbreviated month | `%d %m %Y` | 9 | 18 |  |  | 1 | `15 Mär 2024`, `3 Dez 2023`, `28 Jul 2025` |
| `dt:date:de_short_lc` | German date with abbreviated month lowercase | `%d %m %Y` | 9 | 18 |  |  | 1 | `15 Mär 2024`, `3 Dez 2023`, `28 Jul 2025` |
| `dt:date:de_rare_1` | German date month-first format | `%m %d %Y` | 11 | 25 |  |  | 1 | `März 15, 2024`, `Dezember 3, 2023`, `Juli 28, 2025` |
| `dt:date:de_rare_2` | German date month-first lowercase | `%m %d %Y` | 11 | 25 |  |  | 1 | `märz 15, 2024`, `dezember 3, 2023`, `juli 28, 2025` |


## English (EN)

**Pattern Count**: 38

| Pattern Key | Name | Format | Min Length | Max Length | Year Short | No Year | Filter | Examples |
|-------------|------|--------|------------|------------|------------|---------|--------|----------|
| `dt:date:date_1` | Datetime string | `%d/%m/%Y` | 8 | 10 |  |  |  | `15/03/2024`, `3/12/2023`, `28/7/2025` |
| `dt:date:date_2` | Datetime string | `%d.%m.%Y` | 8 | 10 |  |  |  | `15.03.2024`, `3.12.2023`, `28.07.2025` |
| `dt:date:date_3` | Datetime string | `%Y/%m/%d` | 8 | 10 |  |  |  | `2024/03/15`, `2023/12/3`, `2025/7/28` |
| `dt:date:date_4` | Datetime string | `%d.%m.%y` | 6 | 8 | Yes |  |  | `15.03.24`, `3.12.23`, `28.07.25` |
| `dt:date:date_iso8601` | ISO 8601 date | `%d-%m-%Y` | 8 | 10 |  |  |  | `15-03-2024`, `3-12-2023`, `28-07-2025` |
| `dt:date:date_iso8601_short` | ISO 8601 date shorted | `%d-%m-%Y` | 6 | 8 | Yes |  |  | `15-03-2024`, `3-12-2023`, `28-07-2025` |
| `dt:date:date_8` | Date with 2-digits year | `%d/%m/%y` | 6 | 8 | Yes |  |  | `15/03/24`, `3/12/23`, `28/7/25` |
| `dt:date:date_9` | Date as ISO | `%Y-%m-%d` | 6 | 10 |  |  |  | `2024-03-15`, `2023-12-03`, `2025-07-28` |
| `dt:date:date_10` | Date as yyyy.mm.dd | `%Y.%m.%d` | 6 | 10 |  |  |  | `2024.03.15`, `2023.12.3`, `2025.7.28` |
| `dt:date:date_usa_1` | Date with 2-digits year | `%m/%d/%y` | 6 | 8 | Yes |  |  | `03/15/24`, `12/3/23`, `7/28/25` |
| `dt:date:date_usa` | USA mm/dd/yyyy string | `%m/%d/%Y` | 8 | 10 |  |  |  | `03/15/2024`, `12/3/2023`, `7/28/2025` |
| `dt:date:date_eng1` | Date with english month and possible dots | `%d.%b.%Y` | 10 | 20 |  |  |  | `15.March.2024`, `3.December.2023`, `28.July.2025` |
| `dt:date:date_eng1x` | Date with english month and ,  | `%d.%b.%Y` | 10 | 20 |  |  |  | `15.March.2024`, `3.December.2023`, `28.July.2025` |
| `dt:date:date_eng1_lc` | Date with english month lowcase | `%d.%b.%Y` | 10 | 20 |  |  |  | `15.march.2024`, `3.december.2023`, `28.jule.2025` |
| `dt:date:date_eng1_short` | Date with english month short | `%d.%b.%Y` | 10 | 11 |  |  |  | `15.mar.2024`, `3.dec.2023`, `28.jul.2025` |
| `dt:date:date_eng2` | Date with english month 2 | `%b %d, %Y` | 10 | 22 |  |  |  | `March 15, 2024`, `December 3, 2023`, `July 28, 2025` |
| `dt:date:date_eng2_lc` | Date with english month 2 lowcase | `%b %d, %Y` | 10 | 22 |  |  |  | `march 15, 2024`, `december 3, 2023`, `jule 28, 2025` |
| `dt:date:date_eng2_short` | Date with english month 2 short | `%b %d, %Y` | 10 | 10 |  |  |  | `mar 15, 2024`, `dec 3, 2023`, `jul 28, 2025` |
| `dt:date:date_eng3` | Date with english month full lowcase | `%b %d, %Y` | 10 | 20 |  |  | 2 | `march 15, 2024`, `december 3, 2023`, `jule 28, 2025` |
| `dt:date:date_eng3_nolc` | Date with english month full | `%b %d, %Y` | 10 | 20 |  |  | 2 | `March 15, 2024`, `December 3, 2023`, `July 28, 2025` |
| `dt:date:date_eng4_short` | Date with english month short with dash | `%d-%b-%y` | 10 | 10 | Yes |  |  | `15-mar-24`, `3-dec-23`, `28-jul-25` |
| `dt:date:noyear_1` | Datetime string without year | `%d.%m` | 5 | 5 |  | Yes |  | `15.03`, `3.12`, `28.07` |
| `dt:date:date_4_point` | Datetime string | `%d.%m.%y` | 6 | 9 | Yes |  |  | `15.03.24`, `3.12.23`, `28.07.25` |
| `dt:date:weekday_eng` | Date with english month and weekday | `%d %m %Y` | 17 | 27 |  |  | 1 | `Monday, 15 March 2024`, `Monday, 3 December 2023`, `Monday, 28 July 2025` |
| `dt:date:weekday_eng_lc` | Date with english month and weekday | `%d %m %Y` | 17 | 27 |  |  | 1 | `Monday, 15 March 2024`, `Monday, 3 December 2023`, `Monday, 28 July 2025` |
| `dt:date:weekday_eng_wshort` | Date with english month and weekday | `%d %m %Y` | 16 | 27 |  |  | 1 | `Monday, 15 March 2024`, `Monday, 3 December 2023`, `Monday, 28 July 2025` |
| `dt:date:weekday_eng_mshort_wshort` | Date with short english month and short weekday | `%d %m %Y` | 15 | 15 |  |  | 1 | `mon, 15 mar 2024`, `mon, 3 dec 2023`, `mon, 28 jul 2025` |
| `dt:date:weekday_eng_iso` | Date with english weekday and iso date | `%d/%m/%Y` | 13 | 25 |  |  | 1 | `15/03/2024`, `3/12/2023`, `28/7/2025` |
| `dt:date:weekday_short_eng_iso` | Date with english short weekday and iso date | `%d/%m/%Y` | 13 | 18 |  |  | 1 | `15/03/2024`, `3/12/2023`, `28/7/2025` |
| `dt:date:weekday_eng_mixed` | Date with english full weekday and short month | `%d %m %Y` | 13 | 27 |  |  | 1 | `mon, 15 mar 2024`, `mon, 3 dec 2023`, `mon, 28 jul 2025` |
| `dt:date:date_eng_abbrev1` | Date with abbreviated English month (day first) | `%d %b %Y` | 9 | 13 |  |  | 1 | `15 mar 2024`, `3 dec 2023`, `28 jul 2025` |
| `dt:date:date_eng_abbrev2` | Date with abbreviated English month (month first) | `%b %d, %Y` | 9 | 15 |  |  | 1 | `mar 15, 2024`, `dec 3, 2023`, `jul 28, 2025` |
| `dt:date:date_eng_abbrev3` | Date with abbreviated English month and comma (day first) | `%d %b, %Y` | 9 | 15 |  |  | 1 | `15 mar, 2024`, `3 dec, 2023`, `28 jul, 2025` |
| `dt:date:weekday_eng_abbrev1` | Date with abbreviated English month and short weekday | `%d %b %Y` | 13 | 17 |  |  | 1 | `15 mar 2024`, `3 dec 2023`, `28 jul 2025` |
| `dt:date:weekday_eng_abbrev2` | Date with abbreviated English month, short weekday, and comma | `%d %b %Y` | 13 | 18 |  |  | 1 | `15 mar 2024`, `3 dec 2023`, `28 jul 2025` |
| `dt:date:date_eng_abbrev_postfix` | Date with abbreviated English month and day with ordinal suffix | `%d %b %Y` | 11 | 16 |  |  | 1 | `15 mar 2024`, `3 dec 2023`, `28 jul 2025` |
| `dt:date:date_5` | Datetime string as ddmmyyyy | `%d%m%Y` | 8 | 8 |  |  |  | `15032024`, `03122023`, `28072025` |
| `dt:date:date_6` | Datetime string as yyyymmdd | `%Y%m%d` | 8 | 8 |  |  |  | `20240315`, `20231203`, `20250728` |


## Spanish (ES)

**Pattern Count**: 6

| Pattern Key | Name | Format | Min Length | Max Length | Year Short | No Year | Filter | Examples |
|-------------|------|--------|------------|------------|------------|---------|--------|----------|
| `dt:date:es_base` | Base spanish date with month name not article | `%d %m %Y` | 11 | 22 |  |  | 1 | `15 Marzo 2024`, `3 Diciembre 2023`, `28 Julio 2025` |
| `dt:date:es_base_lc` | Base spanish date with month name and lowcase, no article | `%d %m %Y` | 11 | 22 |  |  | 1 | `15 marzo 2024`, `3 diciembre 2023`, `28 julio 2025` |
| `dt:date:es_base_article` | Base spanish date with month name and articles | `%d %m %Y` | 11 | 26 |  |  | 1 | `15 de Marzo 2024`, `3 de Diciembre 2023`, `28 de Julio 2025` |
| `dt:date:es_base_lc_article` | Base spanish date with month name and articles and lowcase | `%d %m %Y` | 11 | 26 |  |  | 1 | `15 de marzo 2024`, `3 de diciembre 2023`, `28 de julio 2025` |
| `dt:date:es_rare_1` | Spanish date stars with month name | `%M %d %Y` | 11 | 25 |  |  | 1 | `15/03/2024`, `3/12/2023`, `28/7/2025` |
| `dt:date:es_rare_2` | Spanish date stars with month name lowcase | `%M %d %Y` | 11 | 25 |  |  | 1 | `15/03/2024`, `3/12/2023`, `28/7/2025` |


## French (FR)

**Pattern Count**: 4

| Pattern Key | Name | Format | Min Length | Max Length | Year Short | No Year | Filter | Examples |
|-------------|------|--------|------------|------------|------------|---------|--------|----------|
| `dt:date:fr_base` | Base french date with month name not archive | `%d %m %Y` | 11 | 22 |  |  | 1 | `15 Mars 2024`, `3 Décembre 2023`, `28 Juillet 2025` |
| `dt:date:fr_base_lc` | Base french date with month name and lowcase, no article | `%d %m %Y` | 11 | 22 |  |  | 1 | `15 mars 2024`, `3 décembre 2023`, `28 juillet 2025` |
| `dt:date:fr_base_article` | Base french date with month name and articles | `%d %m %Y` | 11 | 22 |  |  | 1 | `15 le Mars 2024`, `3 le Décembre 2023`, `28 le Juillet 2025` |
| `dt:date:fr_base_lc_article` | Base french date with month name and articles and lowcase | `%d %m %Y` | 11 | 22 |  |  | 1 | `15 le mars 2024`, `3 le décembre 2023`, `28 le juillet 2025` |


## Italian (IT)

**Pattern Count**: 6

| Pattern Key | Name | Format | Min Length | Max Length | Year Short | No Year | Filter | Examples |
|-------------|------|--------|------------|------------|------------|---------|--------|----------|
| `dt:date:it_base` | Base italian date with month name not article | `%d %m %Y` | 11 | 22 |  |  | 1 | `15 Marzo 2024`, `3 Dicembre 2023`, `28 Luglio 2025` |
| `dt:date:it_base_lc` | Base italian date with month name and lowcase, no article | `%d %m %Y` | 11 | 22 |  |  | 1 | `15 marzo 2024`, `3 dicembre 2023`, `28 luglio 2025` |
| `dt:date:it_base_article` | Base italian date with month name and articles | `%d %m %Y` | 11 | 26 |  |  | 1 | `15 de Marzo 2024`, `3 de Dicembre 2023`, `28 de Luglio 2025` |
| `dt:date:it_base_lc_article` | Base italian date with month name and articles and lowcase | `%d %m %Y` | 11 | 26 |  |  | 1 | `15 de marzo 2024`, `3 de dicembre 2023`, `28 de luglio 2025` |
| `dt:date:it_rare_1` | Italian date stars with month name | `%M %d %Y` | 11 | 25 |  |  | 1 | `15/03/2024`, `3/12/2023`, `28/7/2025` |
| `dt:date:it_rare_2` | Italian date stars with month name lowcase | `%M %d %Y` | 11 | 25 |  |  | 1 | `15/03/2024`, `3/12/2023`, `28/7/2025` |


## Polish (PL)

**Pattern Count**: 4

| Pattern Key | Name | Format | Min Length | Max Length | Year Short | No Year | Filter | Examples |
|-------------|------|--------|------------|------------|------------|---------|--------|----------|
| `dt:date:pl_base` | Base polish date with month name (nominative) | `%d %m %Y` | 11 | 28 |  |  | 1 | `15 Marzec 2024`, `3 Grudzień 2023`, `28 Lipiec 2025` |
| `dt:date:pl_base_lc` | Base polish date with month name lower-case (nominative) | `%d %m %Y` | 11 | 28 |  |  | 1 | `15 Marzec 2024`, `3 Grudzień 2023`, `28 Lipiec 2025` |
| `dt:date:pl_gen` | Polish date with month name in genitive form | `%d %m %Y` | 11 | 28 |  |  | 1 | `15 Marca 2024`, `3 Grudnia 2023`, `28 Lipca 2025` |
| `dt:date:pl_gen_lc` | Polish date with month name in genitive form (lower-case) | `%d %m %Y` | 11 | 28 |  |  | 1 | `15 Marca 2024`, `3 Grudnia 2023`, `28 Lipca 2025` |


## Portuguese (PT)

**Pattern Count**: 4

| Pattern Key | Name | Format | Min Length | Max Length | Year Short | No Year | Filter | Examples |
|-------------|------|--------|------------|------------|------------|---------|--------|----------|
| `dt:date:pt_base` | Base portugal date with month name not article | `%d %m %Y` | 11 | 22 |  |  | 1 | `15 Março 2024`, `3 Dezembro 2023`, `28 Julho 2025` |
| `dt:date:pt_base_lc` | Base portugal date with month name and lowcase, no article | `%d %m %Y` | 11 | 22 |  |  | 1 | `15 março 2024`, `3 dezembro 2023`, `28 julho 2025` |
| `dt:date:pt_base_article` | Base portugal date with month name and articles | `%d %m %Y` | 11 | 26 |  |  | 1 | `15 de Março 2024`, `3 de Dezembro 2023`, `28 de Julho 2025` |
| `dt:date:pt_base_lc_article` | Base portugal date with month name and articles and lowcase | `%d %m %Y` | 11 | 26 |  |  | 1 | `15 de março 2024`, `3 de dezembro 2023`, `28 de julho 2025` |


## Russian (RU)

**Pattern Count**: 11

| Pattern Key | Name | Format | Min Length | Max Length | Year Short | No Year | Filter | Examples |
|-------------|------|--------|------------|------------|------------|---------|--------|----------|
| `dt:date:date_rus` | Date with russian month | `%d %m %Y` | 11 | 20 |  |  | 1 | `15 Марта 2024`, `3 Декабря 2023`, `28 Июля 2025` |
| `dt:date:date_rus2` | Date with russian month and year word | `%d %m %Y` | 13 | 20 |  |  | 1 | `15 Марта 2024 г.`, `3 Декабря 2023 г.`, `28 Июля 2025 г.` |
| `dt:date:date_rus3` | Date with russian year | `%d.%m.%Y` | 14 | 20 |  |  |  | `15.03.2024`, `3.12.2023`, `28.07.2025` |
| `dt:date:date_rus_lc1` | Date with russian month | `%d %m %Y` | 10 | 20 |  |  | 1 | `15 Марта 2024`, `3 Декабря 2023`, `28 Июля 2025` |
| `dt:date:date_rus_lc2` | Date with russian month with year word | `%d %m %Y` | 13 | 25 |  |  | 1 | `15 Марта 2024 г.`, `3 Декабря 2023 г.`, `28 Июля 2025 г.` |
| `dt:date:weekday_rus` | Date with russian month and weekday | `%d %m %Y` | 13 | 20 |  |  | 1 | `Понедельник, 15 Марта 2024`, `Понедельник, 3 Декабря 2023`, `Понедельник, 28 Июля 2025` |
| `dt:date:weekday_rus_lc1` | Date with russian month and weekday | `%d %m %Y` | 13 | 25 |  |  | 1 | `Понедельник, 15 Марта 2024`, `Понедельник, 3 Декабря 2023`, `Понедельник, 28 Июля 2025` |
| `dt:date:rus_rare_2` | Date with russian month with dots as divider | `%d.%m.%Y` | 11 | 20 |  |  | 1 | `15.03.2024`, `3.12.2023`, `28.07.2025` |
| `dt:date:rus_rare_3` | Date with russian month with dots as divider with low case months | `%d.%m.%Y` | 11 | 20 |  |  | 1 | `15.03.2024`, `3.12.2023`, `28.07.2025` |
| `dt:date:rus_rare_5` | Russian date stars with month name | `%d %m %Y` | 13 | 22 |  |  | 1 | `15 Марта 2024`, `3 Декабря 2023`, `28 Июля 2025` |
| `dt:date:rus_rare_6` | Russian date stars with weekday and follows with month name | `%d %m %Y` | 13 | 22 |  |  | 1 | `Понедельник, 15 Марта 2024`, `Понедельник, 3 Декабря 2023`, `Понедельник, 28 Июля 2025` |


## Turkish (TR)

**Pattern Count**: 2

| Pattern Key | Name | Format | Min Length | Max Length | Year Short | No Year | Filter | Examples |
|-------------|------|--------|------------|------------|------------|---------|--------|----------|
| `dt:date:tr_base` | Base Turkish date with capitalized month | `%d %m %Y` | 11 | 32 |  |  | 1 | `15 Mart 2024`, `3 Aralık 2023`, `28 Temmuz 2025` |
| `dt:date:tr_base_lc` | Base Turkish date with lowercase month | `%d %m %Y` | 11 | 32 |  |  | 1 | `15 mart 2024`, `3 aralık 2023`, `28 temmuz 2025` |


---

## Notes

### Pattern Flags

- **Year Short**: Indicates that the pattern handles 2-digit years (e.g., '99' for 1999)
- **No Year**: Indicates that the pattern matches dates without a year component
- **Filter**: Filter level used for pattern matching optimization (1 = stricter filtering)

### Format Strings

Format strings use Python's `strftime` format codes:
- `%d` - Day of the month (01-31)
- `%m` - Month as a number (01-12)
- `%Y` - Year with century (e.g., 2024)
- `%y` - Year without century (00-99)
- `%b` - Abbreviated month name

### Length Constraints

Each pattern specifies minimum and maximum string lengths to optimize
pattern matching performance. Patterns are only tested against strings
that fall within these length constraints.
