@SHEBANG@
# Copyright 2018 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import os
import sys
import gc
import logging
import os.path as op

from PyQt5.QtCore import QFile, QTextStream, QSettings, Qt
from PyQt5.QtGui import QIcon, QPixmap, QPalette, QColor
from PyQt5.QtWidgets import QApplication, QStyleFactory

import hscommon.trans
from core.args import get_parser
from qt.support.error_report_dialog import install_excepthook
from qt.util import setupQtLogging
from qt.preferences import adjust_after_deserialization
import qt.mg_rc # noqa
from qt.plat import BASE_PATH


def apply_light_theme(app):
    """Force a light ("white") appearance, independent of the macOS System
    Settings -> Appearance (Dark/Light). Disable with MG_THEME=dark or
    MG_THEME=system. See AGENTS.md for details."""
    theme = os.environ.get('MG_THEME', 'light').lower()
    if theme in ('dark', 'system'):
        return
    fusion = QStyleFactory.create('Fusion')
    if fusion is not None:
        app.setStyle(fusion)
    white = QColor(255, 255, 255)
    light = QColor(240, 240, 240)
    text = QColor(0, 0, 0)
    disabled = QColor(120, 120, 120)
    pal = QPalette()
    pal.setColor(QPalette.Window, light)
    pal.setColor(QPalette.WindowText, text)
    pal.setColor(QPalette.Base, white)
    pal.setColor(QPalette.AlternateBase, light)
    pal.setColor(QPalette.ToolTipBase, white)
    pal.setColor(QPalette.ToolTipText, text)
    pal.setColor(QPalette.Text, text)
    pal.setColor(QPalette.Button, light)
    pal.setColor(QPalette.ButtonText, text)
    pal.setColor(QPalette.BrightText, Qt.red)
    pal.setColor(QPalette.Highlight, QColor(48, 140, 198))
    pal.setColor(QPalette.HighlightedText, white)
    pal.setColor(QPalette.Link, QColor(48, 140, 198))
    pal.setColor(QPalette.Disabled, QPalette.Text, disabled)
    pal.setColor(QPalette.Disabled, QPalette.WindowText, disabled)
    pal.setColor(QPalette.Disabled, QPalette.ButtonText, disabled)
    app.setPalette(pal)


def main():
    parser = get_parser()
    args = parser.parse_args()
    app = QApplication([])
    apply_light_theme(app)
    app.setWindowIcon(QIcon(QPixmap(":/logo_small")))
    app.setOrganizationName('Hardcoded Software')
    app.setApplicationName('moneyGuru')
    settings = QSettings()
    if args.debug:
        LOGGING_LEVEL = logging.DEBUG
    else:
        LOGGING_LEVEL = logging.DEBUG if adjust_after_deserialization(settings.value('DebugMode')) else logging.WARNING
    setupQtLogging(level=LOGGING_LEVEL)
    logging.debug('started in debug mode')
    stylesheetFile = QFile(':/stylesheet_lnx')
    stylesheetFile.open(QFile.ReadOnly)
    textStream = QTextStream(stylesheetFile)
    style = textStream.readAll()
    stylesheetFile.close()
    app.setStyleSheet(style)
    lang = settings.value('Language')
    locale_folder = op.join(BASE_PATH, 'locale')
    hscommon.trans.install_gettext_trans_under_qt(locale_folder, lang)
    # Many strings are translated at import time, so this is why we only import after the translator
    # has been installed
    from qt.app import MoneyGuru
    app.setApplicationVersion(MoneyGuru.VERSION)
    mgapp = MoneyGuru(filepath=args.filepath)
    install_excepthook('https://github.com/hsoft/moneyguru/issues')
    exec_result = app.exec_()
    del mgapp
    # Since PyQt 4.7.2, I had crashes on exit, and from reading the mailing list, it seems to be
    # caused by some weird crap about C++ instance being deleted with python instance still living.
    # The worst part is that Phil seems to say this is expected behavior. So, whatever, this
    # gc.collect() below is required to avoid a crash.
    gc.collect()
    return exec_result

if __name__ == "__main__":
    sys.exit(main())
