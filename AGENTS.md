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
PyQt5 (5.15.x) nema wheel za 3.14. Pravimo `.venv` sa `/opt/homebrew/bin/python3.12`.
Isti interpreter koristimo i za `make -C ccore` (ABI konzistentnost _ccore.so).

### 2. (u toku) Build koraci
Beleške o `pyrcc5`, `pkg-config sqlite3`, linkovanju i pokretanju dodaju se ovde kako
nailazimo na njih.

## Konvencije za buduće agente

- `upstream` remote = `rp42/moneyguru` (povlačenje budućih fixova).
- Svaku novu tehničku prepreku i rešenje dopisati u sekciju "Tehnička rešenja".
- Korisnički vidljive promene (build uputstvo, status) idu i u `README.md` "Dnevnik rada".
- Ne menjati upstream istoriju; raditi na grani izvedenoj iz `2.12.0_fixes`.
