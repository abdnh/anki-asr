from __future__ import annotations

from abc import ABC, abstractmethod

from .cache import cache_transcription, get_cached_transcription


class ASRProvider(ABC):
    name: str

    def __init__(self, config: dict) -> None:
        self.config = config
        super().__init__()

    def transcribe(self, filename: str, lang: str) -> str:
        transcription = get_cached_transcription(filename)
        if not transcription:
            transcription = self._transcribe(filename, lang)
            cache_transcription(filename, transcription)
        return transcription

    @abstractmethod
    def _transcribe(self, filename: str, lang: str) -> str:
        raise NotImplementedError()

    @property
    @abstractmethod
    def languages(self) -> list[tuple[str, str]]:
        """Return a list containing tuples of (language_id, language_name) pairs for languages supported  by the provider."""
        return []
