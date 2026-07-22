# macOS Apple Silicon packaging

moneyGuru is packaged as a native macOS application with PyInstaller. The package supports Apple Silicon only. Intel and universal builds are intentionally outside the supported scope.

## Requirements

- macOS 11 or newer on an Apple Silicon Mac
- Xcode Command Line Tools
- Homebrew
- Homebrew `pkgconf`, `gettext`, `sqlite`, and `python@3.12`
- Python packages from `requirements-macos.txt`

Install the build dependencies and create the virtual environment:

```sh
brew install pkgconf gettext sqlite python@3.12

/opt/homebrew/bin/python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements-macos.txt
```

Both the host and the selected Python interpreter must report `arm64`. The C extension and every bundled dependency inherit that architecture.

## Build

```sh
make package-macos-arm64
```

To use another Python 3.12 ARM64 environment:

```sh
PYTHON=/absolute/path/to/python make package-macos-arm64
```

The command performs a clean source build, compiles translations, builds the C core against Homebrew SQLite, and runs PyInstaller with `moneyGuru.spec`.

All PyInstaller cache data stays under `build/`. This matters on constrained systems and in sandboxes because the default cache path is under `~/Library/Application Support`.

## Outputs

The build creates:

```text
dist/moneyGuru.app
dist/moneyGuru-2.12.0-arm64.zip
```

The ZIP name comes from `core.__version__`. The script prints the SHA 256 checksum needed by the Homebrew Cask.

## Automatic verification

Packaging fails unless all of these checks pass:

1. The host architecture is `arm64`.
2. Python 3.12 runs as `arm64` and imports PyQt5 and PyInstaller.
3. The C extension builds and links against Homebrew SQLite.
4. Every Mach O file in the application contains an ARM64 slice.
5. `codesign --verify --deep --strict` accepts the complete bundle.
6. The packaged application keeps its Qt event loop alive for five seconds with the offscreen platform.

The application bundle uses `com.cvladan.moneyguru` as its identifier, includes the GPL licence, and declares macOS 11 as its minimum version. Open `.moneyguru` documents through the application File menus. Finder launch emulation is disabled because it is not stable in the verified offscreen launch path.

## Signing

PyInstaller applies an ad hoc signature by default. The signature protects bundle integrity but does not establish an Apple verified developer identity and is not notarized.

To sign with an installed Developer ID Application certificate:

```sh
security find-identity -v -p codesigning
CODESIGN_IDENTITY="Developer ID Application: Example Name (TEAMID)" \
  make package-macos-arm64
```

Verify the result:

```sh
codesign --verify --deep --strict --verbose=2 dist/moneyGuru.app
codesign -dv --verbose=4 dist/moneyGuru.app
```

Apple notarization requires Developer ID credentials and must happen before the release ZIP is published. Until those credentials are available, users may need to approve the application through the first launch Gatekeeper prompt.

## Release artefact

The Homebrew Cask expects this exact GitHub release contract:

```text
Tag:   v2.12.0
Asset: moneyGuru-2.12.0-arm64.zip
```

After the repository changes are committed and the tag is ready, create the release with the generated ZIP:

```sh
gh release create v2.12.0 \
  dist/moneyGuru-2.12.0-arm64.zip \
  --repo cvladan/moneyguru \
  --title "moneyGuru 2.12.0 for Apple Silicon" \
  --notes "Apple Silicon macOS application package."
```

Update the Cask checksum only after the final signing and packaging pass because any bundle change produces a different ZIP checksum.
