from __future__ import annotations

from abc import ABC, abstractmethod
from concurrent.futures import Future
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar

from anki.utils import pointVersion

from .cache import cache_transcription, get_cached_transcription
from .tasklist import tasklist

if TYPE_CHECKING:
    from aqt.taskman import TaskManager


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

    def transcribe_in_background(
        self,
        filename: str,
        lang: str,
        taskman: TaskManager,
        on_done: Callable[[Future], None] | None = None,
    ) -> Future:
        kwargs: dict[str, Any] = dict(
            task=lambda: self.transcribe(filename, lang), on_done=on_done
        )
        if pointVersion() >= 231000:
            kwargs["uses_collection"] = False
        future = taskman.run_in_background(**kwargs)
        tasklist.add_task(filename, future)

        return future

    @abstractmethod
    def _transcribe(self, filename: str, lang: str) -> str:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def languages(cls) -> list[tuple[str, str]]:
        """Return a list containing tuples of (language_id, language_name) pairs for languages supported  by the provider."""
        return []
