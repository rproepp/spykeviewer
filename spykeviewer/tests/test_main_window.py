"""
try:
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
        self.window = None

        from spykeviewer.ui.main_window_neo import MainWindowNeo
        app = QtGui.QApplication(sys.argv)
        self.window = MainWindowNeo()

    def test_creation(self):
        self.assertNotEqual(self.window, None)

    def test_object_selections(self):
        self.assertNotEqual(self.window.neo_blocks(), None)
        self.assertNotEqual(self.window.neo_segments(), None)
        self.assertNotEqual(self.window.neo_channel_groups(), None)
        self.assertNotEqual(self.window.neo_channels(), None)
        self.assertNotEqual(self.window.neo_units(), None)

    def tearDown(self):
        self.window.close()

if __name__ == '__main__':
    ut.main()
"""