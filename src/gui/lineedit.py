from __future__ import annotations

from typing import Iterable

from aqt.qt import *


# Credit: adapted from aqt.tagedit
class LineEditWithSuggestions(QLineEdit):
    _completer: QCompleter

    def __init__(self, parent: QWidget, suggestions: Iterable[str]) -> None:
        super().__init__(parent)
        self.model = QStringListModel(suggestions)
        self._completer = QCompleter(self.model, parent)
        self._completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.setCompleter(self._completer)

    def keyPressEvent(self, evt: QKeyEvent) -> None:
        if evt.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down):
            # show completer on arrow key up/down
            if not self._completer.popup().isVisible():
                self.show_completer()
            return
        if (
            evt.key() == Qt.Key.Key_Tab
            and evt.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
            # select next completion
            if not self._completer.popup().isVisible():
                self.show_completer()
            index = self._completer.currentIndex()
            self._completer.popup().setCurrentIndex(index)
            cur_row = index.row()
            if not self._completer.setCurrentRow(cur_row + 1):
                self._completer.setCurrentRow(0)
            return
        if (
            evt.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return)
            and self._completer.popup().isVisible()
        ):
            # apply first completion if no suggestion selected
            selected_row = self._completer.popup().currentIndex().row()
            if selected_row == -1:
                self._completer.setCurrentRow(0)
                index = self._completer.currentIndex()
                self._completer.popup().setCurrentIndex(index)
            self.hide_completer()
            QWidget.keyPressEvent(self, evt)
            return
        super().keyPressEvent(evt)
        if not evt.text():
            # if it's a modifier, don't show
            return
        if evt.key() not in (
            Qt.Key.Key_Enter,
            Qt.Key.Key_Return,
            Qt.Key.Key_Escape,
            Qt.Key.Key_Space,
            Qt.Key.Key_Tab,
            Qt.Key.Key_Backspace,
            Qt.Key.Key_Delete,
        ):
            self.show_completer()

    def show_completer(self) -> None:
        self._completer.setCompletionPrefix(self.text())
        self._completer.complete()

    def focusOutEvent(self, evt: QFocusEvent) -> None:
        super().focusOutEvent(evt)
        self._completer.popup().hide()

    def hide_completer(self) -> None:
        if sip.isdeleted(self._completer):  # type: ignore
            return
        self._completer.popup().hide()
