# -*- coding: utf-8 -*-
"""Canonical month-name table for every supported language.

This module is the **single source of truth** for month-name lists and the
``month → int`` mapping that the parser and language-detection logic both
read from. Per-language modules in ``qddate/patterns/<lang>.py`` re-export
the names they need (``LANG_MONTHS``, ``LANG_MONTHS_LC``, ``lang_mname2mon``,
``langabbrev_mname2mon``) so existing tests and downstream consumers continue
to work unchanged.

Adding a new language now means appending a single ``LanguageMonths`` entry to
``MONTHS_BY_LANGUAGE`` — no separate edits to ``qdparser.py`` and no risk of
the detection list drifting from the pattern list.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional, Tuple


@dataclass(frozen=True)
class LanguageMonths:
    """Month-name data for one language.

    Every list is exactly 12 elements long and indexed 1–12 in calendar
    order. ``genitive`` (Russian/Ukrainian/Polish/Czech) carries the
    grammatical case used after a numeric day, e.g. ``3 января``;
    languages without a separate genitive form leave it ``None``.

    ``detect_excludes`` lists tokens that are shared with another supported
    language (e.g. Romanian ``mai`` is the Portuguese ``mai``; ``august``
    is also a valid English/Dutch/German month). These tokens are still
    full parse targets, but the language-detection heuristic skips them
    so an unrestricted parser doesn't relabel a non-Romanian text as
    Romanian just because it contains one ambiguous token.
    """

    code: str
    full: Tuple[str, ...]
    full_lc: Tuple[str, ...]
    abbrev: Tuple[str, ...]
    abbrev_lc: Tuple[str, ...]
    genitive: Optional[Tuple[str, ...]] = None
    genitive_lc: Optional[Tuple[str, ...]] = None
    short: Optional[Tuple[str, ...]] = None
    short_lc: Optional[Tuple[str, ...]] = None
    detect_excludes: Tuple[str, ...] = ()

    @property
    def month_to_int(self) -> Mapping[str, int]:
        """Return a combined dict mapping every variant → month integer (1–12).

        Excludes ``genitive``/``short`` variants if absent; otherwise they're
        folded in. The mapping is recomputed each call (cheap: 60-ish items
        in the worst case) and is intentionally a plain ``dict`` for fast
        pyparsing ``one_of(...)`` lookups.
        """
        out: dict[str, int] = {}
        for src in (self.full, self.full_lc, self.abbrev, self.abbrev_lc):
            for i, name in enumerate(src, 1):
                out[name] = i
        for opt_src in (self.genitive, self.genitive_lc, self.short, self.short_lc):
            if opt_src is not None:
                for i, name in enumerate(opt_src, 1):
                    out[name] = i
        return out

    def variant_counts(self) -> dict[str, int]:
        """How many entries each variant contributes. For testing/debugging."""
        return {
            "full": len(self.full),
            "full_lc": len(self.full_lc),
            "abbrev": len(self.abbrev),
            "abbrev_lc": len(self.abbrev_lc),
            "genitive": 0 if self.genitive is None else len(self.genitive),
            "genitive_lc": 0 if self.genitive_lc is None else len(self.genitive_lc),
            "short": 0 if self.short is None else len(self.short),
            "short_lc": 0 if self.short_lc is None else len(self.short_lc),
        }


# ---------------------------------------------------------------------------
# Canonical table. Order of variants in each tuple is calendar (Jan, Feb, ...).
# ---------------------------------------------------------------------------

MONTHS_BY_LANGUAGE: Mapping[str, LanguageMonths] = {
    "en": LanguageMonths(
        code="en",
        full=("January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"),
        full_lc=("january", "february", "march", "april", "may", "june",
                 "july", "august", "september", "october", "november", "december"),
        abbrev=("Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"),
        abbrev_lc=("jan", "feb", "mar", "apr", "may", "jun",
                   "jul", "aug", "sep", "oct", "nov", "dec"),
        short=("Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"),
        short_lc=("jan", "feb", "mar", "apr", "may", "jun",
                  "jul", "aug", "sep", "oct", "nov", "dec"),
    ),
    "ru": LanguageMonths(
        code="ru",
        full=("Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
              "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"),
        full_lc=("январь", "февраль", "март", "апрель", "май", "июнь",
                 "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь"),
        abbrev=("Янв.", "Февр.", "Мар.", "Апр.", "Май", "Июн.",
                "Июл.", "Авг.", "Сент.", "Окт.", "Нояб.", "Дек."),
        abbrev_lc=("янв.", "февр.", "мар.", "апр.", "май", "июн.",
                   "июл.", "авг.", "сент.", "окт.", "нояб.", "дек."),
        genitive=("Января", "Февраля", "Марта", "Апреля", "Мая", "Июня",
                  "Июля", "Августа", "Сентября", "Октября", "Ноября", "Декабря"),
        genitive_lc=("января", "февраля", "марта", "апреля", "мая", "июня",
                      "июля", "августа", "сентября", "октября", "ноября", "декабря"),
    ),
    "de": LanguageMonths(
        code="de",
        full=("Januar", "Februar", "März", "April", "Mai", "Juni",
              "Juli", "August", "September", "Oktober", "November", "Dezember"),
        full_lc=("januar", "februar", "märz", "april", "mai", "juni",
                 "juli", "august", "september", "oktober", "november", "dezember"),
        abbrev=("Jan", "Feb", "Mär", "Apr", "Mai", "Jun",
                "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"),
        abbrev_lc=("jan", "feb", "mär", "apr", "mai", "jun",
                   "jul", "aug", "sep", "okt", "nov", "dez"),
    ),
    "fr": LanguageMonths(
        code="fr",
        full=("Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
              "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"),
        full_lc=("janvier", "février", "mars", "avril", "mai", "juin",
                 "juillet", "août", "septembre", "octobre", "novembre", "décembre"),
        abbrev=("Janv", "Févr", "Mars", "Avr", "Mai", "Juin",
                "Juil", "Août", "Sept", "Oct", "Nov", "Déc"),
        abbrev_lc=("janv", "févr", "mars", "avr", "mai", "juin",
                   "juil", "août", "sept", "oct", "nov", "déc"),
    ),
    "es": LanguageMonths(
        code="es",
        full=("Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
              "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"),
        full_lc=("enero", "febrero", "marzo", "abril", "mayo", "junio",
                 "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"),
        abbrev=("Ene", "Feb", "Mar", "Abr", "May", "Jun",
                "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"),
        abbrev_lc=("ene", "feb", "mar", "abr", "may", "jun",
                   "jul", "ago", "sep", "oct", "nov", "dic"),
    ),
    "it": LanguageMonths(
        code="it",
        full=("Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
              "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"),
        full_lc=("gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
                 "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"),
        abbrev=("Gen", "Feb", "Mar", "Apr", "Mag", "Giu",
                "Lug", "Ago", "Set", "Ott", "Nov", "Dic"),
        abbrev_lc=("gen", "feb", "mar", "apr", "mag", "giu",
                   "lug", "ago", "set", "ott", "nov", "dic"),
    ),
    "nl": LanguageMonths(
        code="nl",
        full=("Januari", "Februari", "Maart", "April", "Mei", "Juni",
              "Juli", "Augustus", "September", "Oktober", "November", "December"),
        full_lc=("januari", "februari", "maart", "april", "mei", "juni",
                 "juli", "augustus", "september", "oktober", "november", "december"),
        abbrev=("Jan", "Feb", "Mrt", "Apr", "Mei", "Jun",
                "Jul", "Aug", "Sep", "Okt", "Nov", "Dec"),
        abbrev_lc=("jan", "feb", "mrt", "apr", "mei", "jun",
                   "jul", "aug", "sep", "okt", "nov", "dec"),
    ),
    "pt": LanguageMonths(
        code="pt",
        full=("Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
              "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"),
        full_lc=("janeiro", "fevereiro", "março", "abril", "maio", "junho",
                 "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"),
        abbrev=("Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                "Jul", "Ago", "Set", "Out", "Nov", "Dez"),
        abbrev_lc=("jan", "fev", "mar", "abr", "mai", "jun",
                   "jul", "ago", "set", "out", "nov", "dez"),
    ),
    "pl": LanguageMonths(
        code="pl",
        full=("Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec",
              "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień"),
        full_lc=("styczeń", "luty", "marzec", "kwiecień", "maj", "czerwiec",
                 "lipiec", "sierpień", "wrzesień", "październik", "listopad", "grudzień"),
        abbrev=("Sty", "Lut", "Mar", "Kwi", "Maj", "Cze",
                "Lip", "Sie", "Wrz", "Paź", "Lis", "Gru"),
        abbrev_lc=("sty", "lut", "mar", "kwi", "maj", "cze",
                   "lip", "sie", "wrz", "paź", "lis", "gru"),
        genitive=("Stycznia", "Lutego", "Marca", "Kwietnia", "Maja", "Czerwca",
                  "Lipca", "Sierpnia", "Września", "Października", "Listopada", "Grudnia"),
        genitive_lc=("stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca",
                      "lipca", "sierpnia", "września", "października", "listopada", "grudnia"),
    ),
    "cz": LanguageMonths(
        code="cz",
        full=("Leden", "Únor", "Březen", "Duben", "Květen", "Červen",
              "Červenec", "Srpen", "Září", "Říjen", "Listopad", "Prosinec"),
        full_lc=("leden", "únor", "březen", "duben", "květen", "červen",
                 "červenec", "srpen", "září", "říjen", "listopad", "prosinec"),
        # Czech doesn't have a separate abbreviation set in the legacy code;
        # the disambiguation between "Červen" (June) and "Červenec" (July)
        # is done via the full names only. ``abbrev`` is therefore empty.
        abbrev=(),
        abbrev_lc=(),
        genitive=("Ledna", "Února", "Března", "Dubna", "Května", "Června",
                  "Července", "Srpna", "Září", "Října", "Listopadu", "Prosince"),
        genitive_lc=("ledna", "února", "března", "dubna", "května", "června",
                      "července", "srpna", "září", "října", "listopadu", "prosince"),
    ),
    "ro": LanguageMonths(
        code="ro",
        full=("Ianuarie", "Februarie", "Martie", "Aprilie", "Mai", "Iunie",
              "Iulie", "August", "Septembrie", "Octombrie", "Noiembrie", "Decembrie"),
        full_lc=("ianuarie", "februarie", "martie", "aprilie", "mai", "iunie",
                 "iulie", "august", "septembrie", "octombrie", "noiembrie", "decembrie"),
        abbrev=("Ian.", "Feb.", "Mar.", "Apr.", "Mai", "Iun.",
                "Iul.", "Aug.", "Sept.", "Oct.", "Nov.", "Dec."),
        abbrev_lc=("ian.", "feb.", "mar.", "apr.", "mai", "iun.",
                   "iul.", "aug.", "sept.", "oct.", "nov.", "dec."),
        # Romanian "mai" and "august" overlap with Portuguese / English /
        # Dutch / German. Excluded from language detection so an unrestricted
        # parser doesn't relabel ambiguous text as Romanian; the patterns
        # still parse these tokens correctly when ``languages="ro"`` is set.
        detect_excludes=("Mai", "mai", "August", "august"),
    ),
    "uk": LanguageMonths(
        code="uk",
        full=("Січень", "Лютий", "Березень", "Квітень", "Травень", "Червень",
              "Липень", "Серпень", "Вересень", "Жовтень", "Листопад", "Грудень"),
        full_lc=("січень", "лютий", "березень", "квітень", "травень", "червень",
                 "липень", "серпень", "вересень", "жовтень", "листопад", "грудень"),
        abbrev=("Січ.", "Лют.", "Бер.", "Квіт.", "Трав.", "Черв.",
                "Лип.", "Серп.", "Вер.", "Жовт.", "Листоп.", "Груд."),
        abbrev_lc=("січ.", "лют.", "бер.", "квіт.", "трав.", "черв.",
                   "лип.", "серп.", "вер.", "жовт.", "листоп.", "груд."),
        genitive=("Січня", "Лютого", "Березня", "Квітня", "Травня", "Червня",
                  "Липня", "Серпня", "Вересня", "Жовтня", "Листопада", "Грудня"),
        genitive_lc=("січня", "лютого", "березня", "квітня", "травня", "червня",
                      "липня", "серпня", "вересня", "жовтня", "листопада", "грудня"),
    ),
    "tr": LanguageMonths(
        code="tr",
        full=("Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
              "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"),
        full_lc=("ocak", "şubat", "mart", "nisan", "mayıs", "haziran",
                 "temmuz", "ağustos", "eylül", "ekim", "kasım", "aralık"),
        abbrev=("Oca", "Şub", "Mar", "Nis", "May", "Haz",
                "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"),
        abbrev_lc=("oca", "şub", "mar", "nis", "may", "haz",
                   "tem", "ağu", "eyl", "eki", "kas", "ara"),
    ),
    "bg": LanguageMonths(
        code="bg",
        full=("Януари", "Февруари", "Март", "Април", "Май", "Юни",
              "Юли", "Август", "Септември", "Октомври", "Ноември", "Декември"),
        full_lc=("януари", "февруари", "март", "април", "май", "юни",
                 "юли", "август", "септември", "октомври", "ноември", "декември"),
        abbrev=("Ян.", "Фев.", "Мар.", "Апр.", "Мая", "Юни",
                "Юли", "Авг.", "Сеп.", "Окт.", "Ное.", "Дек."),
        abbrev_lc=("ян.", "фев.", "мар.", "апр.", "мая", "юни",
                   "юли", "авг.", "сеп.", "окт.", "ное.", "дек."),
    ),
}


def get_months(code: str) -> LanguageMonths:
    """Return the ``LanguageMonths`` for ``code`` or raise ``ValueError``."""
    if code not in MONTHS_BY_LANGUAGE:
        raise ValueError(
            f"Unknown language code {code!r}; expected one of {sorted(MONTHS_BY_LANGUAGE)}"
        )
    return MONTHS_BY_LANGUAGE[code]
