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
from PyQt4.QtTest import QTest
from PyQt4.QtCore import Qt
from spykeviewer.ui.main_window_neo import MainWindowNeo


class TestMainWindow(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtGui.QApplication(sys.argv)
        cls.win = MainWindowNeo()

    @classmethod
    def tearDownClass(cls):
        cls.win.close()

    def test_object_selections(self):
        self.assertNotEqual(self.win.neo_blocks(), None)
        self.assertNotEqual(self.win.neo_segments(), None)
        self.assertNotEqual(self.win.neo_channel_groups(), None)
        self.assertNotEqual(self.win.neo_channels(), None)
        self.assertNotEqual(self.win.neo_units(), None)

    def test_plugins_loaded(self):
        self.assert_(
            self.win.plugin_model.hasIndex(0, 0),
            'Plugin model is empty')

    def test_filter_tree(self):
        self.assertEqual(
            self.win.filterDock.filterTreeWidget.topLevelItemCount(), 5)

    def test_file_tree(self):
        self.assert_(
            self.win.fileTreeView.model().hasIndex(0, 0),
            'Filesystem model is empty')

    def test_console(self):
        QTest.keyClick(self.win.console, Qt.Key_1)
        QTest.keyClick(self.win.console, Qt.Key_Plus)
        QTest.keyClick(self.win.console, Qt.Key_1)
        lines = self.win.console.get_line_count()
        self.assertEqual(
            self.win.console.get_text_line(lines - 1), '>>> 1+1')

        QTest.keyClick(self.win.console, Qt.Key_Enter)
        lines = self.win.console.get_line_count()
        self.assertEqual(self.win.console.get_text_line(lines - 1), '>>> ')

    def test_history(self):
        history_lines = self.win.history.get_line_count()
        QTest.keyClick(self.win.console, Qt.Key_5)
        QTest.keyClick(self.win.console, Qt.Key_Enter)
        self.assertEqual(
            history_lines + 1, self.win.history.get_line_count())
        self.assertEqual(
            self.win.history.get_text_line(history_lines), '5')

    def test_plugin_editor(self):
        self.assertEqual(
            self.win.pluginEditorDock.tabs.currentWidget(), None)
        self.win.actionNewPlugin.trigger()
        self.assertNotEqual(
            self.win.pluginEditorDock.tabs.currentWidget(), None)
        self.assertEqual(
            u'\n'.join(self.win.pluginEditorDock.code()),
            unicode(self.win.pluginEditorDock.template_code + '\n'))


if __name__ == '__main__':
    ut.main()