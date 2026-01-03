#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generate CSV file with date and datetime strings for performance benchmarking.
Generates at least 10,000 examples covering all supported patterns.
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

# Month names in different languages
MONTHS = {
    'en': ['January', 'February', 'March', 'April', 'May', 'June',
           'July', 'August', 'September', 'October', 'November', 'December'],
    'en_lc': ['january', 'february', 'march', 'april', 'may', 'june',
              'july', 'august', 'september', 'october', 'november', 'december'],
    'en_short': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    'es': ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
           'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
    'es_lc': ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
              'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'],
    'es_short': ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
    'fr': ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
           'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'],
    'fr_lc': ['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
              'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'],
    'fr_short': ['Janv', 'Févr', 'Mars', 'Avr', 'Mai', 'Juin',
                 'Juil', 'Août', 'Sept', 'Oct', 'Nov', 'Déc'],
    'de': ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
           'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'],
    'de_lc': ['januar', 'februar', 'märz', 'april', 'mai', 'juni',
              'juli', 'august', 'september', 'oktober', 'november', 'dezember'],
    'de_short': ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'],
    'ru': ['Января', 'Февраля', 'Марта', 'Апреля', 'Мая', 'Июня',
           'Июля', 'Августа', 'Сентября', 'Октября', 'Ноября', 'Декабря'],
    'ru_lc': ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
              'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'],
    'ru_orig': ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'],
    'it': ['Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno',
           'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre'],
    'it_lc': ['gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno',
              'luglio', 'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre'],
    'pt': ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
           'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'],
    'pt_lc': ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
              'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'],
    'bg': ['Януари', 'Февруари', 'Март', 'Април', 'Май', 'Юни',
           'Юли', 'Август', 'Септември', 'Октомври', 'Ноември', 'Декември'],
    'bg_lc': ['януари', 'февруари', 'март', 'април', 'май', 'юни',
              'юли', 'август', 'септември', 'октомври', 'ноември', 'декември'],
    'cz': ['Leden', 'Únor', 'Březen', 'Duben', 'Květen', 'Červen',
           'Červenec', 'Srpen', 'Září', 'Říjen', 'Listopad', 'Prosinec'],
    'cz_lc': ['leden', 'únor', 'březen', 'duben', 'květen', 'červen',
              'červenec', 'srpen', 'září', 'říjen', 'listopad', 'prosinec'],
    'pl': ['Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec',
           'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień'],
    'pl_lc': ['styczeń', 'luty', 'marzec', 'kwiecień', 'maj', 'czerwiec',
              'lipiec', 'sierpień', 'wrzesień', 'październik', 'listopad', 'grudzień'],
    'nl': ['Januari', 'Februari', 'Maart', 'April', 'Mei', 'Juni',
           'Juli', 'Augustus', 'September', 'Oktober', 'November', 'December'],
    'nl_lc': ['januari', 'februari', 'maart', 'april', 'mei', 'juni',
              'juli', 'augustus', 'september', 'oktober', 'november', 'december'],
    'tr': ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran',
           'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'],
    'tr_lc': ['ocak', 'şubat', 'mart', 'nisan', 'mayıs', 'haziran',
              'temmuz', 'ağustos', 'eylül', 'ekim', 'kasım', 'aralık'],
}

# Weekday names
WEEKDAYS = {
    'en': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
    'en_short': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    'es': ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'],
    'fr': ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'],
    'de': ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag'],
    'ru': ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресение'],
}

# Numeric suffixes
def get_suffix(day):
    """Get the correct ordinal suffix for a day."""
    if 10 <= day % 100 <= 20:
        return 'th'
    return {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')


def random_date(start_year=1900, end_year=2030):
    """Generate a random date."""
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    days = random.randint(0, delta.days)
    return start + timedelta(days=days)


def generate_numeric_dates(count=2000):
    """Generate numeric date formats."""
    dates = []
    formats = [
        ('%d/%m/%Y', '/', 'dt:date:date_1'),
        ('%d.%m.%Y', '.', 'dt:date:date_2'),
        ('%d-%m-%Y', '-', 'dt:date:date_iso8601'),
        ('%Y/%m/%d', '/', 'dt:date:date_3'),
        ('%Y-%m-%d', '-', 'dt:date:date_9'),
        ('%Y.%m.%d', '.', 'dt:date:date_10'),
        ('%m/%d/%Y', '/', 'dt:date:date_usa'),
        ('%d/%m/%y', '/', 'dt:date:date_8'),
        ('%d.%m.%y', '.', 'dt:date:date_4'),
        ('%d-%m-%y', '-', 'dt:date:date_iso8601_short'),
        ('%m/%d/%y', '/', 'dt:date:date_usa_1'),
        ('%d %m %Y', ' ', 'dt:date:date_1'),  # Space variant
        ('%d %m %y', ' ', 'dt:date:date_8'),  # Space variant
    ]
    
    for _ in range(count):
        dt = random_date()
        fmt, sep, pattern_key = random.choice(formats)
        date_str = dt.strftime(fmt)
        dates.append((date_str, pattern_key))
    
    return dates


def generate_english_dates(count=1500):
    """Generate English date formats."""
    dates = []
    
    for _ in range(count):
        dt = random_date()
        day = dt.day
        month_idx = dt.month - 1
        year = dt.year
        
        patterns = [
            (f"{day} {MONTHS['en'][month_idx]} {year}", 'dt:date:date_eng1x'),
            (f"{day} {MONTHS['en_lc'][month_idx]} {year}", 'dt:date:date_eng1_lc'),
            (f"{day} {MONTHS['en_short'][month_idx]} {year}", 'dt:date:date_eng1_short'),
            (f"{MONTHS['en'][month_idx]} {day}, {year}", 'dt:date:date_eng3_nolc'),
            (f"{MONTHS['en_lc'][month_idx]} {day}, {year}", 'dt:date:date_eng3'),
            (f"{MONTHS['en_short'][month_idx]} {day}, {year}", 'dt:date:date_eng2_short'),
            (f"{day}.{MONTHS['en'][month_idx]}.{year}", 'dt:date:date_eng1'),
            (f"{day}.{MONTHS['en_lc'][month_idx]}.{year}", 'dt:date:date_eng1_lc'),
            (f"{day}.{MONTHS['en_short'][month_idx]}.{year}", 'dt:date:date_eng1_short'),
            (f"{day}{get_suffix(day)} {MONTHS['en'][month_idx]} {year}", 'dt:date:date_eng2'),
            (f"{MONTHS['en'][month_idx]} {day}{get_suffix(day)}, {year}", 'dt:date:date_eng2'),
        ]
        
        # Add weekday variants
        if random.random() < 0.3:
            weekday_idx = dt.weekday()
            patterns.extend([
                (f"{WEEKDAYS['en'][weekday_idx]} {day} {MONTHS['en'][month_idx]} {year}", 'dt:date:weekday_eng'),
                (f"{WEEKDAYS['en_short'][weekday_idx]} {day} {MONTHS['en_short'][month_idx]} {year}", 'dt:date:weekday_eng_short'),
                (f"{WEEKDAYS['en_short'][weekday_idx]}, {day} {MONTHS['en'][month_idx]} {year}", 'dt:date:weekday_eng_short'),
            ])
        
        dates.append(random.choice(patterns))
    
    return dates


def generate_spanish_dates(count=800):
    """Generate Spanish date formats."""
    dates = []
    
    for _ in range(count):
        dt = random_date()
        day = dt.day
        month_idx = dt.month - 1
        year = dt.year
        
        patterns = [
            (f"{day} de {MONTHS['es'][month_idx]} de {year}", 'dt:date:es_base_article'),
            (f"{day} de {MONTHS['es_lc'][month_idx]} de {year}", 'dt:date:es_base_lc_article'),
            (f"{day} de {MONTHS['es_short'][month_idx]} de {year}", 'dt:date:es_short'),
            (f"{MONTHS['es'][month_idx]} {day}, {year}", 'dt:date:es_rare_1'),
            (f"{MONTHS['es_lc'][month_idx]} {day}, {year}", 'dt:date:es_rare_2'),
            (f"{day} {MONTHS['es'][month_idx]} {year}", 'dt:date:es_base'),
            (f"{day} {MONTHS['es_lc'][month_idx]} {year}", 'dt:date:es_base_lc'),
        ]
        
        if random.random() < 0.2:
            weekday_idx = dt.weekday()
            patterns.append((f"{WEEKDAYS['es'][weekday_idx]}, {day} de {MONTHS['es'][month_idx]} de {year}", 'dt:date:es_weekday'))
        
        dates.append(random.choice(patterns))
    
    return dates


def generate_french_dates(count=800):
    """Generate French date formats."""
    dates = []
    
    for _ in range(count):
        dt = random_date()
        day = dt.day
        month_idx = dt.month - 1
        year = dt.year
        
        patterns = [
            (f"Le {day} {MONTHS['fr'][month_idx]} {year}", 'dt:date:fr_base_article'),
            (f"{day} {MONTHS['fr'][month_idx]} {year}", 'dt:date:fr_base'),
            (f"{day} {MONTHS['fr_lc'][month_idx]} {year}", 'dt:date:fr_base_lc'),
            (f"{day} {MONTHS['fr_short'][month_idx]} {year}", 'dt:date:fr_short'),
            (f"{MONTHS['fr'][month_idx]} {day}, {year}", 'dt:date:fr_short_monthfirst'),
            (f"{MONTHS['fr_lc'][month_idx]} {day}, {year}", 'dt:date:fr_short_lc_monthfirst'),
        ]
        
        if random.random() < 0.2:
            weekday_idx = dt.weekday()
            patterns.append((f"{WEEKDAYS['fr'][weekday_idx]}, {day} {MONTHS['fr'][month_idx]} {year}", 'dt:date:fr_weekday'))
        
        dates.append(random.choice(patterns))
    
    return dates


def generate_german_dates(count=800):
    """Generate German date formats."""
    dates = []
    
    for _ in range(count):
        dt = random_date()
        day = dt.day
        month_idx = dt.month - 1
        year = dt.year
        
        patterns = [
            (f"{day} {MONTHS['de'][month_idx]} {year}", 'dt:date:de_base'),
            (f"{day} {MONTHS['de_lc'][month_idx]} {year}", 'dt:date:de_base_lc'),
            (f"{day} {MONTHS['de_short'][month_idx]} {year}", 'dt:date:de_short'),
            (f"{MONTHS['de'][month_idx]} {day}, {year}", 'dt:date:de_rare_1'),
            (f"{MONTHS['de_lc'][month_idx]} {day}, {year}", 'dt:date:de_rare_2'),
            (f"{day}. {MONTHS['de'][month_idx]} {year}", 'dt:date:de_base'),
        ]
        
        if random.random() < 0.2:
            weekday_idx = dt.weekday()
            patterns.append((f"{WEEKDAYS['de'][weekday_idx]}, {day} {MONTHS['de'][month_idx]} {year}", 'dt:date:de_weekday'))
        
        dates.append(random.choice(patterns))
    
    return dates


def generate_russian_dates(count=800):
    """Generate Russian date formats."""
    dates = []
    
    for _ in range(count):
        dt = random_date()
        day = dt.day
        month_idx = dt.month - 1
        year = dt.year
        
        patterns = [
            (f"{day} {MONTHS['ru'][month_idx]} {year}", 'dt:date:date_rus'),
            (f"{day} {MONTHS['ru_lc'][month_idx]} {year}", 'dt:date:date_rus_lc1'),
            (f"{day} {MONTHS['ru'][month_idx]} {year} года", 'dt:date:date_rus2'),
            (f"{day} {MONTHS['ru_lc'][month_idx]} {year} г.", 'dt:date:date_rus_lc2'),
            (f"{MONTHS['ru_orig'][month_idx]} {day}, {year}", 'dt:date:rus_rare_5'),
            (f"{day}.{MONTHS['ru_lc'][month_idx]}.{year}", 'dt:date:rus_rare_3'),
            (f"{day}/{MONTHS['ru_lc'][month_idx]}/{year}", 'dt:date:date_rus_lc1'),
        ]
        
        if random.random() < 0.2:
            weekday_idx = dt.weekday()
            patterns.append((f"{WEEKDAYS['ru'][weekday_idx]}, {day} {MONTHS['ru'][month_idx]} {year}", 'dt:date:weekday_rus'))
        
        dates.append(random.choice(patterns))
    
    return dates


def generate_italian_dates(count=600):
    """Generate Italian date formats."""
    dates = []
    
    for _ in range(600):
        dt = random_date()
        day = dt.day
        month_idx = dt.month - 1
        year = dt.year
        
        patterns = [
            (f"{day} {MONTHS['it'][month_idx]} {year}", 'dt:date:it_base'),
            (f"{day} {MONTHS['it_lc'][month_idx]} {year}", 'dt:date:it_base_lc'),
            (f"{MONTHS['it'][month_idx]} {day}, {year}", 'dt:date:it_rare_1'),
            (f"{MONTHS['it_lc'][month_idx]} {day}, {year}", 'dt:date:it_rare_2'),
            (f"{day} de {MONTHS['it'][month_idx]} de {year}", 'dt:date:it_base_article'),
            (f"{day} de {MONTHS['it_lc'][month_idx]} de {year}", 'dt:date:it_base_lc_article'),
        ]
        
        dates.append(random.choice(patterns))
    
    return dates


def generate_portuguese_dates(count=600):
    """Generate Portuguese date formats."""
    dates = []
    
    for _ in range(count):
        dt = random_date()
        day = dt.day
        month_idx = dt.month - 1
        year = dt.year
        
        patterns = [
            (f"{day} de {MONTHS['pt'][month_idx]} de {year}", 'dt:date:pt_base_article'),
            (f"{day} de {MONTHS['pt_lc'][month_idx]} de {year}", 'dt:date:pt_base_lc_article'),
            (f"{day} {MONTHS['pt'][month_idx]} {year}", 'dt:date:pt_base'),
            (f"{day} {MONTHS['pt_lc'][month_idx]} {year}", 'dt:date:pt_base_lc'),
            (f"{MONTHS['pt'][month_idx]} {day}, {year}", 'dt:date:pt_short_monthfirst'),
            (f"{MONTHS['pt_lc'][month_idx]} {day}, {year}", 'dt:date:pt_short_lc_monthfirst'),
        ]
        
        dates.append(random.choice(patterns))
    
    return dates


def generate_other_language_dates(count=600):
    """Generate dates in Bulgarian, Czech, Polish, Dutch, Turkish."""
    dates = []
    
    languages = ['bg', 'cz', 'pl', 'nl', 'tr']
    
    for _ in range(count):
        dt = random_date()
        day = dt.day
        month_idx = dt.month - 1
        year = dt.year
        lang = random.choice(languages)
        
        if lang == 'bg':
            patterns = [
                (f"{day} {MONTHS['bg'][month_idx]} {year}", 'dt:date:bg_base'),
                (f"{day} {MONTHS['bg_lc'][month_idx]} {year}", 'dt:date:bg_base_lc'),
            ]
        elif lang == 'cz':
            patterns = [
                (f"{day} {MONTHS['cz'][month_idx]} {year}", 'dt:date:cz_base'),
                (f"{day} {MONTHS['cz_lc'][month_idx]} {year}", 'dt:date:cz_base_lc'),
            ]
        elif lang == 'pl':
            patterns = [
                (f"{day} {MONTHS['pl'][month_idx]} {year}", 'dt:date:pl_base'),
                (f"{day} {MONTHS['pl_lc'][month_idx]} {year}", 'dt:date:pl_base_lc'),
            ]
        elif lang == 'nl':
            patterns = [
                (f"{day} {MONTHS['nl'][month_idx]} {year}", 'dt:date:nl_base'),
                (f"{day} {MONTHS['nl_lc'][month_idx]} {year}", 'dt:date:nl_base_lc'),
            ]
        elif lang == 'tr':
            patterns = [
                (f"{day} {MONTHS['tr'][month_idx]} {year}", 'dt:date:tr_base'),
                (f"{day} {MONTHS['tr_lc'][month_idx]} {year}", 'dt:date:tr_base_lc'),
            ]
        
        dates.append(random.choice(patterns))
    
    return dates


def generate_datetime_strings(count=1500):
    """Generate datetime strings with time components."""
    dates = []
    
    for _ in range(count):
        dt = random_date()
        day = dt.day
        month_idx = dt.month - 1
        year = dt.year
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        second = random.randint(0, 59) if random.random() < 0.5 else None
        
        # Numeric datetime formats (with time, pattern key is same as date pattern)
        if random.random() < 0.4:
            if second:
                time_str = f"{hour:02d}:{minute:02d}:{second:02d}"
            else:
                time_str = f"{hour:02d}:{minute:02d}"
            
            date_formats = [
                (f"{day:02d}.{month_idx+1:02d}.{year} {time_str}", 'dt:date:date_2'),
                (f"{day:02d}/{month_idx+1:02d}/{year} {time_str}", 'dt:date:date_1'),
                (f"{day:02d}-{month_idx+1:02d}-{year} {time_str}", 'dt:date:date_iso8601'),
                (f"{year}-{month_idx+1:02d}-{day:02d} {time_str}", 'dt:date:date_9'),
                (f"{year}-{month_idx+1:02d}-{day:02d} - {time_str}", 'dt:date:date_9'),
            ]
            dates.append(random.choice(date_formats))
        else:
            # Text-based datetime formats
            if second:
                time_str = f"{hour:02d}:{minute:02d}:{second:02d}"
            else:
                time_str = f"{hour:02d}:{minute:02d}"
            
            lang = random.choice(['en', 'es', 'fr', 'de', 'ru'])
            
            if lang == 'en':
                patterns = [
                    (f"{day} {MONTHS['en'][month_idx]} {year} {time_str}", 'dt:date:date_eng1x'),
                    (f"{day} {MONTHS['en_short'][month_idx]} {year} {time_str}", 'dt:date:date_eng1_short'),
                    (f"{MONTHS['en'][month_idx]} {day}, {year} {time_str}", 'dt:date:date_eng3_nolc'),
                ]
            elif lang == 'es':
                patterns = [
                    (f"{day} de {MONTHS['es'][month_idx]} de {year} {time_str}", 'dt:date:es_base_article'),
                ]
            elif lang == 'fr':
                patterns = [
                    (f"{day} {MONTHS['fr'][month_idx]} {year} {time_str}", 'dt:date:fr_base'),
                ]
            elif lang == 'de':
                patterns = [
                    (f"{day} {MONTHS['de'][month_idx]} {year} {time_str}", 'dt:date:de_base'),
                ]
            elif lang == 'ru':
                patterns = [
                    (f"{day} {MONTHS['ru'][month_idx]} {year} {time_str}", 'dt:date:date_rus'),
                    (f"{day} {MONTHS['ru'][month_idx]} в {time_str}", 'dt:date:date_rus'),
                ]
            
            dates.append(random.choice(patterns))
    
    return dates


def generate_edge_cases(count=500):
    """Generate edge cases and special formats."""
    dates = []
    
    # Edge dates
    edge_dates = [
        datetime(1900, 1, 1),
        datetime(2000, 1, 1),
        datetime(2024, 12, 31),
        datetime(2030, 12, 31),
        datetime(1999, 12, 31),
        datetime(2001, 1, 1),
    ]
    
    for _ in range(count):
        if random.random() < 0.3:
            dt = random.choice(edge_dates)
        else:
            dt = random_date()
        
        day = dt.day
        month_idx = dt.month - 1
        year = dt.year
        
        # Special formats (pattern keys approximate - these may match multiple patterns)
        patterns = [
            (f"{day:02d}{month_idx+1:02d}{year}", 'dt:date:date_2'),  # DDMMYYYY - compact format
            (f"{year}{month_idx+1:02d}{day:02d}", 'dt:date:date_9'),  # YYYYMMDD - ISO compact
            (f"{day}/{month_idx+1}/{year} Hello people", 'dt:date:date_1'),  # With text after
            (f"{day}.{month_idx+1}.{year} [11:23]", 'dt:date:date_2'),  # With brackets
            (f"{day} {MONTHS['en'][month_idx]} {year}:", 'dt:date:date_eng1x'),  # With colon
            (f"{day} {MONTHS['en'][month_idx]} {year} | 11:08", 'dt:date:date_eng1x'),  # With pipe
            (f"{day} / {month_idx+1} '{year%100:02d}", 'dt:date:date_8'),  # With apostrophe
            (f"{day:02d}.{month_idx+1:02d}.{year} 14:53:12", 'dt:date:date_2'),  # Full datetime
        ]
        
        dates.append(random.choice(patterns))
    
    return dates


def main():
    """Generate CSV file with test data."""
    print("Generating test data...")
    
    all_dates = []
    
    # Generate different types of dates
    print("  - Numeric dates...")
    all_dates.extend(generate_numeric_dates(2000))
    
    print("  - English dates...")
    all_dates.extend(generate_english_dates(1500))
    
    print("  - Spanish dates...")
    all_dates.extend(generate_spanish_dates(800))
    
    print("  - French dates...")
    all_dates.extend(generate_french_dates(800))
    
    print("  - German dates...")
    all_dates.extend(generate_german_dates(800))
    
    print("  - Russian dates...")
    all_dates.extend(generate_russian_dates(800))
    
    print("  - Italian dates...")
    all_dates.extend(generate_italian_dates(600))
    
    print("  - Portuguese dates...")
    all_dates.extend(generate_portuguese_dates(600))
    
    print("  - Other language dates...")
    all_dates.extend(generate_other_language_dates(600))
    
    print("  - Datetime strings...")
    all_dates.extend(generate_datetime_strings(1500))
    
    print("  - Edge cases...")
    all_dates.extend(generate_edge_cases(500))
    
    # Shuffle to mix patterns
    random.shuffle(all_dates)
    
    # Ensure we have at least 10,000
    if len(all_dates) < 10000:
        print(f"  - Adding more numeric dates to reach 10,000...")
        additional = generate_numeric_dates(10000 - len(all_dates))
        all_dates.extend(additional)
    
    # Remove duplicates while preserving order (based on date string only)
    seen = set()
    unique_dates = []
    for date_tuple in all_dates:
        date_str, pattern_key = date_tuple
        if date_str not in seen:
            seen.add(date_str)
            unique_dates.append(date_tuple)
    
    # If we lost too many, add more
    if len(unique_dates) < 10000:
        print(f"  - Adding more dates after deduplication...")
        formats_with_keys = [
            ('%d/%m/%Y', 'dt:date:date_1'),
            ('%d.%m.%Y', 'dt:date:date_2'),
            ('%Y-%m-%d', 'dt:date:date_9'),
            ('%m/%d/%Y', 'dt:date:date_usa'),
        ]
        while len(unique_dates) < 10000:
            dt = random_date()
            fmt, pattern_key = random.choice(formats_with_keys)
            date_str = dt.strftime(fmt)
            if date_str not in seen:
                seen.add(date_str)
                unique_dates.append((date_str, pattern_key))
    
    # Write to CSV
    output_file = Path(__file__).parent / 'test_data.csv'
    print(f"\nWriting {len(unique_dates)} dates to {output_file}...")
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['date_string', 'pattern_key'])  # Header
        for date_str, pattern_key in unique_dates:
            writer.writerow([date_str, pattern_key])
    
    print(f"✓ Generated {len(unique_dates)} unique date/datetime strings")
    print(f"✓ Saved to {output_file}")


if __name__ == '__main__':
    main()

