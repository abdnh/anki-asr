"""
This is an example of how to write a custom ASR provider.
Do not forget to add your provider class to the `PROVIDERS` list in user_files/__init__.py
"""

from __future__ import annotations

from dataclasses import dataclass

# pylint: disable=relative-beyond-top-level
from ...providers.provider import Provider, ProviderConfig


@dataclass
class MyProviderConfig(ProviderConfig):
    """Specify config options for your provider here. Options can be configured from provider_options.my_provider in the config screen"""

    api_key: str


class MyProvider(Provider[MyProviderConfig]):
    name = "my_provider"
    config_class = MyProviderConfig

    def _transcribe(self, filename: str, lang: str) -> str:
        """Transcribe `filename` given language `lang`. Config options can be accessed from `self.config`"""
        return "test"

    @classmethod
    def languages(cls) -> list[tuple[str, str]]:
        """Return a list of (language_identifier, language_name) tuples"""
        langs = [
            ("en", "English"),
        ]
        return langs
