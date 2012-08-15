#! /usr/bin/env python

import sys
import os
import locale

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

    locale.setlocale(locale.LC_ALL, '')
    app = QtGui.QApplication(sys.argv)
    ui = MainWindowNeo()
    ui.show()
    sys.exit(app.exec_())
