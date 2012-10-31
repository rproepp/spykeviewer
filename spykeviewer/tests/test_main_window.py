"""try:
    import unittest2 as ut
except ImportError:
    import unittest as ut

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


class TestMainWindow(ut.TestCase):
    def setUp(self):
        from spykeviewer.ui.main_window_neo import MainWindowNeo

        app = QtGui.QApplication(sys.argv)
        self.window = MainWindowNeo()
        #ui.show()
        #ui.raise_()
        #sys.exit(app.exec_())

    def test_creation(self):
        self.assertNotEqual(self.window, None)

if __name__ == '__main__':
    ut.main()
"""