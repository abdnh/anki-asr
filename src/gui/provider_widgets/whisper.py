from __future__ import annotations

from aqt.qt import *

from ...providers.whisper import Whisper
from .provider_widget import ProviderWidget


class WhisperWidget(ProviderWidget[Whisper]):
    def __init__(self, parent: QWidget, provider: Whisper):
        super().__init__(parent, provider)
        self._setup()

    def _setup(self) -> None:
        layout = QFormLayout(self)
        self.setLayout(layout)

        self.api_key = QLineEdit(self)
        self.api_key.setText(self.provider.config.api_key)
        qconnect(self.api_key.textChanged, self.on_api_changed)
        layout.addRow("API Key", self.api_key)

    def on_api_changed(self, api: str) -> None:
        self.provider.config.api_key = api
