from __future__ import annotations

from typing import Type

from ...providers.provider import Provider
from .deepgram import Deepgram, DeepgramWidget
from .provider_widget import ProviderWidget
from .whisper import Whisper, WhisperWidget

PROVIDER_WIDGETS: dict[type[Provider], type[ProviderWidget]] = {
    Deepgram: DeepgramWidget,
    Whisper: WhisperWidget,
}
