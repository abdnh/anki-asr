from __future__ import annotations

from aqt.qt import *

from ...providers.deepgram import Deepgram
from ..lineedit import LineEditWithSuggestions
from .provider_widget import ProviderWidget


class DeepgramWidget(ProviderWidget[Deepgram]):
    def __init__(self, parent: QWidget, provider: Deepgram):
        super().__init__(parent, provider)
        self._setup()

    def _setup(self) -> None:
        layout = QFormLayout(self)
        self.setLayout(layout)

        self.api_key = QLineEdit(self)
        self.api_key.setText(self.provider.config.api_key)
        qconnect(self.api_key.textChanged, self.on_api_changed)
        layout.addRow("API Key", self.api_key)

        self.tier = LineEditWithSuggestions(self, ["nova", "enhanced", "base"])
        self.tier.setText(self.provider.config.tier)
        qconnect(self.tier.textChanged, self.on_tier_changed)
        layout.addRow("Tier", self.tier)

        self.model = LineEditWithSuggestions(
            self,
            [
                "general",
                "whisper",
                "whisper-tiny",
                "whisper-base",
                "whisper-small",
                "whisper-medium",
                "whisper-large",
                "meeting",
                "phonecall",
                "finance",
                "voicemail",
                "conversationalai",
                "video",
            ],
        )
        self.model.setText(self.provider.config.model)
        qconnect(self.model.textChanged, self.on_model_changed)
        layout.addRow("Model", self.model)

    def on_api_changed(self, api: str) -> None:
        self.provider.config.api_key = api

    def on_tier_changed(self, tier: str) -> None:
        self.provider.config.tier = tier

    def on_model_changed(self, model: str) -> None:
        self.provider.config.model = model
