from __future__ import annotations

import hashlib
import json

from ..consts import consts


def get_cache() -> dict:
    path = consts.dir / "user_files" / "transcriptions.json"
    if not path.exists():
        with open(path, "w", encoding="utf-8") as file:
            file.write("{}")
    with open(path, encoding="utf-8") as file:
        return json.load(file)


def write_cache(cache: dict) -> None:
    path = consts.dir / "user_files" / "transcriptions.json"
    with open(path, "w", encoding="utf-8") as file:
        json.dump(cache, file, ensure_ascii=False)


def get_cached_transcription(provider: str, lang: str, filename: str) -> str | None:
    with open(filename, "rb") as file:
        digest = hashlib.sha256(
            file.read() + lang.encode() + provider.encode()
        ).hexdigest()
        cache = get_cache()
        return cache.get(digest, None)


def cache_transcription(
    provider: str, lang: str, filename: str, transcription: str
) -> None:
    with open(filename, "rb") as file:
        digest = hashlib.sha256(
            file.read() + lang.encode() + provider.encode()
        ).hexdigest()
        cache = get_cache()
        cache[digest] = transcription
        write_cache(cache)
