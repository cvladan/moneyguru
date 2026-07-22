# Homebrew distribution

The personal tap lives in [`cvladan/homebrew-tap`](https://github.com/cvladan/homebrew-tap). moneyGuru is distributed as a Cask because the release artefact is a ready made macOS application.

## Install

```sh
brew install --cask cvladan/tap/moneyguru
```

The Cask requires Apple Silicon and macOS 11 or newer. Homebrew downloads the release ZIP, checks its SHA 256 checksum, and moves `moneyGuru.app` into `/Applications`.

The current build has an ad hoc signature. If macOS blocks the first launch, right click `moneyGuru.app`, choose Open, and confirm the prompt. A future Developer ID signed and notarized release will remove this manual approval step.

## Cask release contract

For version `2.12.0`, the Cask uses:

```text
https://github.com/cvladan/moneyguru/releases/download/v2.12.0/moneyGuru-2.12.0-arm64.zip
```

The application version, Git tag, archive filename, Cask version, and SHA 256 checksum must describe the same final build.

## Update procedure

1. Run `make package-macos-arm64` in the moneyGuru repository.
2. Record the printed SHA 256 checksum.
3. Publish the ZIP under the matching `v<version>` GitHub release.
4. Update `Casks/moneyguru.rb` in the tap with the version and checksum.
5. Run the Cask syntax, style, audit, and install checks.

## Tap verification

From the tap repository:

```sh
brew style --cask Casks/moneyguru.rb
brew audit --cask --online cvladan/tap/moneyguru
brew fetch --cask cvladan/tap/moneyguru
brew install --cask cvladan/tap/moneyguru
```

Then verify the installed application:

```sh
file /Applications/moneyGuru.app/Contents/MacOS/moneyGuru
codesign --verify --deep --strict --verbose=2 /Applications/moneyGuru.app
```

The `file` result must report `arm64`. The code signature check must complete successfully.

## Uninstall

```sh
brew uninstall --cask moneyguru
```

To remove application preferences and support files as well:

```sh
brew uninstall --zap --cask moneyguru
```
