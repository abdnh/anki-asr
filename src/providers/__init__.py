from __future__ import annotations

from .deepgram import Deepgram
from .provider import ASRProvider

PROVIDERS = [Deepgram]


def get_provider(config: dict, name: str) -> ASRProvider | None:
    name = name.lower()
    for provider_class in PROVIDERS:
        if provider_class.name == name:
            return provider_class(config.get("provider_options", {}).get(name, {}))
    return None
