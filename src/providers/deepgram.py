from __future__ import annotations

import asyncio
import mimetypes
import sys
from dataclasses import dataclass

from ..utils import contain_imports
from .provider import Provider, ProviderConfig

# Work around "RuntimeError: Event loop is closed"
# TODO: Test in Anki 2.1.55+ and remove if the issue is resolved
# Credit: https://github.com/encode/httpx/issues/914#issuecomment-622586610
if sys.platform.startswith("win32"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@dataclass
class DeepgramConfig(ProviderConfig):
    api_key: str
    model: str = "general"
    tier: str = "base"


class Deepgram(Provider[DeepgramConfig]):
    name = "deepgram"
    config_class = DeepgramConfig

    def _transcribe(self, filename: str, lang: str) -> str:
        with contain_imports():
            from deepgram import Deepgram as DG

            dg_client = DG(self.config.api_key)

            async def get_transcription() -> str:
                mimetype, _ = mimetypes.guess_type(filename)
                with open(filename, "rb") as audio:
                    source = {"buffer": audio, "mimetype": mimetype}
                    options = {
                        "punctuate": True,
                        "model": self.config.model,
                        "language": lang,
                        "tier": self.config.tier,
                    }
                    response = await dg_client.transcription.prerecorded(
                        source, options
                    )
                    return response["results"]["channels"][0]["alternatives"][0][
                        "transcript"
                    ]

            return asyncio.run(get_transcription())

    @classmethod
    def languages(cls) -> list[tuple[str, str]]:
        langs = [
            ("en", "English"),
            ("en-AU", "English (Australia)"),
            ("en-IN", "English (India)"),
            ("en-NZ", "English (New Zealand)"),
            ("en-GB", "English (United Kingdom)"),
            ("en-US", "English (United States)"),
            ("zh-CN", "Simplified Mandarin (China)"),
            ("zh-TW", "Traditional Mandarin (Taiwan)"),
            ("nl", "Dutch"),
            ("fr", "French"),
            ("fr-CA", "French (Canada)"),
            ("de", "German"),
            ("hi", "Hindi"),
            ("hi-Latn", "Hindi (Roman script)"),
            ("id", "Indonesian"),
            ("it", "Italian"),
            ("ja", "Japanese"),
            ("ko", "Korean"),
            ("pl", "Polish"),
            ("pt", "Portuguese"),
            ("pt-BR", "Portuguese (Brazil)"),
            ("pt-PT", "Portuguese (Portugal)"),
            ("ru", "Russian"),
            ("es", "Spanish"),
            ("es-419", "Spanish (Latin America)"),
            ("sv", "Swedish"),
            ("tr", "Turkish"),
            ("uk", "Ukrainian"),
        ]

        return langs
