from __future__ import annotations

from typing import Type

from ..config import config
from .deepgram import Deepgram
from .provider import Provider
from .whisper import Whisper

try:
    from ..user_files.providers import PROVIDERS as USER_PROVIDERS
except ImportError:
    USER_PROVIDERS = []

PROVIDERS: list[type[Provider]] = [Deepgram, Whisper, *USER_PROVIDERS]


def init_provider(provider_class: type[Provider]) -> Provider:
    return provider_class(
        config.get("provider_options", {}).get(provider_class.name, {})
    )


def get_provider(name: str) -> type[Provider] | None:
    name = name.lower()
    for provider_class in PROVIDERS:
        if provider_class.name == name:
            return provider_class
    return None
