[Anki](https://apps.ankiweb.net/) add-on for [speech recognition](https://en.wikipedia.org/wiki/Speech_recognition).

## Supported speech-to-text services

The only supported service at the moment is [Deepgram](https://deepgram.com/). I plan to add support for [Google Speech-to-Text](https://cloud.google.com/speech-to-text) and maybe [Whisper](https://github.com/openai/whisper) in the future.

## Usage

Most speech recognition services require you to register for an API key.
After you sign up and get your key, you need to paste it in the add-on's config. Go to _Tools > Add-ons_, select this add-on from your add-on list, and click _Config_. Then paste your key in the `api_key` option under _provider_options > deepgram_.

### As a template filter

Currently, the add-on works as a template filter you put in your [card template](https://docs.ankiweb.net/templates/intro.html). E.g:

```
{{asr:Front}}
```

The add-on processes any `[sound:foo.mp3]` tags in the specified field and replaces them with the transcriptions of the audio.

You can specify the language using the `lang` option. E.g:

```
{{asr lang=tr:Front}}
```

The default language is English (`en`). Supported languages depend on the service used. For Deepgram, see https://deepgram.com/product/languages/ for a list of supported languages.

The speech-to-text service used can be specified using the `provider` option. E.g:

```
{{asr provider=deepgram:Front}}
```

If you set `auto=false`, a button will be shown that you can click to show the transcription:

```
{{asr auto=false:Front}}
```

This is useful to avoid making a request to the ASR service when not needed, or to simply use the transcription as an optional hint.

## Planned features

Besides adding support for more services, I plan to add an option to fill in note a chosen field with the transcription, maybe with an option to process notes in bulk.
