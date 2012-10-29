try:
    import unittest2 as ut
except ImportError:
    import unittest as ut

import sys
import os
from spykeviewer.plugin_framework.plugin_manager import PluginManager

class TestPluginManager(ut.TestCase):
    def setUp(self):
        self.manager = PluginManager()

        if hasattr(sys, 'frozen'):
            module_path = os.path.dirname(sys.executable)
        else:
            file_path = os.path.abspath(os.path.dirname(__file__))
            module_path = os.path.dirname(file_path)
        self.manager.add_path(os.path.join(module_path, 'plugins'))

    def test_not_empty(self):
        self.assertGreater(self.manager.root.childCount(), 0,
            'Plugin manager with default path is empty')

    def test_directories_loaded(self):
        num_dirs = 0
        for n in self.manager.root.children:
            if isinstance(n, PluginManager.DirNode):
                num_dirs += 1
        self.assertGreater(num_dirs, 0, 'No plugin directories loaded')

    def test_plugins_loaded(self):
        def find_plugins(dir_node):
            plugins = 0
            for n in dir_node.children:
                if isinstance(n, PluginManager.DirNode):
                    plugins += find_plugins(n)
                else:
                    plugins += 1
            return plugins

        self.assertGreater(find_plugins(self.manager.root), 0,
            'No plugins loaded')

if __name__ == '__main__':
    ut.main()
