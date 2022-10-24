from __future__ import annotations

import asyncio
import mimetypes
import sys

from deepgram import Deepgram as DG

from .provider import ASRProvider

# Work around "RuntimeError: Event loop is closed"
# TODO: Test in Anki 2.1.55+ and remove if the issue is resolved
# Credit: https://github.com/encode/httpx/issues/914#issuecomment-622586610
if sys.platform.startswith("win32"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class Deepgram(ASRProvider):
    name = "deepgram"

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.dg_client = DG(self.config["api_key"])

    def _transcribe(self, filename: str, lang: str) -> str:
        async def get_transcription() -> str:
            mimetype, _ = mimetypes.guess_type(filename)
            with open(filename, "rb") as audio:
                source = {"buffer": audio, "mimetype": mimetype}
                options = {
                    "punctuate": True,
                    "model": "general",
                    "language": lang,
                    "tier": "base",
                }
                response = await self.dg_client.transcription.prerecorded(
                    source, options
                )
                return response["results"]["channels"][0]["alternatives"][0][
                    "transcript"
                ]

        return asyncio.run(get_transcription())
