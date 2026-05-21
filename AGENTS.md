# AGENTS.md — tehnička beleška za moneyGuru (cvladan fork)

Ovaj fajl je tehnički dnevnik: arhitektura, build pipeline, i **sva tehnička rešenja**
(problemi na koje naiđemo i kako su rešeni). README.md je za korisnika; ovde idu detalji.

## Cilj

Kompajlirati i pokrenuti moneyGuru na **macOS** (Apple Silicon), pa kasnije i Windows.
Polazna osnova: `rp42/moneyguru` grana `2.12.0_fixes` (Qt5 + C core).

## Arhitektura

```
ccore/      C "very core": currency.c, amount.c, py_ccore.c  -> _ccore.so (CPython ekstenzija)
core/       Python core logika (model, gui state). Učitava core/model/_ccore.so
qt/         PyQt5 UI (mg_rc.py se generiše iz mg.qrc preko pyrcc5)
hscommon/   HS deljeni helperi
locale/     .po prevodi -> .mo (msgfmt)
support/    build pomoćnici (run.template.py, skripte)
images/     resursi
help/        Sphinx dokumentacija
```

## Build pipeline (iz Makefile-a)

`make` (target `all`) radi:
1. `qt/mg_rc.py` ← `pyrcc5 qt/mg.qrc` (kompajlira Qt resurse u Python modul)
2. `run.py` ← iz `support/run.template.py` (sed zamena `@SHEBANG@`)
3. `core/model/_ccore.so` ← `make -C ccore` pa kopiranje u `core/model`
4. `i18n`: svaki `locale/*/LC_MESSAGES/*.po` → `.mo` preko `msgfmt`
5. `reqs`: provera Python ≥ 3.4 i da `import PyQt5` radi

### ccore/Makefile
- Kompajlira `currency.c amount.c py_ccore.c` → `_ccore.so`.
- Sve flagove vuče iz `python -c "import sysconfig; ..."` (CC, BLDSHARED, BLDLIBRARY,
  CFLAGS, INCLUDEPY) — zato je **portabilno**: na macOS-u sysconfig daje
  `clang -bundle -undefined dynamic_lookup`.
- Linkuje: `pkg-config --libs sqlite3` + `BLDLIBRARY`.
- **Bitno:** mora se graditi istim Pythonom kojim se i pokreće (ABI). Koristimo venv 3.12.

## Okruženje

- macOS 26.5, Apple Silicon, clang iz Command Line Tools.
- Homebrew: `pkg-config` (pkgconf), `gettext` (msgfmt), `sqlite`, `python@3.12`.
- Sistemski `python3` je 3.14.5 — **prenov za PyQt5 wheel-ove**, zato koristimo 3.12.

## Tehnička rešenja (hronološki)

### 1. Izbor Pythona 3.12
PyQt5 (5.15.11) nema wheel za sistemski 3.14. Pravimo `.venv` sa
`/opt/homebrew/bin/python3.12`. Isti interpreter koristimo i za `make -C ccore`
(ABI konzistentnost `_ccore.so`). Instaliran wheel: `PyQt5-5.15.11-cp38-abi3-macosx_11_0_arm64`.

### 2. pyrcc5 dolazi sa PyQt5 wheel-om
Na Linuxu se `pyrcc5` instalira iz `pyqt5-dev-tools`. Na macOS-u **pip PyQt5 wheel već sadrži**
`.venv/bin/pyrcc5`, `pyuic5`, `pylupdate5` — nije potreban poseban paket. Build se pokreće sa
`.venv` na PATH-u (ili aktiviranim venv-om) da bi `make` našao `pyrcc5`.

### 3. sqlite3 je keg-only (PKG_CONFIG_PATH)
`ccore/Makefile` linkuje preko `pkg-config --libs sqlite3`. Homebrew-ov `sqlite` je keg-only,
pa `sqlite3.pc` nije na default putanji. Rešenje:
```
export PKG_CONFIG_PATH="/opt/homebrew/opt/sqlite/lib/pkgconfig"
```
Tada `pkg-config --libs sqlite3` → `-L/opt/homebrew/opt/sqlite/lib -lsqlite3`.

### 4. Linkovanje C ekstenzije na macOS-u (radi bez izmena)
`sysconfig` na 3.12 daje `BLDSHARED = clang -bundle -undefined dynamic_lookup` i prazan
`BLDLIBRARY` (Python simboli se razrešavaju pri učitavanju — ispravno za ekstenzije na Mac-u).
Pošto `ccore/Makefile` sve flagove vuče iz `sysconfig`, link prolazi bez ikakvih izmena.
Ime fajla `_ccore.so` (bez `.cpython-...` sufiksa) se uredno importuje jer je `.so` u
`importlib.machinery.EXTENSION_SUFFIXES`.

### 5. C fix: `if isdigit(c)` → `if (isdigit(c))` (ccore/amount.c, ~l.468)
clang odbija `if isdigit(c) {` ("expected '(' after 'if'") — to nikad i nije validan C.
Dodate zagrade. Ovo je jedina izmena izvornog koda potrebna za macOS build.
(Upozorenja tipa `%ld` vs `int64_t` su bezopasna i ostavljena.)

### 6. Build komanda (sve zajedno)
```
source .venv/bin/activate
export PKG_CONFIG_PATH="/opt/homebrew/opt/sqlite/lib/pkgconfig"
make PYTHON=python      # PYTHON=python da sub-make ccore koristi venv interpreter
```

### 7. Verifikacija
- `import core.model._ccore` → izlaže `Amount, amount_parse, amount_format, currency_*` (OK).
- `import core.app; import qt.app` (OK).
- `QT_QPA_PLATFORM=offscreen python ./run.py` → drži Qt event loop 12s bez greške
  (samo bezopasno "plugin does not support propagateSizeHints()"). Na realnom desktopu = prozor.

### Otvorene stavke / dalje
- Pravljenje `.app` bundle-a za macOS (PyInstaller/py2app) — još nije rađeno.
- Windows build (PyQt5 + MSVC/MinGW za ccore) — kasnije.
- Format-warning u `amount.c` se mogu očistiti (`%lld`/`%llu`) ako se želi čist build.

## Konvencije za buduće agente

- `upstream` remote = `rp42/moneyguru` (povlačenje budućih fixova).
- Svaku novu tehničku prepreku i rešenje dopisati u sekciju "Tehnička rešenja".
- Korisnički vidljive promene (build uputstvo, status) idu i u `README.md` "Dnevnik rada".
- Ne menjati upstream istoriju; raditi na grani izvedenoj iz `2.12.0_fixes`.
