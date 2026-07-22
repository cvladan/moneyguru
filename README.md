# moneyGuru, cvladan fork

This fork revives moneyGuru for macOS on Apple Silicon and provides a native application package and Homebrew Cask.

Intel Macs are not supported.

## Origin

- Virgil Dupras created the original `hsoft/moneyguru` project. That repository has since been removed from GitHub.
- This code started from the [`rp42/moneyguru`](https://github.com/rp42/moneyguru) `2.12.0_fixes` branch. It contains moneyGuru 2.12.0 and small fixes for modern Python and Qt.
- The rp42 fork is no longer maintained. This repository continues independently and has no `upstream` remote.

## Install with Homebrew

```sh
brew install --cask cvladan/tap/moneyguru
```

The current package is built only for Apple Silicon and requires macOS 11 or newer. It is ad hoc signed because the build machine has no Apple Developer ID certificate. If Gatekeeper blocks the first launch, right click `moneyGuru.app`, choose Open, and confirm the prompt.

See [Homebrew distribution](docs/homebrew.md) for release details and verification commands.

## Build from source

The tested environment is macOS 26.5 on Apple Silicon with Xcode Command Line Tools.

```sh
brew install pkgconf gettext sqlite python@3.12

/opt/homebrew/bin/python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-macos.txt

export PKG_CONFIG_PATH="/opt/homebrew/opt/sqlite/lib/pkgconfig"
make PYTHON=.venv/bin/python
make run
```

The application uses Python 3.12 because PyQt5 does not provide a compatible wheel for the system Python 3.14.

For a launch test without a visible window:

```sh
QT_QPA_PLATFORM=offscreen .venv/bin/python ./run.py
```

## Build the Apple Silicon application

After creating `.venv` and installing `requirements-macos.txt`, run:

```sh
make package-macos-arm64
```

The command creates:

- `dist/moneyGuru.app`
- `dist/moneyGuru-2.12.0-arm64.zip`

The packaging script rejects Intel hosts and non ARM64 Python interpreters. It checks every Mach O file, verifies the application signature, and runs a five second launch test before creating the ZIP.

See [macOS Apple Silicon packaging](docs/macos-packaging.md) for the complete build and signing procedure.

## Currency rates

moneyGuru fetches rates from [Frankfurter](https://frankfurter.dev), a free and open source API based on central bank data. The public endpoint is `https://api.frankfurter.dev/v2/rates`. It supports more than 160 currencies, including RSD, with data from 1999.

You can run Frankfurter locally:

```sh
docker run -d -p 8080:8080 lineofflight/frankfurter
```

Then point moneyGuru at the local service:

```sh
MG_FRANKFURTER_URL="http://localhost:8080/v2/rates" make run
```

A new local Frankfurter instance performs an initial data import, so some endpoints may briefly return no data. See the [Frankfurter deployment guide](https://frankfurter.dev/deploy) for persistent storage and operational details.

## Work log

- 2026-05-21: Imported the `rp42/moneyguru` `2.12.0_fixes` branch and continued development on `main`.
- 2026-05-21: Completed the first successful Apple Silicon source build. Fixed invalid C syntax in `ccore/amount.c`, compiled the C core, generated Qt resources and translations, and verified the Qt event loop.
- 2026-05-21: Added the default light Fusion theme. Set `MG_THEME=system` or `MG_THEME=dark` to keep the system appearance.
- 2026-05-21: Replaced the retired Bank of Canada currency source with Frankfurter v2 and added RSD support.
- 2026-07-22: Added the reproducible Apple Silicon application package, ARM64 validation, code signature verification, launch testing, ZIP release artefact, and Homebrew Cask workflow.

Technical implementation notes live in [AGENTS.md](AGENTS.md).

---

# moneyGuru, original README

[moneyGuru][moneyguru] is a personal finance management application. With it,
you can evaluate your financial situation so you can make informed (and thus
better) decisions. Most finance applications have the same goal, but
moneyGuru's difference is in the way it achieves it. Rather than having reports
which you have to configure (or find out which pre-configured report is the
right one), your important financial data (net worth, profit) is constantly
up-to-date and "in your face".

## Contents of this folder

* ccore: The "very core" code of moneyGuru. Written in C.
* core: Contains the core logic code for moneyGuru. It's Python code.
* qt: UI code for the Qt toolkit. It's written in Python and uses PyQt.
* images: Images used by the different UI codebases.
* help: Help document, written for [Sphinx][sphinx].
* locale: .po files for localisation.
* support: various files to help with the build process.
* hscommon: A collection of helpers used across HS applications.

## How to build moneyGuru from source, original Linux instructions

### Prerequisites

* Python 3.4+
* PyQt5
* GNU build environment

On Ubuntu: `apt-get install python3-dev python3-pyqt5 pyqt5-dev-tools`

### make

    $ make
    $ make run

## Running tests

The complete test suite is run with [Tox][tox], or without it via
`pip install -r requirements-tests.txt` then `py.test core hscommon`.

[moneyguru]: http://www.hardcoded.net/moneyguru/
[documentation]: http://www.hardcoded.net/moneyguru/help/en/
[sphinx]: http://sphinx.pocoo.org/
[tox]: https://tox.readthedocs.org/en/latest/
