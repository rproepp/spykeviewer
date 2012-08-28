import os
import sys
import inspect
import traceback
import logging

from spykeutils.plugin.analysis_plugin import AnalysisPlugin

logger = logging.getLogger('spykeviewer')

class PluginManager:
    """ Manages plugins loaded from a directory
    """
    class Node:
        def __init__(self, parent, data, path, name):
            self.parent = parent
            self.data = data
            self.name = name
            self.path = path

        def childCount(self):
            return 0

        def row(self):
            if self.parent:
                return self.parent.children.index(self)
            return 0

    class DirNode(Node):
        def __init__(self, parent, data, path = ''):
            """ Recursively walk down the tree, loading all legal plugin classes along the way
            """
            PluginManager.Node.__init__(self, parent, data, path, '')
            self.children = []

            if path:
                self.addPath(path)

        def child(self, row):
            return self.children[row]

        def childCount(self):
            return len(self.children)

        def get_dir_child(self, dir):
            for n in self.children:
                if os.path.split(n.path)[1] == os.path.split(dir)[1] and \
                   isinstance(n, PluginManager.DirNode):
                    return n
            return None

        def addPath(self, path):
            if not path:
                return

            self.name = os.path.split(path)[1]

            for f in os.listdir(path):
                # Don't include hidden directories
                if f.startswith('.'):
                    continue

                p = os.path.join(path, f)
                if os.path.isdir(p):
                    new_node = self.get_dir_child(p)
                    if new_node:
                        new_node.addPath(p)
                    else:
                        new_node = PluginManager.DirNode(self, None, p)
                        self.children.append(new_node)
                else:
                    if not f.endswith('.py'):
                        continue

                    # Found a Python file, execute it and look for plugins
                    exc_globals = {}
                    try:
                        execfile(p, exc_globals)
                    except Exception:
                        logger.warning('Error during execution of ' +
                            'potential plugin file ' + p + ':\n' +
                            traceback.format_exc() + '\n')
                    for cl in exc_globals.values():
                        if not inspect.isclass(cl):
                            continue

                        # Should be a subclass of AnalysisPlugin...
                        if not issubclass(cl, AnalysisPlugin):
                            continue
                        # ...but should not be AnalysisPlugin (can happen
                        # when directly imported)
                        if cl == AnalysisPlugin:
                            continue

                        # Plugin class found, add it to tree
                        try:
                            instance = cl()
                        except Exception:
                            etype, evalue, etb = sys.exc_info()
                            evalue = etype('Exception while creating %s: %s' %
                                           (cl.__name__, evalue))
                            raise etype, evalue, etb
                        self.children.append(PluginManager.Node(self,
                            instance, p, instance.get_name()))

    def __init__(self):
        self.root = self.DirNode(None, None)

    def add_path(self, path):
        self.root.addPath(path)