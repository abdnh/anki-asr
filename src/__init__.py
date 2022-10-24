from __future__ import annotations

import json
import os
import re
import sys
from concurrent.futures import Future
from re import Match

from anki import hooks
from anki.template import TemplateRenderContext
from aqt import mw

from . import consts

sys.path.append(str(consts.ADDON_DIR / "vendor"))

from .providers import get_provider

SOUND_RE = re.compile(r"\[sound:(.*?)\]")
CONFIG = mw.addonManager.getConfig(__name__)


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
            # TODO: make this work in the previewer/clayout screens too
            if mw.reviewer.card.id == ctx.card().id:
                mw.reviewer.web.eval(
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
