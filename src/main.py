from __future__ import annotations

import html
import json
import os
import re
import sys
from concurrent.futures import Future
from dataclasses import dataclass
from re import Match
from typing import Any

from anki import hooks
from anki.cards import Card
from anki.collection import Collection, OpChanges
from anki.template import TemplateRenderContext
from aqt import gui_hooks, mw
from aqt.browser.previewer import Previewer
from aqt.clayout import CardLayout
from aqt.editor import Editor
from aqt.operations import CollectionOp
from aqt.qt import *
from aqt.qt import QAction, QApplication, QKeySequence, qconnect
from aqt.utils import showText, showWarning
from aqt.webview import AnkiWebView

sys.path.append(os.path.join(os.path.dirname(__file__), "vendor"))

from .consts import consts
from .gui.tasklist import TasklistDialog

try:
    from aqt.browser.browser import Browser
except ImportError:
    from aqt.browser import Browser

from .config import config
from .gui.transcribe import TranscribeDialog
from .providers import get_provider, init_provider

SOUND_RE = re.compile(r"\[sound:(.*?)\]")


@dataclass
class CardContext:
    card: Card | None = None
    web: AnkiWebView | None = None


def get_active_card_context() -> CardContext:
    dialog = QApplication.activeModalWidget()
    if isinstance(dialog, CardLayout):
        return CardContext(dialog.rendered_card, dialog.preview_web)
    window = QApplication.activeWindow()
    if isinstance(window, Previewer):
        # pylint: disable=protected-access
        return CardContext(window.card(), window._web)
    return CardContext(mw.reviewer.card, mw.reviewer.web)


def get_bool_option(options: dict, name: str, default: bool) -> bool:
    val = options.get(name, "true" if default else "false").lower()
    return val == "true"


def format_filter_error(msg: str) -> str:
    return (
        f"<div style='color: red'>{consts.name} add-on error: {html.escape(msg)}</div>"
    )


def on_field_filter(
    field_text: str, field_name: str, filter_name: str, ctx: TemplateRenderContext
) -> str:
    if not filter_name.startswith("asr"):
        return field_text
    filter_parts = filter_name.split()
    options = dict(opt.split("=") for opt in filter_parts[1:])
    provider_name = options.get("provider", "deepgram")

    if "-" in filter_parts[0]:
        subfilter = filter_parts[0].split("-", maxsplit=1)[1]
        if subfilter == "langs":
            provider_class = get_provider(options["provider"])
            if not provider_class:
                return format_filter_error(f'Unrecognized provider: "{provider_name}"')
            langs = provider_class.languages()
            formatted_langs = ""
            for lang_tuple in langs:
                formatted_langs += f"{lang_tuple}<br>"
            return formatted_langs

    lang = options.get("lang", "en")
    auto = get_bool_option(options, "auto", True)
    idx = 0

    def repl(match: Match) -> str:
        filename = match.group(1)
        path = os.path.join(mw.col.media.dir(), filename)
        if not os.path.exists(path):
            return ""
        nonlocal idx
        idx += 1
        msg = {
            "cmd": "transcribe",
            "lang": lang,
            "provider": provider_name,
            "filename": path,
            "cid": ctx.card().id,
            "idx": idx - 1,
        }
        cmd = json.dumps(f"{consts.module}:{json.dumps(msg)}")
        if auto:
            return f"<div class='asr'>Transcribing audio...<br><script>pycmd({cmd})</script></div>"
        return f"""<div class='asr'><button title='Transcribe {filename}' onclick='var div = document.createElement("div"); div.textContent = "Transcribing audio..."; event.currentTarget.parentElement.appendChild(div); pycmd({cmd}); return false;'>Transcribe audio ({idx})</button></div>"""

    return SOUND_RE.sub(repl, field_text)


def handle_js_message(
    handled: tuple[bool, Any], message: str, context: Any
) -> tuple[bool, Any]:
    cmd, *args = message.split(":", maxsplit=1)
    if cmd != consts.module:
        return handled
    options = json.loads(args[0])
    card_context = get_active_card_context()

    if options["cmd"] == "transcribe":
        lang = options["lang"]
        filename = options["filename"]
        idx = options["idx"]
        cid = int(options["cid"])
        provider_class = get_provider(options["provider"])
        if not provider_class:
            card_context.web.eval(
                """
                (() => {
                    const asr = document.getElementsByClassName('asr')[%d];
                    asr.style.color = 'red';
                    asr.textContent = 'Unrecognized provider: "%s"';
                })();
            """
                % (idx, options["provider"])
            )
            return (True, None)

        provider = init_provider(provider_class)

        def on_done(fut: Future) -> None:
            try:
                result = fut.result()
            except Exception as exc:
                showWarning(str(exc), title=consts.name)
                return
            if card_context.card and card_context.web and card_context.card.id == cid:
                card_context.web.eval(
                    """
                    (() => {
                        document.getElementsByClassName('asr')[%d].textContent = %s;
                    })();
                """
                    % (idx, json.dumps(result))
                )

        provider.transcribe_in_background(filename, lang, mw.taskman, on_done)

    return (True, None)


def on_editor_button(editor: Editor) -> None:
    dialog = TranscribeDialog(mw, editor.widget, [editor.note])
    if dialog.exec():
        editor.loadNoteKeepingFocus()
    if dialog.errors:
        showWarning("\n".join(dialog.errors), editor.widget, title=consts.name)


def add_editor_button(buttons: list[str], editor: Editor) -> None:
    shortcut = config["editor_shortcut"]
    shortcut_desc = (
        f" ({QKeySequence(shortcut).toString(QKeySequence.SequenceFormat.NativeText)})"
        if shortcut
        else ""
    )
    buttons.append(
        editor.addButton(
            icon=str(consts.dir / "icons" / "icon.svg"),
            cmd=f"{consts.module}_editor",
            func=on_editor_button,
            tip=f"Transcribe {shortcut_desc}",
            keys=config["editor_shortcut"],
        )
    )


def on_browser_action(browser: Browser) -> None:
    notes = [mw.col.get_note(nid) for nid in browser.selected_notes()]
    if not notes:
        return
    dialog = TranscribeDialog(mw, browser, notes)
    if dialog.exec():

        def op(col: Collection) -> OpChanges:
            undo_entry = col.add_custom_undo_entry("Audio Transcription")
            col.update_notes(dialog.updated_notes)
            return col.merge_undo_entries(undo_entry)

        def on_success(_: OpChanges) -> None:
            if dialog.errors:
                text = (
                    "The following errors happened when trying to transcribe some files:\n<ul>"
                    + "".join(f"<li>{error}</li>" for error in dialog.errors)
                    + "</ul>"
                )
                showText(text, browser, title=consts.name, type="rich")

        CollectionOp(browser, op=op).success(on_success).run_in_background(
            initiator=browser
        )


def add_browser_action(browser: Browser) -> None:
    action = QAction("Transcribe selected", browser)
    action.setShortcut(config["browser_shortcut"])
    qconnect(action.triggered, lambda: on_browser_action(browser))
    browser.form.menu_Notes.addAction(action)


tasklist_dialog: TasklistDialog | None = None


def on_task_list() -> None:
    global tasklist_dialog
    tasklist_dialog = TasklistDialog(mw)
    tasklist_dialog.show()


def add_main_menu() -> None:
    menu = QMenu(consts.name, mw)
    tasklist_action = QAction("Transcribed Files", menu)
    qconnect(tasklist_action.triggered, on_task_list)
    menu.addAction(tasklist_action)
    mw.form.menuTools.addMenu(menu)


hooks.field_filter.append(on_field_filter)
gui_hooks.webview_did_receive_js_message.append(handle_js_message)
gui_hooks.editor_did_init_buttons.append(add_editor_button)
gui_hooks.browser_menus_did_init.append(add_browser_action)
add_main_menu()
