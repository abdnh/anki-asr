from __future__ import annotations

import dataclasses
import functools
import time
from concurrent.futures import Future
from typing import Type, cast

from anki.notes import Note
from aqt.main import AnkiQt
from aqt.qt import *
from aqt.utils import showWarning, tooltip

if qtmajor >= 6:
    from ..forms.dialog_qt6 import Ui_Dialog
else:
    from ..forms.dialog_qt5 import Ui_Dialog  # type: ignore

from .. import consts
from ..providers import PROVIDERS, init_provider
from ..providers.provider import Provider
from .provider_widgets import PROVIDER_WIDGETS, ProviderWidget


class TranscribeDialog(QDialog):
    def __init__(self, mw: AnkiQt, parent: QWidget, notes: list[Note]) -> None:
        super().__init__(parent)
        self.mw = mw
        self.notes = notes
        self.updated_notes: list[Note] = []
        self.errors: list[str] = []
        self.config = cast(dict, mw.addonManager.getConfig(__name__))
        self.form = Ui_Dialog()
        self.form.setupUi(self)
        self.provider_class: Type[Provider] = PROVIDERS[0]
        self.provider: Provider = init_provider(self.config, self.provider_class)
        self.provider_widget: ProviderWidget | None = None
        self.lang = self.config["lang_field"]
        self.form.providerOptionsGroup.setLayout(QVBoxLayout())
        qconnect(self.form.provider.currentIndexChanged, self.on_provider_changed)
        provider_names = [provider.name for provider in PROVIDERS]
        self.form.provider.addItems([name.title() for name in provider_names])
        try:
            idx = provider_names.index(self.config["provider_field"])
            self.form.provider.setCurrentIndex(idx)
        except ValueError:
            pass
        qconnect(self.form.lang.currentIndexChanged, self.on_lang_changed)
        qconnect(self.form.addButton.clicked, self.on_add)
        qconnect(self.finished, self.on_finished)
        self.form.addButton.setShortcut("Ctrl+Return")
        self.setWindowTitle(consts.ADDON_NAME)

    def on_provider_changed(self, index: int) -> None:
        self.provider_class = PROVIDERS[index]
        self.provider = init_provider(self.config, self.provider_class)
        self.form.lang.clear()
        for i, (code, name) in enumerate(self.provider_class.languages()):
            self.form.lang.addItem(name, code)
            if self.lang in (code, name):
                self.form.lang.setCurrentIndex(i)
        self.lang = self.form.lang.currentData(Qt.ItemDataRole.UserRole)
        self.load_provider_widget()

    def load_provider_widget(self) -> None:
        while child := self.form.providerOptionsGroup.layout().takeAt(0):
            child.widget().deleteLater()
            del child
        if widget_class := PROVIDER_WIDGETS.get(self.provider_class, None):
            self.form.providerOptionsGroup.setVisible(True)
            self.provider_widget = widget_class(self, self.provider)
            self.form.providerOptionsGroup.layout().addWidget(self.provider_widget)
        else:
            self.form.providerOptionsGroup.setVisible(False)

    def on_lang_changed(self, index: int) -> None:
        self.lang = self.form.lang.currentData(Qt.ItemDataRole.UserRole)

    def exec(self) -> int:
        if self._fill_fields():
            return super().exec()
        return QDialog.DialogCode.Rejected

    def _fill_fields(self) -> bool:
        if len({note.mid for note in self.notes}) != 1:
            showWarning(
                "Please select notes from only one notetype.",
                parent=self,
                title=consts.ADDON_NAME,
            )
            return False

        field_names = self.notes[0].keys()
        self.form.audioField.addItems(field_names)
        self.form.textField.addItems(field_names)
        try:
            idx = field_names.index(self.config["audio_field"])
            self.form.audioField.setCurrentIndex(idx)
        except ValueError:
            pass
        try:
            idx = field_names.index(self.config["text_field"])
            self.form.textField.setCurrentIndex(idx)
        except ValueError:
            self.form.textField.setCurrentIndex(1)

        return True

    def on_finished(self) -> None:
        audio_field = self.form.audioField.currentText()
        text_field = self.form.textField.currentText()
        provider_field = self.form.provider.currentText().lower()
        lang_field = self.form.lang.currentData(Qt.ItemDataRole.UserRole)
        self.config["audio_field"] = audio_field
        self.config["text_field"] = text_field
        self.config["provider_field"] = provider_field
        self.config["lang_field"] = lang_field
        self.config["provider_options"][self.provider_class.name] = dataclasses.asdict(
            self.provider.config
        )
        self.mw.addonManager.writeConfig(__name__, self.config)

    def on_add(self) -> None:
        audio_field = self.form.audioField.currentText()
        text_field = self.form.textField.currentText()
        provider = self.provider
        lang = self.lang
        mid = self.notes[0].mid
        self.mw.progress.start(
            max=len(self.notes), min=0, label="Processing notes...", parent=self
        )
        self.mw.progress.set_title(consts.ADDON_NAME)

        def task() -> None:
            last_progress = 0.0
            want_cancel = False

            def on_progress(i: int) -> None:
                self.mw.progress.update(
                    f"Processed {i+1} out {len(self.notes)} notes", value=i + 1
                )
                nonlocal want_cancel
                want_cancel = self.mw.progress.want_cancel()

            for i, note in enumerate(self.notes):
                filenames = self.mw.col.media.filesInStr(mid, note[audio_field])
                if not filenames:
                    continue
                texts = []
                for filename in filenames:
                    try:
                        texts.append(
                            provider.transcribe(
                                os.path.join(self.mw.col.media.dir(), filename), lang
                            )
                        )
                    except Exception as exc:
                        self.errors.append(
                            f"Failed to transcribe {filename}: {str(exc)}"
                        )
                if texts:
                    note[text_field] = "<br>".join(texts)
                    self.updated_notes.append(note)
                if time.time() - last_progress >= 0.1:
                    self.mw.taskman.run_on_main(functools.partial(on_progress, i=i))
                    last_progress = time.time()
                if want_cancel:
                    return

        def on_done(fut: Future) -> None:
            self.mw.progress.finish()
            fut.result()
            tooltip(
                f"Processed {len(self.updated_notes)} notes", parent=self.parentWidget()
            )
            self.accept()

        self.mw.taskman.run_in_background(task, on_done)
