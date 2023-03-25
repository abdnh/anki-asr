from __future__ import annotations

import openai

from .provider import ASRProvider


class Whisper(ASRProvider):
    name = "whisper"

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        openai.api_key = self.config["api_key"]

    def _transcribe(self, filename: str, lang: str) -> str:
        with open(filename, "rb") as file:
            res = openai.Audio.transcribe(
                model="whisper-1", file=file, language=lang, response_format="text"
            )
            return str(res)

    @classmethod
    def languages(cls) -> list[tuple[str, str]]:
        # https://github.com/openai/whisper/blob/main/whisper/tokenizer.py
        langs = [
            ("en", "English"),
            ("zh", "Chinese"),
            ("de", "German"),
            ("es", "Spanish"),
            ("ru", "Russian"),
            ("ko", "Korean"),
            ("fr", "French"),
            ("ja", "Japanese"),
            ("pt", "Portuguese"),
            ("tr", "Turkish"),
            ("pl", "Polish"),
            ("ca", "Catalan"),
            ("nl", "Dutch"),
            ("ar", "Arabic"),
            ("sv", "Swedish"),
            ("it", "Italian"),
            ("id", "Indonesian"),
            ("hi", "Hindi"),
            ("fi", "Finnish"),
            ("vi", "Vietnamese"),
            ("he", "Hebrew"),
            ("uk", "Ukrainian"),
            ("el", "Greek"),
            ("ms", "Malay"),
            ("cs", "Czech"),
            ("ro", "Romanian"),
            ("da", "Danish"),
            ("hu", "Hungarian"),
            ("ta", "Tamil"),
            ("no", "Norwegian"),
            ("th", "Thai"),
            ("ur", "Urdu"),
            ("hr", "Croatian"),
            ("bg", "Bulgarian"),
            ("lt", "Lithuanian"),
            ("la", "Latin"),
            ("mi", "Maori"),
            ("ml", "Malayalam"),
            ("cy", "Welsh"),
            ("sk", "Slovak"),
            ("te", "Telugu"),
            ("fa", "Persian"),
            ("lv", "Latvian"),
            ("bn", "Bengali"),
            ("sr", "Serbian"),
            ("az", "Azerbaijani"),
            ("sl", "Slovenian"),
            ("kn", "Kannada"),
            ("et", "Estonian"),
            ("mk", "Macedonian"),
            ("br", "Breton"),
            ("eu", "Basque"),
            ("is", "Icelandic"),
            ("hy", "Armenian"),
            ("ne", "Nepali"),
            ("mn", "Mongolian"),
            ("bs", "Bosnian"),
            ("kk", "Kazakh"),
            ("sq", "Albanian"),
            ("sw", "Swahili"),
            ("gl", "Galician"),
            ("mr", "Marathi"),
            ("pa", "Punjabi"),
            ("si", "Sinhala"),
            ("km", "Khmer"),
            ("sn", "Shona"),
            ("yo", "Yoruba"),
            ("so", "Somali"),
            ("af", "Afrikaans"),
            ("oc", "Occitan"),
            ("ka", "Georgian"),
            ("be", "Belarusian"),
            ("tg", "Tajik"),
            ("sd", "Sindhi"),
            ("gu", "Gujarati"),
            ("am", "Amharic"),
            ("yi", "Yiddish"),
            ("lo", "Lao"),
            ("uz", "Uzbek"),
            ("fo", "Faroese"),
            ("ht", "Haitian Creole"),
            ("ps", "Pashto"),
            ("tk", "Turkmen"),
            ("nn", "Nynorsk"),
            ("mt", "Maltese"),
            ("sa", "Sanskrit"),
            ("lb", "Luxembourgish"),
            ("my", "Myanmar"),
            ("bo", "Tibetan"),
            ("tl", "Tagalog"),
            ("mg", "Malagasy"),
            ("as", "Assamese"),
            ("tt", "Tatar"),
            ("haw", "Hawaiian"),
            ("ln", "Lingala"),
            ("ha", "Hausa"),
            ("ba", "Bashkir"),
            ("jw", "Javanese"),
            ("su", "Sundanese"),
        ]
        return langs
