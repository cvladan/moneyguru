# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

from core import __version__


datas = [
    (str(path), str(path.parent))
    for path in sorted(Path("locale").glob("*/LC_MESSAGES/*.mo"))
]
datas.append(("LICENSE", "."))
codesign_identity = os.environ.get("CODESIGN_IDENTITY") or None


a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='moneyGuru',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='arm64',
    codesign_identity=codesign_identity,
    entitlements_file=None,
    icon=['images/main_icon.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='moneyGuru',
)
app = BUNDLE(
    coll,
    name='moneyGuru.app',
    icon='images/main_icon.icns',
    bundle_identifier='com.cvladan.moneyguru',
    version=__version__,
    info_plist={
        'CFBundleDevelopmentRegion': 'en',
        'CFBundleVersion': __version__,
        'LSApplicationCategoryType': 'public.app-category.finance',
        'LSMinimumSystemVersion': '11.0',
    },
)
