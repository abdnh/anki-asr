from __future__ import annotations

from typing import Any, Type

from .deepgram import Deepgram
from .provider import ASRProvider
from .whisper import Whisper

PROVIDERS = [Deepgram, Whisper]


def init_provider(
    config: dict[str, Any], provider_class: Type[ASRProvider]
) -> ASRProvider:
    return provider_class(
        config.get("provider_options", {}).get(provider_class.name, {})
    )


def get_provider(name: str) -> Type[ASRProvider] | None:
    name = name.lower()
    for provider_class in PROVIDERS:
        if provider_class.name == name:
            return provider_class
    return None
