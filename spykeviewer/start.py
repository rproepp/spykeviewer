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

# The entry point for Spyke Viewer
def main():
    from ui.main_window_neo import MainWindowNeo

    app = QtGui.QApplication(sys.argv)
    ui = MainWindowNeo()
    ui.show()
    ui.raise_()
    sys.exit(app.exec_())