# -*- coding: utf-8 -*-
"""Short labels a publication date follows, by language.

``DateParser.search(text, labels=True)`` accepts a date that does not start
the text only after one of these labels ("Posted on May 5, 2022",
"Опубликовано: 5 мая 2022", "Veröffentlicht am 5. Mai 2022"), after a
dateline ("GENEVA, 29 July 2022") or after punctuation alone. Labels are
compared case-insensitively, with the colon, dash or bracket after them
removed, so "Updated:" and "UPDATED" match "updated".

Keys are qddate's language codes; ``zh``, ``ja`` and ``ko`` hold the labels of
the Chinese, Japanese and Korean numeric dates, which belong to no language.
"""

DATE_LABELS = {
    "en": (
        "posted", "posted on", "posted at", "published", "published on",
        "published at", "first published", "first published on",
        "originally published", "originally published on",
        "updated", "updated on", "updated at", "last updated", "last updated on",
        "last modified", "modified", "modified on", "created", "created on",
        "date", "dated", "released", "released on", "release date",
        "publication date", "date published", "date posted", "issued",
        "issued on", "as of",
    ),
    "ru": (
        "опубликовано", "опубликован", "опубликована", "обновлено",
        "обновлен", "обновлена", "изменено", "создано", "размещено",
        "дата", "дата публикации", "дата обновления", "дата размещения",
        "последнее обновление", "от",
    ),
    "uk": (
        "опубліковано", "оновлено", "змінено", "створено", "дата",
        "дата публікації", "дата оновлення", "останнє оновлення", "від",
    ),
    "bg": (
        "публикувано", "обновено", "променено", "дата", "дата на публикуване",
    ),
    "de": (
        "veröffentlicht", "veröffentlicht am", "aktualisiert", "aktualisiert am",
        "zuletzt aktualisiert", "zuletzt aktualisiert am", "geändert am",
        "erstellt am", "erschienen", "erschienen am", "datum", "stand", "vom",
    ),
    "fr": (
        "publié", "publié le", "publiée le", "mis en ligne", "mis en ligne le",
        "mis à jour", "mis à jour le",
        "mise à jour", "mise à jour le", "dernière mise à jour", "modifié le",
        "créé le", "date", "date de publication", "le",
    ),
    "es": (
        "publicado", "publicado el", "actualizado", "actualizado el",
        "última actualización", "modificado el", "fecha",
        "fecha de publicación",
    ),
    "it": (
        "pubblicato", "pubblicato il", "aggiornato", "aggiornato il",
        "ultimo aggiornamento", "modificato il", "data",
        "data di pubblicazione",
    ),
    "pt": (
        "publicado", "publicado em", "atualizado", "atualizado em",
        "última atualização", "modificado em", "data",
        "data de publicação",
    ),
    "nl": (
        "gepubliceerd", "gepubliceerd op", "bijgewerkt", "bijgewerkt op",
        "laatst bijgewerkt", "laatst bijgewerkt op", "gewijzigd op", "datum",
    ),
    "pl": (
        "opublikowano", "opublikowano dnia", "zaktualizowano", "aktualizacja",
        "data", "data publikacji", "data aktualizacji", "dnia",
    ),
    "cz": (
        "publikováno", "zveřejněno", "aktualizováno", "aktualizace",
        "datum", "datum zveřejnění", "datum vydání", "dne",
    ),
    "sk": (
        "publikované", "zverejnené", "aktualizované", "aktualizácia",
        "dátum", "dátum zverejnenia", "dňa",
    ),
    "ro": (
        "publicat", "publicat la", "publicat pe", "actualizat",
        "actualizat la", "actualizat pe", "data", "data publicării",
    ),
    "tr": (
        "yayınlandı", "yayınlanma tarihi", "yayın tarihi", "güncellendi",
        "güncelleme", "güncelleme tarihi", "tarih", "oluşturulma tarihi",
    ),
    "zh": (
        "发布时间", "发布于", "发表于", "发布日期", "更新时间", "更新于", "日期",
        "时间", "發佈時間", "發佈於", "發表於", "更新時間",
    ),
    "ja": (
        "公開", "公開日", "投稿", "投稿日", "更新", "更新日", "配信", "配信日",
        "掲載日", "日付", "公開日時", "投稿日時", "更新日時", "最終更新日",
    ),
    "ko": (
        "게시일", "작성일", "등록일", "수정일", "입력", "수정", "기사입력",
        "최종수정", "업데이트", "발행일", "날짜",
    ),
}
