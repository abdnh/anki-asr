from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from .cache import cache_transcription, get_cached_transcription


@dataclass
class ProviderConfig:
    pass


T = TypeVar("T", bound=ProviderConfig)


class Provider(Generic[T], ABC):
    name: str
    config_class: type[T]

    def __init__(self, config: dict) -> None:
        self.config = self.config_class(**config)
        super().__init__()

    def transcribe(self, filename: str, lang: str) -> str:
        transcription = get_cached_transcription(self.name, lang, filename)
        if not transcription:
            transcription = self._transcribe(filename, lang)
            cache_transcription(self.name, lang, filename, transcription)
        return transcription

    @abstractmethod
    def _transcribe(self, filename: str, lang: str) -> str:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def languages(cls) -> list[tuple[str, str]]:
        """Return a list containing tuples of (language_id, language_name) pairs for languages supported  by the provider."""
        return []
