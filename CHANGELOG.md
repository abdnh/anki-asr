# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2024-02-18

### Changed

-   API keys in the interface are now masked.

### Added

-   Added support for custom ASR services.
-   Added a window to show recently transcribed files.

### Fixed

-   Fix progress dialog blocking review when transcribing in the review screen.

## [1.0.1] - 2023-04-18

### Fixed

-   Fixed error when uninstalling or updating the add-on.

## [1.0.0] - 2023-04-17

### Added

-   Added support for [OpenAI Whisper](https://openai.com/research/whisper).
-   Allow customizing each service's options from the interface.
-   Allow customizing Deepgram's tier and model.

### Fixed

-   Fixed last used provider not being saved.

## [0.1.0] - 2023-01-13

### Added

-   Added a feature to paste transcriptions to a chosen field. See the [README](./README.md#fill-in-option) for usage info.
-   Added the `asr-langs` template filter to list a service's supported languages.

### Fixed

-   Fixed transcription caching sometimes being used when it should not.

## [0.0.1] - 2022-10-26

Initial release

[1.0.1]: https://github.com/abdnh/anki-asr/compare/1.0.1...1.1.0
[1.0.1]: https://github.com/abdnh/anki-asr/compare/1.0.0...1.0.1
[1.0.0]: https://github.com/abdnh/anki-asr/compare/0.1.0...1.0.0
[0.1.0]: https://github.com/abdnh/anki-asr/compare/0.0.1...0.1.0
[0.0.1]: https://github.com/abdnh/anki-asr/releases/tag/0.0.1
