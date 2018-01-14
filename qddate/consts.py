# -*- coding: utf-8 -*-
from pyparsing import Word, nums, alphas, oneOf, lineStart, lineEnd, Optional, restOfLine, Literal, ParseException, CaselessLiteral


EN_NUMERIC_SUFFIXES = ['nd', 'rd', 'th', 'st']
PAT_EN_DAY_NUMERIC = Word(nums, min=1, max=2).setResultsName('day') + oneOf(EN_NUMERIC_SUFFIXES).suppress()

BASE_DATE_PATTERNS = {
    'pat:date:d.m'  : Word(nums, exact=2) + Literal('.').suppress() + Word(nums, exact=2),
    'pat:date:d/m/yyyy': Word(nums, min=1, max=2).setResultsName('day') + Literal('/').suppress() + Word(nums, min=1, max=2).setResultsName('month') + Literal('/').suppress() + Word(nums, exact=4).setResultsName('year'),
    'pat:date:m/d/yy'  : Word(nums, min=1, max=2).setResultsName('month') + Literal('/').suppress() + Word(nums, min=1, max=2).setResultsName('day') + Literal('/').suppress() + Word(nums, exact=2).setResultsName('year'),
    'pat:date:d/m/yy'  : Word(nums, min=1, max=2).setResultsName('day') + Literal('/').suppress() + Word(nums, min=1, max=2).setResultsName('month') + Literal('/').suppress() + Word(nums, exact=2).setResultsName('year'),
    'pat:date:d.m.yyyy': Word(nums, min=1, max=2).setResultsName('day') + Literal('.').suppress() + Word(nums, min=1, max=2).setResultsName('month') + Literal('.').suppress() + Word(nums, exact=4).setResultsName('year'),
    'pat:date:yyyy/m/d': Word(nums, exact=4).setResultsName('year') + '/' + Word(nums, min=1, max=2).setResultsName('month') + '/' + Word(nums, min=1, max=2).setResultsName('day'),
    'pat:date:d.m.yy'  : Word(nums, min=1, max=2).setResultsName('day') + Literal('.').suppress() + Word(nums, min=1, max=2).setResultsName('month') + Literal('.').suppress() + Word(nums, exact=2).setResultsName('year'),
    'pat:date:d-m-yy': Word(nums, min=1, max=2).setResultsName('day') + Literal('-').suppress() + Word(nums, min=1, max=2).setResultsName('month') + Literal('-').suppress() + Word(nums, exact=2).setResultsName('year'),
    'pat:date:d-m-yyyy': Word(nums, min=1, max=2).setResultsName('day') + Literal('-').suppress() + Word(nums, min=1, max=2).setResultsName('month') + Literal('-').suppress() + Word(nums, exact=4).setResultsName('year'),
    'pat:date:yyyy-m-d': Word(nums, exact=4).setResultsName('year') + Literal('-').suppress() + Word(nums, min=1, max=2).setResultsName('month') + Literal('-').suppress() + Word(nums, min=1, max=2).setResultsName('day'),
    'pat:date:yyyy.m.d': Word(nums, exact=4).setResultsName('year') + Literal('.').suppress() + Word(nums, min=1, max=2).setResultsName('month') + Literal('.').suppress() + Word(nums, min=1, max=2).setResultsName('day'),
    'pat:date:ddmmyyyy': Word(nums, exact=2).setResultsName('day') + Word(nums, exact=2).setResultsName('month') + Word(nums, exact=4).setResultsName('year'),
    'pat:date:mmyyyy'  : Word(nums, exact=2).setResultsName('month') + Word(nums, exact=4).setResultsName('year'),
    'pat:date:yyyymmdd': Word(nums, exact=4).setResultsName('year') + Word(nums, exact=2).setResultsName('month') + Word(nums, exact=2).setResultsName('day'),
    'pat:date:mm/dd/yyyy': Word(nums, min=1, max=2).setResultsName('month') + Literal('/').suppress() + Word(nums, min=1, max=2).setResultsName('day') + Literal('/').suppress() + Word(nums, exact=4).setResultsName('year'),

    # Rare patterns
    'pat:date:d/m yy': Word(nums, min=1, max=2).setResultsName('day') + Literal('/').suppress() + Word(nums, min=1, max=2).setResultsName('month') + Literal('‘').suppress() + Word(nums, exact=2).setResultsName('year'),
    }

BASE_TIME_PATTERNS = {
    'pat:time:minutes':  Word(nums, exact=2).setResultsName('hour') + Literal(':').suppress() + Word(nums, exact=2).setResultsName('minute'),
    'pat:time:full': Word(nums, exact=2).setResultsName('hour') + Literal(':').suppress() + Word(nums, exact=2).setResultsName('minute') + Literal(':').suppress() + Word(nums, exact=2).setResultsName('second'),
    }


RUS_MONTHS_ORIG = [u'Январь', u'Февраль', u'Март', u'Апрель', u'Май', u'Июнь', u'Июль', u'Август', u'Сентябрь', u'Октябрь', u'Ноябрь', u'Декабрь']
RUS_MONTHS_ORIG_LC = [u'январь', u'февраль', u'март', u'апрель', u'май', u'июнь', 'июль', u'август', u'сентябрь', u'октябрь', u'ноябрь', u'декабрь']
RUS_MONTHS = [u'Января', u'Февраля', u'Марта', u'Апреля', u'Мая', u'Июня', u'Июля', u'Августа', u'Сентября', u'Октября', u'Ноября', u'Декабря']
RUS_MONTHS_LC = [u'января', u'февраля', u'марта', u'апреля', u'мая', u'июня', u'июля', u'августа', u'сентября', u'октября', u'ноября', u'декабря']
RUS_WEEKDAYS = [u'Понедельник', u'Вторник', u'Среда', u'Четверг', u'Пятница', u'Суббота', u'Воскресение']
RUS_WEEKDAYS_LC = [u'понедельник', u'вторник', u'среда', u'четверг', u'пятница', u'суббота', u'воскресение']
RUS_YEARS = [u'г.', u'года']

ENG_MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
ENG_MONTHS_LC = ['january', 'february', 'march', 'april', 'may', 'june', 'jule', 'august', 'september', 'october', 'november', 'december']
ENG_MONTHS_SHORT = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
ENG_WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Satuday', 'Sunday']
ENG_WEEKDAYS_SHORT = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

FR_MONTHS = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
FR_MONTHS_LC = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']

PT_MONTHS = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
PT_MONTHS_LC = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']

DE_MONTHS = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
DE_MONTHS_LC = ['januar', 'februar', 'märz', 'april', 'mai', 'juni', 'juli', 'august', 'september', 'oktober', 'november', 'dezember']

ES_MONTHS = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
ES_MONTHS_LC = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']

BG_MONTHS = ['Янyapи', 'Фeвpyapи', 'Мapт', 'Апpил', 'Май', 'Юни', 'Юли', 'Авгycт', 'Сeптeмвpи', 'Октoмвpи', 'Нoeмвpи', 'Дeкeмвpи']
BG_MONTHS_LC = ['янyapи', 'фeвpyapи', 'мapт', 'aпpил', 'май', 'юни', 'юли', 'aвгycт', 'ceптeмвpи', 'oктoмвpи', 'нoeмвpи', 'дeкeмвpи']


CZ_WEEKDAYS  = ['Pondělí', 'Úterý', 'Středa', 'Čtvrtek', 'Pátek', 'Sobota', 'Neděle']
CZ_WEEKDAYS_LC  = ['pondělí', 'úterý', 'středa', 'čtvrtek', 'pátek', 'sobota', 'neděle']
CZ_MONTHS = ['Leden', 'Únor', 'Březen', 'Duben', 'Květen', 'Červen', 'Červenec', 'Srpen', 'Září', 'Říjen', 'Listopad', 'Prosinec']
CZ_MONTHS_LC = ['leden', 'únor', 'březen', 'duben', 'květen', 'červen', 'červenec', 'srpen', 'září', 'říjen', 'listopad', 'prosinec']

IT_WEEKDAYS = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']
IT_WEEKDAYS_LC = ['lunedì', 'martedì', 'mercoledì', 'giovedì', 'venerdì', 'sabato', 'domenica']


# English months map
en_mname2mon = dict((m,i+1) for i,m in enumerate(ENG_MONTHS) if m)
ensh_mname2mon = dict((m,i+1) for i,m in enumerate(ENG_MONTHS_SHORT) if m)
enlc_mname2mon = dict((m,i+1) for i,m in enumerate(ENG_MONTHS_LC) if m)
ensh_wday2weekday = dict((m,i+1) for i,m in enumerate(ENG_WEEKDAYS_SHORT) if m)

# French months map
fr_mname2mon = dict((m,i+1) for i,m in enumerate(FR_MONTHS) if m)
frlc_mname2mon = dict((m,i+1) for i,m in enumerate(FR_MONTHS_LC) if m)

# Portugal months map
pt_mname2mon = dict((m,i+1) for i,m in enumerate(PT_MONTHS) if m)
ptlc_mname2mon = dict((m,i+1) for i,m in enumerate(PT_MONTHS_LC) if m)

# German months map
de_mname2mon = dict((m,i+1) for i,m in enumerate(DE_MONTHS) if m)
delc_mname2mon = dict((m,i+1) for i,m in enumerate(DE_MONTHS_LC) if m)

# Spanish months map
es_mname2mon = dict((m,i+1) for i,m in enumerate(ES_MONTHS) if m)
eslc_mname2mon = dict((m,i+1) for i,m in enumerate(ES_MONTHS_LC) if m)

# Bulgarian months map
bg_mname2mon = dict((m,i+1) for i,m in enumerate(BG_MONTHS) if m)
bglc_mname2mon = dict((m,i+1) for i,m in enumerate(BG_MONTHS_LC) if m)

# Czech months map
cz_mname2mon = dict((m,i+1) for i,m in enumerate(CZ_MONTHS) if m)
czlc_mname2mon = dict((m,i+1) for i,m in enumerate(CZ_MONTHS_LC) if m)

# Russian months map
ru_mname2mon = dict((m,i+1) for i,m in enumerate(RUS_MONTHS) if m)
rulc_mname2mon = dict((m,i+1) for i,m in enumerate(RUS_MONTHS_LC) if m)
ru_origmname2mon = dict((m,i+1) for i,m in enumerate(RUS_MONTHS_ORIG) if m)
rulc_origmname2mon = dict((m,i+1) for i,m in enumerate(RUS_MONTHS_ORIG_LC) if m)

BASE_TEXT_PATTERNS = {
    'pat:rus:years'   : oneOf(RUS_YEARS),
    'pat:eng:months'   : oneOf(ENG_MONTHS).setParseAction(lambda t: en_mname2mon[t[0]]),
    'pat:eng:months:lc'   : oneOf(ENG_MONTHS_LC).setParseAction(lambda t: enlc_mname2mon[t[0]]),
    'pat:eng:months:short'   : oneOf(ENG_MONTHS_SHORT, caseless=True).setParseAction(lambda t: ensh_mname2mon[t[0].lower()]),
    'pat:eng:weekdays': oneOf(ENG_WEEKDAYS),
    'pat:eng:weekdays:short': oneOf(ENG_WEEKDAYS_SHORT, caseless=True).setParseAction(lambda t: ensh_wday2weekday[t[0].lower()]),
    'pat:rus:months'   : oneOf(RUS_MONTHS).setParseAction(lambda t: ru_mname2mon[t[0]]),
    'pat:rus:months:lc'   : oneOf(RUS_MONTHS_LC).setParseAction(lambda t: rulc_mname2mon[t[0]]),
    'pat:rus:weekdays': oneOf(RUS_WEEKDAYS),
    'pat:rus:weekdays_lc': oneOf(RUS_WEEKDAYS_LC),
    # Original months names, very rarely in use
    'pat:rus:monthsorig'   : oneOf(RUS_MONTHS_ORIG).setParseAction(lambda t: ru_origmname2mon[t[0]]),
    'pat:rus:monthsorig:lc'   : oneOf(RUS_MONTHS_ORIG_LC).setParseAction(lambda t: rulc_origmname2mon[t[0]]),

    'pat:fr:months'   : oneOf(FR_MONTHS).setParseAction(lambda t: fr_mname2mon[t[0]]),
    'pat:fr:months_lc'   : oneOf(FR_MONTHS_LC).setParseAction(lambda t: frlc_mname2mon[t[0]]),

    'pat:pt:months'   : oneOf(PT_MONTHS).setParseAction(lambda t: pt_mname2mon[t[0]]),
    'pat:pt:months_lc'   : oneOf(PT_MONTHS_LC).setParseAction(lambda t: ptlc_mname2mon[t[0]]),

    'pat:de:months'   : oneOf(DE_MONTHS).setParseAction(lambda t: de_mname2mon[t[0]]),
    'pat:de:months_lc'   : oneOf(DE_MONTHS_LC).setParseAction(lambda t: delc_mname2mon[t[0]]),

    'pat:es:months'   : oneOf(ES_MONTHS).setParseAction(lambda t: es_mname2mon[t[0]]),
    'pat:es:months_lc'   : oneOf(ES_MONTHS_LC).setParseAction(lambda t: eslc_mname2mon[t[0]]),

    'pat:bg:months'   : oneOf(BG_MONTHS).setParseAction(lambda t: bg_mname2mon[t[0]]),
    'pat:bg:months_lc'   : oneOf(BG_MONTHS_LC).setParseAction(lambda t: bglc_mname2mon[t[0]]),


    'pat:cz:weekdays': oneOf(CZ_WEEKDAYS),
    'pat:cz:weekdays_lc': oneOf(CZ_WEEKDAYS_LC),

    'pat:cz:months'   : oneOf(CZ_MONTHS).setParseAction(lambda t: cz_mname2mon[t[0]]),
    'pat:cz:months_lc'   : oneOf(CZ_MONTHS_LC).setParseAction(lambda t: czlc_mname2mon[t[0]]),


    #u'((J|j)(ANUARY|anuary)|(F|f)(EBRUARY|ebruary)|(M|m)(art|ART)|(A|a)(PRIL|pril)|(M|m)(ay|AY)|(J|j)(une|UNE)|(J|j)(ule|ULE)|(A|a)(ugust|UGUST)|(S|s)(eptember|EPTEMBER)|(O|o)(ctober|CTOBER)|(N|n)(ovember|OVEMBER)|(D|d)(ecember|ECEMBER))',
    #u'((J|j)(AN|an)|(F|f)(EB|eb)|(M|m)(ar|AR)|(A|a)(PR|pr)|(M|m)(ay|AY)|(J|j)(un|UN)|(J|j)(ul|UL)|(A|a)(ug|UG)|(S|s)(ep|EP)|(O|o)(ct|CT)|(N|n)(ov|OV)|(D|d)(ec|EC))',
    #'pat:rus:months'   : u'((Я|я)нвар(я|ь)|(ф|Ф)еврал(я|ь)|(М|м)арт(|а)|(А|а)прел(я|ь)|(М|м)а(й|я)|(И|и)юн(ь|я)|(И|и)юл(ь|я)|(А|а)вгуста|(С|с)ентябр(ь|я)|(О|о)ктябр(ь|я)|(Н|н)оябр(ь|я)|(Д|д)екабр(ь|я))',
}

BASE_RE_PATTERNS = {}
BASE_RE_PATTERNS.update(BASE_DATE_PATTERNS)
BASE_RE_PATTERNS.update(BASE_TIME_PATTERNS)
BASE_RE_PATTERNS.update(BASE_TEXT_PATTERNS)

DATE_DATA_TYPES_RAW = [
# Universal patterns
    {'key':'dt:date:date_1', 'name': 'Datetime string', 'pattern': BASE_RE_PATTERNS['pat:date:d/m/yyyy'], 'length': {'min': 8, 'max': 10}, 'format': "%d/%m/%Y"},
    {'key':'dt:date:date_2', 'name': 'Datetime string', 'pattern': BASE_RE_PATTERNS['pat:date:d.m.yyyy'], 'length': {'min': 8, 'max': 10}, 'format': "%d.%m.%Y"},
    {'key': 'dt:date:date_3', 'name': 'Datetime string', 'pattern': BASE_RE_PATTERNS['pat:date:yyyy/m/d'], 'length': {'min': 8, 'max': 10}, 'format': "%Y/%m/%d"},
    {'key': 'dt:date:date_4', 'name': 'Datetime string', 'pattern': BASE_RE_PATTERNS['pat:date:d.m.yy'], 'length': {'min': 6, 'max': 8}, 'format': "%d.%m.%y", 'yearshort': True},
    {'key': 'dt:date:date_iso8601', 'name': 'ISO 8601 date', 'pattern': BASE_RE_PATTERNS['pat:date:d-m-yyyy'], 'length': {'min': 8, 'max': 10}, 'format': "%d-%m-%Y"},
    {'key': 'dt:date:date_iso8601_short', 'name': 'ISO 8601 date shorted', 'pattern': BASE_RE_PATTERNS['pat:date:d-m-yy'], 'length': {'min': 6, 'max': 8}, 'format': "%d-%m-%Y", 'yearshort': True},
    {'key': 'dt:date:date_5', 'name': 'Datetime string as ddmmyyyy', 'pattern': BASE_RE_PATTERNS['pat:date:ddmmyyyy'], 'length': {'min': 8, 'max': 8}, 'format': "%d%m%Y"},
    {'key': 'dt:date:date_6', 'name': 'Datetime string as yyyymmdd', 'pattern': BASE_RE_PATTERNS['pat:date:yyyymmdd'], 'length': {'min': 8, 'max': 8}, 'format': "%Y%m%d"},
    {'key': 'dt:date:date_7', 'name': 'Year-month string', 'pattern': BASE_RE_PATTERNS['pat:date:mmyyyy'], 'length': {'min': 6, 'max': 6}, 'format': "%m.%Y"},
    {'key': 'dt:date:date_8', 'name': 'Date with 2-digits year', 'pattern': BASE_RE_PATTERNS['pat:date:d/m/yy'], 'length': {'min': 6, 'max': 8}, 'format': "%d/%m/%y", 'yearshort': True},
    {'key': 'dt:date:date_9', 'name': 'Date as ISO', 'pattern': BASE_RE_PATTERNS['pat:date:yyyy-m-d'], 'length': {'min': 6, 'max': 10}, 'format': "%Y-%m-%d"},
    {'key': 'dt:date:date_10', 'name': 'Date as yyyy.mm.dd', 'pattern': BASE_RE_PATTERNS['pat:date:yyyy.m.d'], 'length': {'min': 6, 'max': 10}, 'format': "%Y.%m.%d"},


# USA patterns
    {'key': 'dt:date:date_usa_1', 'name': 'Date with 2-digits year', 'pattern': BASE_RE_PATTERNS['pat:date:m/d/yy'], 'length': {'min': 6, 'max': 8}, 'format': "%m/%d/%y", 'yearshort': True},
    {'key': 'dt:date:date_usa', 'name': 'USA mm/dd/yyyy string', 'pattern': BASE_RE_PATTERNS['pat:date:mm/dd/yyyy'], 'length': {'min': 8, 'max': 10}, 'format': "%m/%d/%Y"},


# Russian patterns
    {'key': 'dt:date:date_rus', 'name': 'Date with russian month', 'pattern': Word(nums, min=1, max=2).setResultsName('day') + Optional(',').suppress() + BASE_RE_PATTERNS['pat:rus:months'].setResultsName('month') + Optional(',').suppress() + Word(nums, exact=4).setResultsName('year'), 'length': {'min': 11, 'max': 20}, 'format': "%d %m %Y", 'filter': 1},
    {'key': 'dt:date:date_rus2', 'name': 'Date with russian month and year word', 'pattern': Word(nums, min=1, max=2).setResultsName('day') + Optional(',').suppress() + BASE_RE_PATTERNS['pat:rus:months'].setResultsName('month') + Optional(',').suppress() + Word(nums, exact=4).setResultsName('year') + Optional(BASE_RE_PATTERNS['pat:rus:years']).suppress(), 'length': {'min': 13, 'max': 20}, 'format': "%d %m %Y", 'filter': 1},
    {'key': 'dt:date:date_rus3', 'name': 'Date with russian year', 'pattern': BASE_RE_PATTERNS['pat:date:d.m.yyyy'] + BASE_RE_PATTERNS['pat:rus:years'].suppress(), 'length': {'min': 14, 'max': 20}, 'format': "%d.%m.%Y"},
    {'key': 'dt:date:date_rus_lc1', 'name': 'Date with russian month', 'pattern': Word(nums, min=1, max=2).setResultsName('day') + Optional(',').suppress() + BASE_RE_PATTERNS['pat:rus:months:lc'].setResultsName('month') + Optional(',').suppress() + Word(nums, exact=4).setResultsName('year'), 'length': {'min': 10, 'max': 20}, 'format': "%d %m %Y", 'filter': 1},
    {'key': 'dt:date:date_rus_lc2', 'name': 'Date with russian month with year word', 'pattern': Word(nums, min=1, max=2).setResultsName('day') + Optional(',').suppress() + BASE_RE_PATTERNS['pat:rus:months:lc'].setResultsName('month') + Word(nums, exact=4).setResultsName('year') + Optional(BASE_RE_PATTERNS['pat:rus:years']).suppress(), 'length': {'min': 13, 'max': 25}, 'format': "%d %m %Y", 'filter': 1},
    {'key': 'dt:date:weekday_rus', 'name': 'Date with russian month and weekday', 'pattern': BASE_RE_PATTERNS['pat:rus:weekdays'] + Optional(',') + Word(nums, min=1, max=2) + BASE_RE_PATTERNS['pat:rus:months'] + Optional(Literal(',')).suppress() + Word(nums, exact=4).setResultsName('year') + BASE_RE_PATTERNS['pat:rus:years'].suppress(), 'length': {'min': 13, 'max': 20}, 'format': "%d %m %Y", 'filter': 1},
    {'key': 'dt:date:weekday_rus_lc1', 'name': 'Date with russian month and weekday', 'pattern': BASE_RE_PATTERNS['pat:rus:weekdays'] + Optional(',') + Word(nums, min=1, max=2) + BASE_RE_PATTERNS['pat:rus:months:lc'] + Optional(Literal(',')).suppress() + Word(nums, exact=4).setResultsName('year') + BASE_RE_PATTERNS['pat:rus:years'].suppress(), 'length': {'min': 13, 'max': 25}, 'format': "%d %m %Y", 'filter': 1},

    {'key': 'dt:date:rare_2', 'name': 'Date with russian month with dots as divider', 'pattern': Word(nums, min=1, max=2).setResultsName('day') + Optional('.').suppress() + BASE_RE_PATTERNS['pat:rus:months'].setResultsName('month') + Optional('.').suppress() + Word(nums, exact=4).setResultsName('year'), 'length': {'min': 11, 'max': 20}, 'format': "%d.%m.%Y", 'filter': 1},
    {'key': 'dt:date:rare_3', 'name': 'Date with russian month with dots as divider with low case months', 'pattern': Word(nums, min=1, max=2).setResultsName('day') + Literal('.').suppress() + BASE_RE_PATTERNS['pat:rus:months:lc'].setResultsName('month') + Literal('.').suppress() + Word(nums, exact=4).setResultsName('year'), 'length': {'min': 11, 'max': 20}, 'format': "%d.%m.%Y", 'filter': 1},

    # Ulster bank format http://group.ulsterbank.com/media/press-releases.ashx
    {'key': 'dt:date:rare_1', 'name': 'Rare pattern 1, special divider', 'pattern': BASE_RE_PATTERNS['pat:date:d/m yy'], 'length': {'min': 6, 'max': 8}, 'format': "%d/%m‘%y", 'yearshort': True},
    {'key': 'dt:date:rare_4', 'name': 'English date with numeric days, months and year', 'pattern': PAT_EN_DAY_NUMERIC + BASE_RE_PATTERNS['pat:eng:months'].setResultsName('month') + Word(nums, exact=4).setResultsName('year') + Optional(':').suppress(), 'length': {'min': 13, 'max': 22}, 'format': "%d %m %Y", 'filter': 1},

    # KHMB Bank http://www.kbhmb.ru/news/
    {'key': 'dt:date:rare_5', 'name': 'Russian date stars with month name', 'pattern':  BASE_RE_PATTERNS['pat:rus:monthsorig'].setResultsName('month') + Word(nums, min=1, max=2).setResultsName('day') + Literal(',').suppress() + Word(nums, exact=4).setResultsName('year'), 'length': {'min': 13, 'max': 22}, 'format': "%d %m %Y", 'filter': 1},

    # Bank Rus format http://www.bankrus.ru/about/info/g1/news
    {'key': 'dt:date:rare_6', 'name': 'Russian date stars with weekday and follows with month name', 'pattern':  BASE_RE_PATTERNS['pat:rus:weekdays_lc'].suppress() + Literal(',').suppress() + BASE_RE_PATTERNS['pat:rus:months:lc'].setResultsName('month') + Word(nums, min=1, max=2).setResultsName('day') + Literal(',').suppress() + Word(nums, exact=4).setResultsName('year'), 'length': {'min': 13, 'max': 22}, 'format': "%d %m %Y", 'filter': 1},

# English patterns
    {'key': 'dt:date:date_eng1', 'name': 'Date with english month', 'pattern': Word(nums, min=1, max=2).setResultsName('day') + Optional('.').suppress() + BASE_RE_PATTERNS['pat:eng:months'].setResultsName('month') + Optional('.').suppress() +  Word(nums, exact=4).setResultsName('year'), 'length': {'min': 10, 'max': 20}, 'format': "%d.%b.%Y"},
    {'key': 'dt:date:date_eng1_lc', 'name': 'Date with english month lowcase', 'pattern': Word(nums, min=1, max=2).setResultsName('day') + Optional('.').suppress() + BASE_RE_PATTERNS['pat:eng:months:lc'].setResultsName('month') + Optional('.').suppress() + Word(nums, exact=4).setResultsName('year'), 'length': {'min': 10, 'max': 20}, 'format': "%d.%b.%Y"},
    {'key': 'dt:date:date_eng1_short', 'name': 'Date with english month short', 'pattern': Word(nums, min=1, max=2).setResultsName('day') + Optional('.').suppress() + BASE_RE_PATTERNS['pat:eng:months:short'].setResultsName('month') + Optional('.').suppress() + Word(nums, exact=4).setResultsName('year'), 'length': {'min': 10, 'max': 10}, 'format': "%d.%b.%Y"},
    {'key': 'dt:date:date_eng2', 'name': 'Date with english month 2', 'pattern': BASE_RE_PATTERNS['pat:eng:months'].setResultsName('month') + Word(nums, min=1, max=2).setResultsName('day') + Optional(',').suppress() + Word(nums, exact=4).setResultsName('year'), 'length': {'min': 10, 'max': 20}, 'format': "%b %d, %Y"},
    {'key': 'dt:date:date_eng2_lc', 'name': 'Date with english month 2 lowcase', 'pattern': BASE_RE_PATTERNS['pat:eng:months:lc'].setResultsName('month') + Word(nums, min=1, max=2).setResultsName('day') + Optional(',').suppress() + Word(nums, exact=4).setResultsName('year'), 'length': {'min': 10, 'max': 20}, 'format': "%b %d, %Y"},
    {'key': 'dt:date:date_eng2_short', 'name': 'Date with english month 2 short', 'pattern': BASE_RE_PATTERNS['pat:eng:months:short'].setResultsName('month') + Word(nums, min=1, max=2).setResultsName('day') + Optional(',').suppress() + Word(nums, exact=4).setResultsName('year'), 'length': {'min': 10, 'max': 10}, 'format': "%b %d, %Y"},
    {'key': 'dt:date:date_eng3', 'name': 'Date with english month full', 'pattern': BASE_RE_PATTERNS['pat:eng:months:lc'].setResultsName('month') + Word(nums, min=1, max=2).setResultsName('day') + Optional(',').suppress() + Word(nums, exact=4).setResultsName('year'), 'length': {'min': 10, 'max': 20}, 'format': "%b %d, %Y", 'filter': 2},
    {'key': 'dt:date:noyear_1', 'name': 'Datetime string without year', 'pattern': BASE_RE_PATTERNS['pat:date:d.m'], 'length': {'min': 5, 'max': 5}, 'format': "%d.%m", 'noyear': True},
    {'key': 'dt:date:date_4_point', 'name': 'Datetime string', 'pattern': BASE_RE_PATTERNS['pat:date:d.m.yy'] + Literal('.').suppress(), 'length': {'min': 6, 'max': 9}, 'format': "%d.%m.%y", 'yearshort': True },
    {'key': 'dt:date:weekday_eng', 'name': 'Date with english month and weekday', 'pattern': BASE_RE_PATTERNS['pat:eng:weekdays'].suppress() + Optional(',').suppress() + Word(nums, min=1, max=2).setResultsName('day') + BASE_RE_PATTERNS['pat:eng:months'].setResultsName('month') + Optional(Literal(',')).suppress() + Word(nums, exact=4).setResultsName('year') , 'length': {'min': 17, 'max': 27}, 'format': "%d %m %Y", 'filter': 1},
    {'key': 'dt:date:weekday_eng_lc', 'name': 'Date with english month and weekday', 'pattern': BASE_RE_PATTERNS['pat:eng:weekdays'].suppress() + Optional(',').suppress() + Word(nums, min=1, max=2).setResultsName('day') + BASE_RE_PATTERNS['pat:eng:months:lc'].setResultsName('month') + Optional(Literal(',')).suppress() + Word(nums, exact=4).setResultsName('year'), 'length': {'min': 17, 'max': 27}, 'format': "%d %m %Y", 'filter': 1},
    {'key': 'dt:date:weekday_eng_wshort', 'name': 'Date with english month and weekday', 'pattern': BASE_RE_PATTERNS['pat:eng:weekdays:short'].suppress() + Optional(',').suppress() + Word(nums, min=1, max=2).setResultsName('day') + BASE_RE_PATTERNS['pat:eng:months'].setResultsName('month') + Optional(Literal(',')).suppress() + Word(nums, exact=4).setResultsName('year') , 'length': {'min': 16, 'max': 27}, 'format': "%d %m %Y", 'filter': 1},
    {'key': 'dt:date:weekday_eng_mshort_wshort', 'name': 'Date with short english month and short weekday', 'pattern': BASE_RE_PATTERNS['pat:eng:weekdays:short'].suppress()  + Word(nums, min=1, max=2).setResultsName('day') + BASE_RE_PATTERNS['pat:eng:months:short'].setResultsName('month') + Word(nums, exact=4).setResultsName('year') , 'length': {'min': 15, 'max': 15}, 'format': "%d %m %Y", 'filter': 1},
    {'key': 'dt:date:weekday_eng_iso', 'name': 'Date with english weekday and iso date', 'pattern': BASE_RE_PATTERNS['pat:eng:weekdays'].suppress() + Optional(',').suppress() + BASE_RE_PATTERNS['pat:date:d/m/yyyy'] , 'length': {'min': 13, 'max': 25}, 'format': "%d/%m/%Y", 'filter': 1},
    {'key': 'dt:date:weekday_short_eng_iso', 'name': 'Date with english short weekday and iso date', 'pattern': BASE_RE_PATTERNS['pat:eng:weekdays:short'].suppress() + Optional(',').suppress() + BASE_RE_PATTERNS['pat:date:d/m/yyyy'] , 'length': {'min': 13, 'max': 18}, 'format': "%d/%m/%Y", 'filter': 1},

# French patterns
    {'key': 'dt:date:fr_base', 'name': 'Base french date with month name not archive', 'pattern':  Word(nums, min=1, max=2).setResultsName('day') + BASE_RE_PATTERNS['pat:fr:months'].setResultsName('month') +  Word(nums, exact=4).setResultsName('year'), 'length': {'min': 11, 'max': 22}, 'format': "%d %m %Y", 'filter': 1},
    {'key': 'dt:date:fr_base_lc', 'name': 'Base french date with month name and lowcase, no article', 'pattern':  Word(nums, min=1, max=2).setResultsName('day') + BASE_RE_PATTERNS['pat:fr:months_lc'].setResultsName('month') +  Word(nums, exact=4).setResultsName('year'), 'length': {'min': 11, 'max': 22}, 'format': "%d %m %Y", 'filter': 1},
    {'key': 'dt:date:fr_base_article', 'name': 'Base french date with month name and articles', 'pattern':  CaselessLiteral('Le').suppress() + Word(nums, min=1, max=2).setResultsName('day') + BASE_RE_PATTERNS['pat:fr:months'].setResultsName('month') +  Word(nums, exact=4).setResultsName('year'), 'length': {'min': 11, 'max': 22}, 'format': "%d %m %Y", 'filter': 1},
    {'key': 'dt:date:fr_base_lc_article', 'name': 'Base french date with month name and articles and lowcase', 'pattern':  CaselessLiteral('le').suppress() + Word(nums, min=1, max=2).setResultsName('day') + BASE_RE_PATTERNS['pat:fr:months_lc'].setResultsName('month') +  Word(nums, exact=4).setResultsName('year'), 'length': {'min': 11, 'max': 22}, 'format': "%d %m %Y", 'filter': 1},

# Portugal patterns
    {'key': 'dt:date:pt_base', 'name': 'Base portugal date with month name not article', 'pattern':  Word(nums, min=1, max=2).setResultsName('day') + BASE_RE_PATTERNS['pat:pt:months'].setResultsName('month') +  Word(nums, exact=4).setResultsName('year'), 'length': {'min': 11, 'max': 22}, 'format': "%d %m %Y", 'filter': 1},
    {'key': 'dt:date:pt_base_lc', 'name': 'Base portugal date with month name and lowcase, no article', 'pattern':  Word(nums, min=1, max=2).setResultsName('day') + BASE_RE_PATTERNS['pat:pt:months_lc'].setResultsName('month') +  Word(nums, exact=4).setResultsName('year'), 'length': {'min': 11, 'max': 22}, 'format': "%d %m %Y", 'filter': 1},
    {'key': 'dt:date:pt_base_article', 'name': 'Base portugal date with month name and articles', 'pattern':  Word(nums, min=1, max=2).setResultsName('day') + CaselessLiteral('de').suppress() + BASE_RE_PATTERNS['pat:pt:months'].setResultsName('month') +  CaselessLiteral('de').suppress() + Word(nums, exact=4).setResultsName('year'), 'length': {'min': 11, 'max': 26}, 'format': "%d %m %Y", 'filter': 1},
    {'key': 'dt:date:pt_base_lc_article', 'name': 'Base portugal date with month name and articles and lowcase', 'pattern': Word(nums, min=1, max=2).setResultsName('day') + CaselessLiteral("de").suppress() + BASE_RE_PATTERNS['pat:pt:months_lc'].setResultsName('month') + CaselessLiteral("de").suppress() +  Word(nums, exact=4).setResultsName('year'), 'length': {'min': 11, 'max': 26}, 'format': "%d %m %Y", 'filter': 1},

# German patterns
    {'key': 'dt:date:de_base', 'name': 'Base german date with month name', 'pattern':  Word(nums, min=1, max=2).setResultsName('day') + Optional('.').suppress() + BASE_RE_PATTERNS['pat:de:months'].setResultsName('month') +  Word(nums, exact=4).setResultsName('year'), 'length': {'min': 11, 'max': 22}, 'format': "%d %m %Y", 'filter': 1},
    {'key': 'dt:date:de_base_lc', 'name': 'Base german date with month name and lowcase', 'pattern':  Word(nums, min=1, max=2).setResultsName('day') + Optional('.').suppress() + BASE_RE_PATTERNS['pat:de:months_lc'].setResultsName('month') +  Word(nums, exact=4).setResultsName('year'), 'length': {'min': 11, 'max': 22}, 'format': "%d %m %Y", 'filter': 1},

# Bulgarian patterns
    {'key': 'dt:date:bg_base', 'name': 'Base bulgarian date with month name', 'pattern':  Word(nums, min=1, max=2).setResultsName('day') + BASE_RE_PATTERNS['pat:bg:months'].setResultsName('month') +  Word(nums, exact=4).setResultsName('year'), 'length': {'min': 11, 'max': 22}, 'format': "%d %m %Y", 'filter': 1},
    {'key': 'dt:date:bg_base_lc', 'name': 'Base bulgarian date with month name and lowcase', 'pattern':  Word(nums, min=1, max=2).setResultsName('day') + BASE_RE_PATTERNS['pat:bg:months_lc'].setResultsName('month') +  Word(nums, exact=4).setResultsName('year'), 'length': {'min': 11, 'max': 22}, 'format': "%d %m %Y", 'filter': 1},


# Spanish patterns
    {'key': 'dt:date:es_base', 'name': 'Base spanish date with month name not article', 'pattern':  Word(nums, min=1, max=2).setResultsName('day') + BASE_RE_PATTERNS['pat:es:months'].setResultsName('month') +  Word(nums, exact=4).setResultsName('year'), 'length': {'min': 11, 'max': 22}, 'format': "%d %m %Y", 'filter': 1},
    {'key': 'dt:date:es_base_lc', 'name': 'Base spanish date with month name and lowcase, no article', 'pattern':  Word(nums, min=1, max=2).setResultsName('day') + BASE_RE_PATTERNS['pat:es:months_lc'].setResultsName('month') +  Word(nums, exact=4).setResultsName('year'), 'length': {'min': 11, 'max': 22}, 'format': "%d %m %Y", 'filter': 1},
    {'key': 'dt:date:es_base_article', 'name': 'Base spanish date with month name and articles', 'pattern':  Word(nums, min=1, max=2).setResultsName('day') + CaselessLiteral('de').suppress() + BASE_RE_PATTERNS['pat:es:months'].setResultsName('month') +  CaselessLiteral('de').suppress() + Word(nums, exact=4).setResultsName('year'), 'length': {'min': 11, 'max': 26}, 'format': "%d %m %Y", 'filter': 1},
    {'key': 'dt:date:es_base_lc_article', 'name': 'Base spanish date with month name and articles and lowcase', 'pattern': Word(nums, min=1, max=2).setResultsName('day') + CaselessLiteral("de").suppress() + BASE_RE_PATTERNS['pat:es:months_lc'].setResultsName('month') + CaselessLiteral("de").suppress() +  Word(nums, exact=4).setResultsName('year'), 'length': {'min': 11, 'max': 26}, 'format': "%d %m %Y", 'filter': 1},


    ]

