from __future__ import annotations

import json
import os
import re
import sys
from concurrent.futures import Future
from dataclasses import dataclass
from re import Match

from anki import hooks
from anki.cards import Card
from anki.template import TemplateRenderContext
from aqt import mw
from aqt.browser.previewer import Previewer
from aqt.clayout import CardLayout
from aqt.qt import QApplication
from aqt.webview import AnkiWebView

from . import consts

sys.path.append(str(consts.ADDON_DIR / "vendor"))

from .providers import get_provider

SOUND_RE = re.compile(r"\[sound:(.*?)\]")
CONFIG = mw.addonManager.getConfig(__name__)


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


def on_field_filter(
    field_text: str, field_name: str, filter_name: str, ctx: TemplateRenderContext
) -> str:
    if not filter_name.startswith(consts.FILTER_NAME):
        return field_text
    options = dict(opt.split("=") for opt in filter_name.split()[1:])
    lang = options.get("lang", "en")
    provider_name = options.get("provider", "deepgram")
    provider = get_provider(CONFIG, provider_name)

    idx = 0

    def repl(match: Match) -> str:
        filename = os.path.join(mw.col.media.dir(), match.group(1))
        nonlocal idx
        i = idx

        def on_done(fut: Future) -> None:
            result = fut.result()
            card_context = get_active_card_context()
            if (
                card_context.card
                and card_context.web
                and card_context.card.id == ctx.card().id
            ):
                card_context.web.eval(
                    """
                    (() => {
                        document.getElementsByClassName('asr')[%d].textContent = %s;
                    })();
                """
                    % (i, json.dumps(result))
                )

        mw.taskman.run_in_background(
            lambda: provider.transcribe(filename, lang), on_done
        )
        idx += 1
        return f"<div class='asr'>ASR ({i+1})...<br></div>"

    return SOUND_RE.sub(repl, field_text)


hooks.field_filter.append(on_field_filter)
