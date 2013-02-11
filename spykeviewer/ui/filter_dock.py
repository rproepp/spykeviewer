from PyQt4 import QtGui, QtCore
import os
import sys

from PyQt4.QtGui import (QDockWidget, QWidget, QFileDialog, QGridLayout,
                         QMessageBox, QFont, QTabWidget, QTextCursor,
                         QDesktopServices, QAbstractItemView, QTreeWidget,
                         QApplication, QStyle, QTreeWidgetItem)
from PyQt4.QtCore import Qt, pyqtSignal, SIGNAL, QSettings, QMutex

from ..plugin_framework.filter_manager import FilterManager
from checkable_item_delegate import CheckableItemDelegate


class FilterDock(QDockWidget):
    """ Dock with filter tree
    """
    FilterTreeRoleTop = 0
    FilterTreeRoleGroup = 1
    FilterTreeRoleFilter = 2

    def __init__(self, filter_path, title='Filter', parent=None):
        QDockWidget.__init__(self, title, parent)
        self.setupUi()

        self.filter_path = filter_path

        # TODO: Abstract using signal
        self.filter_populate_function = \
            {'Block': parent.populate_neo_block_list,
             'Recording Channel': parent.populate_neo_channel_list,
             'Recording Channel Group': parent.populate_neo_channel_group_list,
             'Segment': parent.populate_neo_segment_list,
             'Unit': parent.populate_neo_unit_list}

        self.filter_managers = {}
        self.filter_managers['Block'] = \
            FilterManager('block', os.path.join(self.filter_path,
                                                'block.py'))
        self.filter_managers['Segment'] = \
            FilterManager('segment', os.path.join(self.filter_path,
                                                  'segment.py'))
        self.filter_managers['Recording Channel Group'] = \
            FilterManager('rcg', os.path.join(self.filter_path,
                                              'rcg.py'))
        self.filter_managers['Recording Channel'] = \
            FilterManager('rc', os.path.join(self.filter_path,
                                             'rc.py'))
        self.filter_managers['Unit'] = \
            FilterManager('unit', os.path.join(self.filter_path,
                                               'unit.py'))
        self.populate_filter_tree()
        self.filters_changed = False

        self.filterTreeWidget.dragMoveEvent = self._filter_drag_move
        self.filterTreeWidget.dropEvent = self._filter_drag_end
        self.filterTreeWidget.keyReleaseEvent = self._filter_key_released
        self.filterTreeWidget.mouseReleaseEvent = \
            self._filter_mouse_released
        self.filterTreeWidget.setItemDelegate(CheckableItemDelegate(
            self.filterTreeWidget))

    def get_active_filters(self, name):
        return self.filter_managers[name].get_active_filters()

    # Method injection to handle the actual "drop" of Drag and Drop
    def _filter_drag_end(self, event):
        source = self.filterTreeWidget.currentItem()
        source_name = source.text(0)
        target = self.filterTreeWidget.itemAt(event.pos())

        source_top, source_group = self._get_filter_item_coords(source)
        parent = target.parent()
        if parent:
            if parent.parent():
                target_top = parent.parent().text(0)
                target_group = parent.text(0)
            else:
                target_top = parent.text(0)
                if target.data(1, Qt.UserRole) == \
                        self.FilterTreeRoleGroup:
                    target_group = target.text(0)
                else:
                    target_group = None
        else:
            target_top = target.text(0)
            target_group = None

        # Find drop position
        target_index = self.filterTreeWidget.indexAt(event.pos())
        target_height = self.filterTreeWidget.rowHeight(target_index)
        pos = event.pos()
        pos.setY((pos.y() - target_height / 2))
        item_above_target = self.filterTreeWidget.itemAt(pos)
        above_target = item_above_target.text(0) if item_above_target \
            else None

        item = self.filter_managers[source_top].get_item(source_name,
                                                         source_group)
        try:
            self.filter_managers[source_top].remove_item(source_name,
                                                         source_group)
            if target_group:
                self.filter_managers[target_top].add_item(item, source_name,
                                                          target_group)
            else:
                self.filter_managers[target_top].add_item(item, source_name)
        except ValueError as e:
            QMessageBox.critical(self, 'Error moving item', str(e))
            return

        self.filter_managers[target_top].move_item(source_name, above_target,
                                                   target_group)

        self.populate_filter_tree()
        self.filter_populate_function[source_top]()

        self.set_selection_mutex = QMutex()

    # Method injection into the filter tree (to enable custom drag and drop
    # behavior)
    def _filter_drag_move(self, event):
        QAbstractItemView.dragMoveEvent(self.filterTreeWidget, event)
        source = self.filterTreeWidget.currentItem()
        target = self.filterTreeWidget.itemAt(event.pos())
        if not target:
            event.ignore()
            return

        source_top = source.parent()
        if source_top.parent():
            source_top = source_top.parent()
        target_top = target
        if target_top.parent():
            target_top = target_top.parent()
        if target_top.parent():
            target_top = target_top.parent()

        # Drag and Drop is only allowed for the same filter type
        if source_top != target_top:
            event.ignore()
            return

        # Groups can only be dragged to top level
        if source.data(1, Qt.UserRole) == self.FilterTreeRoleGroup:
            if target.data(1, Qt.UserRole) == \
                    self.FilterTreeRoleGroup:
                event.ignore()
                return
            if target.parent() != target_top and target != target_top:
                event.ignore()
                return

        # This strange hack prevents from dragging to root level
        if source_top == target:
            pos = event.pos()
            pos.setY(pos.y() - 2)
            higher_target = self.filterTreeWidget.itemAt(pos)
            if target != higher_target:
                event.ignore()

    # Method injection into the filter tree
    # (to enable custom checkable behavior)
    def _filter_key_released(self, event):
        index = self.filterTreeWidget.currentIndex()
        if index.data(CheckableItemDelegate.CheckTypeRole) and \
                event.key() == Qt.Key_Space:
            self._switch_check_state(index)
            event.accept()
            # Hack to repaint the whole current item:
            self.filterTreeWidget.currentItem().setExpanded(False)
        elif event.key() == Qt.Key_Delete:
            self.on_actionDeleteFilter_triggered()
        else:
            QTreeWidget.keyReleaseEvent(self.filterTreeWidget, event)

    # Method injection into the filter tree
    # (to enable custom checkable behavior)
    def _filter_mouse_released(self, event):
        index = self.filterTreeWidget.indexAt(event.pos())
        if index.data(CheckableItemDelegate.CheckTypeRole) and \
                event.button() == Qt.LeftButton:
            style = QApplication.instance().style()
            radio_button_width = style.pixelMetric(
                QStyle.PM_ExclusiveIndicatorWidth)
            spacing = style.pixelMetric(QStyle.PM_RadioButtonLabelSpacing)

            item = self.filterTreeWidget.itemFromIndex(index)
            ind = 1
            while item.parent():
                ind += 1
                item = item.parent()
            indent = ind * self.filterTreeWidget.indentation()
            if indent < event.x() < indent + radio_button_width + spacing:
                self._switch_check_state(index)
                event.accept()
                # Hack to repaint the whole current item:
                self.filterTreeWidget.currentItem().setExpanded(False)
                return

        QTreeWidget.mouseReleaseEvent(self.filterTreeWidget, event)

    def _get_filter_item_coords(self, item):
        parent = item.parent()
        if parent.parent():
            top = parent.parent().text(0)
            group = parent.text(0)
        else:
            top = parent.text(0)
            group = None

        return top, group

    def _switch_check_state(self, index):
        item = self.filterTreeWidget.itemFromIndex(index)
        top, group = self._get_filter_item_coords(item)

        if index.data(CheckableItemDelegate.CheckTypeRole) == \
                CheckableItemDelegate.CheckBoxCheckType:
            item.setData(0, CheckableItemDelegate.CheckedRole,
                         not index.data(CheckableItemDelegate.CheckedRole))
            f = self.filter_managers[top].get_item(item.text(0), group)
            f.active = item.data(0, CheckableItemDelegate.CheckedRole)
        else:
            parent = item.parent()
            if not parent:
                siblings = (self.filterTreeWidget.topLevelItem(x) for x in
                            xrange(self.filterTreeWidget.topLevelItemCount()))
            else:
                siblings = (parent.child(x) for x in
                            xrange(parent.childCount()))

            for s in siblings:
                s.setData(0, CheckableItemDelegate.CheckedRole, s == item)
                f = self.filter_managers[top].get_item(s.text(0), group)
                f.active = (s == item)

        self.filter_populate_function[top]()

    def filter_group_dict(self):
        """ Return a dictionary with filter groups for each filter type
        """
        d = {}
        for n, m in self.filter_managers.iteritems():
            d[n] = m.list_group_names()
        return d

    def populate_filter_tree(self):
        self.filterTreeWidget.clear()

        for name, manager in sorted(self.filter_managers.items()):
            top = QTreeWidgetItem(self.filterTreeWidget)
            top.setText(0, name)
            top.setFlags(Qt.ItemIsEnabled | Qt.ItemIsDropEnabled)
            top.setData(1, Qt.UserRole, self.FilterTreeRoleTop)
            top.setTextColor(0, Qt.gray)
            top.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
            self.filterTreeWidget.addTopLevelItem(top)
            if manager.list_items():
                top.setExpanded(True)

            for i in manager.list_items():
                if isinstance(i[1], manager.FilterGroup):
                    group = QTreeWidgetItem(top)
                    group.setText(0, i[0])
                    group.setData(1, Qt.UserRole,
                                  self.FilterTreeRoleGroup)
                    group.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable |
                                   Qt.ItemIsDropEnabled |
                                   Qt.ItemIsDragEnabled)
                    group.setChildIndicatorPolicy(
                        QTreeWidgetItem.ShowIndicator)
                    if i[1].list_items():
                        group.setExpanded(True)
                    top.addChild(group)

                    for f in i[1].list_items():
                        item = QTreeWidgetItem(group)
                        item.setText(0, f[0])
                        if f[1].active:
                            item.setData(0, CheckableItemDelegate.CheckedRole,
                                         True)
                        else:
                            item.setData(0, CheckableItemDelegate.CheckedRole,
                                         False)
                        if i[1].exclusive:
                            item.setData(0,
                                         CheckableItemDelegate.CheckTypeRole,
                                         CheckableItemDelegate.RadioCheckType)
                        else:
                            item.setData(0,
                                         CheckableItemDelegate.CheckTypeRole,
                                         CheckableItemDelegate.CheckBoxCheckType)
                        item.setData(1, Qt.UserRole,
                                     self.FilterTreeRoleFilter)
                        item.setFlags(Qt.ItemIsEnabled |
                                      Qt.ItemIsSelectable |
                                      Qt.ItemIsDragEnabled)
                        group.addChild(item)
                else:
                    item = QTreeWidgetItem(top)
                    item.setText(0, i[0])
                    if i[1].active:
                        item.setData(0, CheckableItemDelegate.CheckedRole,
                                     True)
                    else:
                        item.setData(0, CheckableItemDelegate.CheckedRole,
                                     False)
                    item.setData(0, CheckableItemDelegate.CheckTypeRole,
                                 CheckableItemDelegate.CheckBoxCheckType)
                    item.setData(1, Qt.UserRole,
                                 self.FilterTreeRoleFilter)
                    item.setFlags(Qt.ItemIsEnabled |
                                  Qt.ItemIsSelectable |
                                  Qt.ItemIsDragEnabled)
                    top.addChild(item)

    def on_filterTreeWidget_currentItemChanged(self, current):
        enabled = current is not None and \
            current.data(1, Qt.UserRole) != self.FilterTreeRoleTop
        self.actionEditFilter.setEnabled(enabled)
        self.actionDeleteFilter.setEnabled(enabled)
        self.actionCopyFilter.setEnabled(enabled)

    def on_filterTreeWidget_customContextMenuRequested(self, pos):
        self.menuFilter.popup(self.filterTreeWidget.mapToGlobal(pos))

    def save(self):
        for m in self.filter_managers.itervalues():
            m.save()

    def setupUi(self):
        self.filterTreeWidget = QtGui.QTreeWidget(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(3)
        sizePolicy.setHeightForWidth(
            self.filterTreeWidget.sizePolicy().hasHeightForWidth())
        self.filterTreeWidget.setSizePolicy(sizePolicy)
        self.filterTreeWidget.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu)
        self.filterTreeWidget.setDragEnabled(True)
        self.filterTreeWidget.setDragDropMode(
            QtGui.QAbstractItemView.InternalMove)
        self.filterTreeWidget.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.filterTreeWidget.setAlternatingRowColors(False)
        self.filterTreeWidget.setUniformRowHeights(False)
        self.filterTreeWidget.setObjectName("filterTreeWidget")
        self.filterTreeWidget.header().setVisible(False)
        self.setWidget(self.filterTreeWidget)