# moneyGuru — cvladan fork (macOS revival)

Lični fork sa ciljem: **kompajlirati i pokrenuti moneyGuru na macOS-u** (a kasnije i Windows),
i eventualno nastaviti razvoj.

## Poreklo (lanac forkova)

- Originalni autor: **Virgil Dupras** (`hsoft/moneyguru`) — repo je **obrisan sa GitHub-a**
  (vraća 404). Korisnik `hsoft` i dalje postoji, ali projekta nema.
- Ovaj fork je nastavak na **[rp42/moneyguru](https://github.com/rp42/moneyguru)**, grana
  `2.12.0_fixes` — to je verzija 2.12.0 sa minimalnim 2023. ispravkama da radi na modernom
  Pythonu/Qt-u (npr. `collections.abc` import, `QPainter.drawPie` int cast).
- `rp42` je dodat kao `upstream` remote radi lakšeg povlačenja budućih ispravki.

## Zašto rp42, a ne lenlo (Cocoa)?

Razmatrana su dva forka za macOS:

| | rp42 (ovaj) | lenlo |
|---|---|---|
| UI toolkit | **Qt5 / PyQt5** (cross-platform) | Cocoa (nativni macOS, Obj-C + PyObjC) |
| Skorašnjost | 2023, već zakrpljen za moderni Python | 2017 |
| Build na Mac-u 2026 | clang + pip PyQt5 — izvodljivo | oživljavanje `objp` bridge-a + stari Xcode projekat — vrlo teško |

Iako je lenlo „nativni macOS", njegov Cocoa build je previše bit-rotovan. rp42 je Qt5, a Qt je
inherentno cross-platform — autor je samo prestao da *pakuje* Mac/Win build-ove, kod sam može da
se izgradi. Zato je rp42 realno najbrži put do „radi na Mac-u".

## Okruženje (testirano)

- macOS 26.5 (Apple Silicon), Xcode Command Line Tools (clang)
- Homebrew: `pkg-config`, `gettext`, `sqlite`, `python@3.12`
- Build Python: **3.12** (PyQt5 ima wheel-ove; sistemski 3.14 je prenov za PyQt5)

## Build na macOS — uputstvo

> Popunjava se kako rešavamo korak po korak. Vidi `AGENTS.md` za detaljna tehnička objašnjenja.

**Testirano: build i pokretanje rade na macOS 26.5 (Apple Silicon).**

```bash
# 1. Build alati (Homebrew)
brew install pkg-config gettext sqlite python@3.12

# 2. Virtualenv sa Python 3.12 + PyQt5
#    (pyrcc5/pyuic5 dolaze U SKLOPU PyQt5 wheel-a — nije potreban poseban paket)
/opt/homebrew/bin/python3.12 -m venv .venv
source .venv/bin/activate
pip install PyQt5

# 3. Build (C core + Qt resursi + prevodi)
#    sqlite je "keg-only" u Homebrew -> mora PKG_CONFIG_PATH za ccore link
export PKG_CONFIG_PATH="/opt/homebrew/opt/sqlite/lib/pkgconfig"
make PYTHON=python

# 4. Pokretanje (na svom Mac desktopu prikazaće pravi prozor)
make run
```

Smoke test bez prozora (offscreen):

```bash
QT_QPA_PLATFORM=offscreen python ./run.py   # mora startovati event loop bez greške
```

## Dnevnik rada

- **2026-05-21** — Forkovan rp42@`2.12.0_fixes`, postavljen na `cvladan/moneyguru`, `rp42`
  dodat kao `upstream`.
- **2026-05-21** — **macOS build USPEŠAN.** Jedina kod-izmena: ispravljena C sintaksna greška
  u `ccore/amount.c` (`if isdigit(c)` → `if (isdigit(c))`, clang je odbijao). C core
  (`_ccore.so`) se kompajlira, Qt resursi i prevodi se generišu, aplikacija se pokreće i drži
  Qt event loop (potvrđeno offscreen). Detalji u `AGENTS.md`.

---

# moneyGuru (originalni README)

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

## How to build moneyGuru from source (original, Linux)

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
