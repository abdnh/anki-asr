from __future__ import annotations

from typing import Generic, TypeVar

from aqt.qt import QWidget

from ...providers import Provider

T = TypeVar("T", bound=Provider)


class ProviderWidget(QWidget, Generic[T]):
    def __init__(self, parent: QWidget, provider: T) -> None:
        super().__init__(parent)
        self.provider = provider
