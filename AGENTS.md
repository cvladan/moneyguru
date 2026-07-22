# AGENTS.md: technical notes for moneyGuru, cvladan fork

This file is the technical journal for architecture, the build pipeline, and every technical problem and solution. `README.md` is for users. Implementation details belong here.

All repository documentation, code comments, identifiers, interface text, filenames, and metadata must be written in English.

## Objective

Compile, package, and run moneyGuru on macOS for Apple Silicon. Intel macOS is not supported. Windows work may be considered separately in the future.

The starting point is the `2.12.0_fixes` branch from `rp42/moneyguru`, which uses Qt 5 and a C core.

## Architecture

```text
ccore/      C very core: currency.c, amount.c, py_ccore.c -> _ccore.so
core/       Python core logic and model state. Loads core/model/_ccore.so
qt/         PyQt5 interface. Generates mg_rc.py from mg.qrc with pyrcc5
hscommon/   Shared helper modules
locale/     Translations compiled from .po to .mo with msgfmt
support/    Build helpers and run.template.py
images/     Application resources and macOS icons
help/       Sphinx documentation
scripts/    Reproducible packaging scripts
```

## Source build pipeline

The default `make` target performs these steps:

1. Generates `qt/mg_rc.py` from `qt/mg.qrc` with the selected Python interpreter.
2. Generates `run.py` from `support/run.template.py` and replaces `@SHEBANG@`.
3. Builds `core/model/_ccore.so` through `ccore/Makefile` and copies it into the Python package.
4. Compiles every `locale/*/LC_MESSAGES/*.po` file to `.mo` with `msgfmt`.
5. Verifies the Python version and checks that `PyQt5` imports successfully.

### C core

`ccore/Makefile` compiles `currency.c`, `amount.c`, and `py_ccore.c` into `_ccore.so`.

The compiler, linker command, Python library settings, flags, and include path come from `sysconfig`. On macOS, Python 3.12 supplies `clang -bundle -undefined dynamic_lookup`. SQLite linker flags come from `pkg-config`.

The C extension must be built with the same Python interpreter that runs or packages the application. The supported build interpreter is ARM64 Python 3.12.

## Tested environment

- macOS 26.5 on Apple Silicon
- Xcode Command Line Tools and clang
- Homebrew `pkgconf`, `gettext`, `sqlite`, and `python@3.12`
- PyQt5 5.15.11
- PyInstaller 6.21.0

The system Python 3.14 is too new for the available PyQt5 wheels, so all source and package builds use Homebrew Python 3.12.

## Technical solutions

### 1. Python 3.12

PyQt5 5.15.11 has no wheel for the system Python 3.14. Create `.venv` with `/opt/homebrew/bin/python3.12`. Use the same interpreter for the C extension to preserve ABI compatibility.

The installed PyQt5 wheel is `PyQt5-5.15.11-cp38-abi3-macosx_11_0_arm64`.

### 2. Qt resource compiler

The PyQt5 wheel includes `pyrcc5`, `pyuic5`, and `pylupdate5`. A separate development tools package is not required on macOS.

The Makefile invokes `$(PYTHON) -m PyQt5.pyrcc_main` instead of relying on the generated `pyrcc5` script. This keeps resource generation tied to the selected Python and also works when a virtual environment has moved and its old script shebang is stale.

### 3. Homebrew SQLite and pkg-config

Homebrew SQLite is keg only, so expose its metadata before compiling the C core:

```sh
export PKG_CONFIG_PATH="/opt/homebrew/opt/sqlite/lib/pkgconfig"
```

`pkg-config --libs sqlite3` then returns the Homebrew library path and `-lsqlite3`.

The C core Makefile now fails with a clear message if `pkg-config` is missing or cannot find SQLite. The old backtick command could print an error and still let clang create an extension with unresolved SQLite symbols.

### 4. macOS extension linking

Python 3.12 reports `BLDSHARED = clang -bundle -undefined dynamic_lookup` and an empty `BLDLIBRARY`. Python symbols are resolved when the extension loads, which is correct on macOS.

The filename `_ccore.so` imports successfully because `.so` is present in `importlib.machinery.EXTENSION_SUFFIXES`.

### 5. C syntax fix

Clang rejects `if isdigit(c) {` because it is not valid C. `ccore/amount.c` now uses `if (isdigit(c)) {`.

The remaining `int64_t` format warnings are harmless and are intentionally unchanged.

### 6. Source build command

```sh
source .venv/bin/activate
export PKG_CONFIG_PATH="/opt/homebrew/opt/sqlite/lib/pkgconfig"
make PYTHON=python
```

### 7. Source build verification

- `import core.model._ccore` exposes `Amount`, parsing, formatting, and currency functions.
- `import core.app; import qt.app` succeeds.
- `QT_QPA_PLATFORM=offscreen python ./run.py` keeps the Qt event loop running. The `propagateSizeHints()` message from the offscreen plugin is harmless.

### 8. Light theme

moneyGuru has no application theme setting. Qt normally inherits the macOS system appearance. `support/run.template.py` applies the Fusion style and an explicit light palette by default so the interface stays light without changing macOS settings.

Set `MG_THEME=dark` or `MG_THEME=system` to retain the system appearance. Edit the template, not generated `run.py`.

### 9. Frankfurter currency rates

The Bank of Canada Valet API no longer provides most currency series that moneyGuru requests. The repeated failures filled the log with temporary problem warnings.

`core/plugin/frankfurter_provider.py` uses the free Frankfurter v2 API at `https://api.frankfurter.dev/v2/rates`. It supports more than 160 currencies, including RSD, with data from 1999. The application keeps its existing currency definitions.

Important API details:

- Rates use `GET /v2/rates?from=&to=&base=<CUR>&quotes=CAD` and return a flat JSON list.
- The v1 style `/v2/latest` and dated path variants do not exist.
- The CDN rejects the default Python urllib user agent, so the provider sends an explicit user agent.
- HTTP 404 and 422 mean the pair or currency is unsupported. They map to `CurrencyNotSupportedException`, which allows the quiet fallback rate.
- Network and other service errors map to `RateProviderUnavailable`.

Set `MG_FRANKFURTER_URL` to use a self hosted service, for example `http://localhost:8080/v2/rates`.

### 10. Apple Silicon application package

`make package-macos-arm64` runs `scripts/build-macos-arm64.sh`. The script refuses to run unless both the host and Python interpreter are ARM64. It requires Python 3.12, builds generated resources and the C core, and creates the application with the versioned `moneyGuru.spec` file.

The PyInstaller bundle uses one directory mode, embeds the GPL licence and only compiled translations, requires macOS 11 or newer, and uses `com.cvladan.moneyguru` as its bundle identifier.

Every Mach O file in the bundle must contain an ARM64 slice. The script also verifies the complete code signature and runs the packaged application for five seconds with the Qt offscreen platform. It then creates `dist/moneyGuru-<version>-arm64.zip` and prints its SHA 256 checksum.

PyInstaller applies an ad hoc signature when `CODESIGN_IDENTITY` is empty. Set that environment variable to an installed Developer ID Application identity for a distributable Apple signature. Notarization still requires Apple credentials and is a separate release step.

The PyInstaller configuration directory stays under `build/` so packaging does not depend on write access to `~/Library/Application Support/pyinstaller`.

PyInstaller `argv_emulation` was tested for Finder document opening but caused the packaged application to abort while connecting to Launch Services in the offscreen launch test. It remains disabled. Documents open normally through the application File menus.

### 11. Homebrew Cask distribution

The companion tap is `cvladan/homebrew-tap`. Its `moneyguru` Cask downloads the versioned ARM64 ZIP from the matching GitHub release, verifies its SHA 256 checksum, requires Apple Silicon and macOS 11 or newer, and installs `moneyGuru.app` into `/Applications`.

The first package is ad hoc signed because no Developer ID identity is installed on the build machine. macOS Gatekeeper may therefore require the user to approve the application on first launch. See `docs/homebrew.md` for the release and installation procedure.

## Open work

- Add Developer ID signing and Apple notarization when credentials are available.
- Consider Windows support as a separate project.
- Clean the existing `amount.c` format warnings if a warning free build becomes a priority.
- Modernise the old pytest fixtures. The current suite uses the removed `pytest_funcarg__monkeypatch` hook and does not run on current pytest.

## Conventions for future agents

- `main` is the only branch. There is no `upstream` remote because development continues independently.
- Record every new technical obstacle and solution in the `Technical solutions` section.
- Add user visible build and release changes to the `README.md` work log.
- Keep all repository documentation and human facing artefacts in English.
- Package only for macOS on Apple Silicon unless the user explicitly changes the supported platform scope.
