#! /usr/bin/env python

import sys
import os
import platform
import locale

# Hack to circumvent OS X locale bug
if platform.system() == 'Darwin':
    if os.getenv('LC_CTYPE') == 'UTF-8':
        os.environ['LC_CTYPE'] = ''
else:
    locale.setlocale(locale.LC_ALL, '')

# Use new style API
import sip
sip.setapi('QString', 2)
sip.setapi('QDate', 2)
sip.setapi('QDateTime', 2)
sip.setapi('QTextStream', 2)
sip.setapi('QTime', 2)
sip.setapi('QVariant', 2)
sip.setapi('QUrl', 2)
sip.setapi('QVariant', 2)

from PyQt4 import QtGui

if __name__ == "__main__":
    # If spykeviewer is not on pythonpath, try parent directory
    try:
        from spykeviewer.ui.main_window_neo import MainWindowNeo
    except ImportError:
        sys.path.insert(0, os.path.abspath(os.pardir))
        from spykeviewer.ui.main_window_neo import MainWindowNeo

    app = QtGui.QApplication(sys.argv)
    ui = MainWindowNeo()
    ui.show()
    ui.raise_()
    sys.exit(app.exec_())
