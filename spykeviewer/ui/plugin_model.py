from PyQt4.QtCore import Qt
from PyQt4.QtCore import QAbstractItemModel, QModelIndex

from spykeviewer.plugin_framework.plugin_manager import PluginManager

#noinspection PyMethodOverriding
class PluginModel(PluginManager, QAbstractItemModel):
    """ Implements a Qt-Model for the PluginManager for use in e.g. QTreeView
    """
    DataRole = Qt.UserRole
    FilePathRole = Qt.UserRole+1

    def __init__(self, parent=None):
        PluginManager.__init__(self)
        QAbstractItemModel.__init__(self, parent)

    def columnCount(self, parent):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return None

        item = index.internalPointer()
        if role == Qt.DisplayRole:
            if index.column() > 0:
                return None

            return item.name

        if role == PluginModel.DataRole:
            return item.data
        if role == PluginModel.FilePathRole:
            return item.path

        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        if not index.internalPointer().data:
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole and \
           section == 0:
            return self.root.name

        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parent_node = self.root
        else:
            parent_node = parent.internalPointer()

        child_node = parent_node.child(row)
        if child_node:
            return self.createIndex(row, column, child_node)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        child_node = index.internalPointer()
        parent_node = child_node.parent

        if parent_node == self.root:
            return QModelIndex()

        return self.createIndex(parent_node.row(), 0, parent_node)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parent_node = self.root
        else:
            parent_node = parent.internalPointer()

        return parent_node.childCount()

    def get_indices_for_path(self, path, parent=None):
        indices = []
        if parent is None:
            parent = self.root

        for i in xrange(parent.childCount()):
            c = parent.child(i)
            indices.extend(self.get_indices_for_path(path, c))
            if c.path == path:
                indices.append(self.createIndex(i, 0, c))

        return indices