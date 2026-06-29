from __future__ import annotations

import unicodedata


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text.casefold())
    without_accents = "".join(
        character for character in normalized if unicodedata.category(character) != "Mn"
    )
    return without_accents.strip()

