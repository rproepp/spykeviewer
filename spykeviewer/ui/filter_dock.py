import os

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import (QDockWidget, QMessageBox, QAbstractItemView,
                         QTreeWidget, QApplication, QStyle, QTreeWidgetItem)
from PyQt4.QtCore import Qt, pyqtSignal

from ..plugin_framework.filter_manager import FilterManager
from checkable_item_delegate import CheckableItemDelegate


class FilterDock(QDockWidget):
    """ Dock with filter tree. It manages filters of different
    types. They are displayed in a tree view and can be moved using drag
    and drop (only possible within the same filter type). The dock also
    takes care of storing and restoring the filters from disk.

    This dock has two signals:

    * ``current_filter_changed()``: Emitted when the currently selected item
      in the tree view changes.
    * ``filters_changed(str)``: Emitted whenever an action causes the list of
      filtered items to (potentially) change.
    """
    FilterTreeRoleTop = 0
    FilterTreeRoleGroup = 1
    FilterTreeRoleFilter = 2

    current_filter_changed = pyqtSignal()
    filters_changed = pyqtSignal(str)

    def __init__(self, filter_path, type_list, menu=None,
                 title='Filter', parent=None):
        """ Create a new filter dock.

        :param str filter_path: Folder in the filesystem where filters are
            saved and loaded.
        :param list type_list: A list of (str, str) tuples. Each tuple
            describes one filter type. The first element is the name of the
            filter type. It will be displayed and used as parameter in the
            filters_changed callback. The second element is the filename
            that will be used to save and load the filters of this type.
        :param :class:`PyQt4.QtGui.QMenu` menu: A menu that will be displayed
            as context when the tree view is right-clicked.
        :param str title: The title of the dock.
        :param :class:`PyQt4.QtGui.QWidget` parent: The parent of this dock.
        """
        QDockWidget.__init__(self, title, parent)
        self.setupUi()

        self.filter_path = filter_path
        self.menuFilter = menu
        self.filter_managers = {}
        self.type_list = type_list

        self.reload_filters(filter_path)

        self.filterTreeWidget.dragMoveEvent = self._filter_drag_move
        self.filterTreeWidget.dropEvent = self._filter_drag_end
        self.filterTreeWidget.keyReleaseEvent = self._filter_key_released
        self.filterTreeWidget.mouseReleaseEvent = \
            self._filter_mouse_released
        self.filterTreeWidget.setItemDelegate(
            CheckableItemDelegate(self.filterTreeWidget))
        self.filterTreeWidget.currentItemChanged.connect(
            self._current_filter_changed)
        self.filterTreeWidget.customContextMenuRequested.connect(
            self._context_menu)

    def reload_filters(self, filter_path=None):
        """ Reload filters from disk.

        :param str filter_path: Folder in the filesystem where filters are
            saved and loaded. If ``None``, previous filter path is used.
            Default: ``None``
        """
        if filter_path:
            self.filter_path = filter_path

        for t in self.type_list:
            self.filter_managers[t[0]] = FilterManager(
                t[1], os.path.join(filter_path, t[1] + '.py'))
        self.populate_filter_tree()

    def get_active_filters(self, filter_type):
        """ Return currently active filters for a filter type.
        """
        return self.filter_managers[filter_type].get_active_filters()

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
        self.filters_changed.emit(source_top)

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
            self.delete_current_filter()
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

        self.filters_changed.emit(top)

    def current_filter_type(self):
        """ Return the name of the currently selected filter group or filter.
        If nothing is selected, None is returned.
        """
        item = self.filterTreeWidget.currentItem()
        top = None
        if item:
            while item.parent():
                item = item.parent()
            top = item.text(0)

        return top

    def current_filter_group(self):
        """ Return the name of the currently selected filter group. If a
        from inside a group is selected, the name of that group is returned.
        If a group or no item is selected, None is returned.
        """
        item = self.filterTreeWidget.currentItem()
        group = None
        if item:
            parent = item.parent()
            if parent:
                if parent.parent():
                    group = parent.text(0)
                elif item.data(1, Qt.UserRole) == self.FilterTreeRoleGroup:
                    group = item.text(0)

        return group

    def current_name(self):
        """ Return name of currently selected item.
        """
        item = self.filterTreeWidget.currentItem()
        return item.text(0)

    def is_current_group(self):
        """ Return if the currently selected item is a filter group.
        """
        item = self.filterTreeWidget.currentItem()
        return item.data(1, Qt.UserRole) == self.FilterTreeRoleGroup

    def current_item(self):
        """ Returns the current filter or filter group.
        """
        item = self.filterTreeWidget.currentItem()
        top = self.current_filter_type()
        group = None
        if item:
            parent = item.parent()
            if parent:
                if parent.parent():
                    group = parent.text(0)

        return self.filter_managers[top].get_item(item.text(0), group)

    def group_filters(self, filter_type, group_name):
        """ Returns a list of all filters for a given filter group.

        :param str filter_type: Type of the filter group.
        :param str group_name: Name of the group.
        :returns: list
        """
        return self.filter_managers[filter_type].get_group_filters(group_name)

    def filter_group_dict(self):
        """ Return a dictionary with filter groups for each filter type.
        """
        d = {}
        for n, m in self.filter_managers.iteritems():
            d[n] = m.list_group_names()
        return d

    def delete_item(self, filter_type, name, group):
        """ Removes a filter or a filter group.

        :param str name: Name of the item to be removed.
        :param str group: Name of the group to which the item belongs.
            If this is None, a top level item will be removed.
            Default: None
        """
        self.filter_managers[filter_type].remove_item(name, group)

    def delete_current_filter(self):
        """ Removes the current filter. Checks with the user if he really
        wants to remove the filter.
        """
        item = self.filterTreeWidget.currentItem()
        if not item:
            return
        if not item.parent():
            return
            
        if QMessageBox.question(self, 'Please confirm',
                                'Do you really want to delete "%s"?' % item.text(0),
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
            return

        parent = item.parent()
        if parent.parent():
            top = parent.parent().text(0)
            group = parent.text(0)
        else:
            top = parent.text(0)
            group = None

        try:
            self.filter_managers[top].remove_item(item.text(0), group)
        except StandardError as e:
            QMessageBox.critical(self, 'Error removing filter', str(e))
        else:
            self.populate_filter_tree()
            self.filters_changed.emit(top)

    def add_filter(self, name, group, filter_type, code, on_exception,
                   combined, overwrite=False):
        """ Add a new filter.

        :param str name: Name of the new filter.
        :param str group: Name of the group that the new filter belongs to.
            If this is None, the filter will not belong to any group (root
            level). Default: None
        :param str filter_type: The type of the new filter
        :param list code: List of lines of code in the filter function.
        :param bool on_exception: Should the filter return True on an
            exception? Default: ``True``
        :param bool overwrite: If ``True``, an existing filter with the same
            name will be overwritten. If ``False`` and a filter with the
            same name exists, a value error is raised. Default: ``False``
        """
        self.filter_managers[filter_type].add_filter(
            name, code, on_exception=on_exception, group_name=group,
            combined=combined, overwrite=overwrite)
        self.populate_filter_tree()
        self.filters_changed.emit(filter_type)

    def add_filter_group(self, name, filter_type, exclusive, filters=None,
                         overwrite=False):
        """ Add a new filter group.

        :param str name: The name of the new filter group.
        :param str filter_type: The name of the type the filter group belongs to.
        :param bool exclusive: Determines if the new group is exclusive, i.e.
            only one of its items can be active at the same time.
        :param list filters: A list of filter objects that the new filter
            group will contain.
            Default: None
        :param bool overwrite: If ``True``, an existing group with the same
            name will be overwritten. If ``False`` and a group with the same
            name exists, a value error is raised.
            Default : ``False``
        """
        self.filter_managers[filter_type].add_group(
            name, exclusive, group_filters=filters, overwrite=overwrite)
        self.populate_filter_tree()
        self.filters_changed.emit(filter_type)

    def save(self):
        """ Save all filters.
        """
        for m in self.filter_managers.itervalues():
            m.save()

    def populate_filter_tree(self):
        """ Populates the filter tree widget from the filter data. Called
        automatically from other methods when necessary.
        """
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

    def current_is_data_item(self):
        """ Returns if the currently selected item is a filter or a filter
        group.
        """
        current = self.filterTreeWidget.currentItem()
        return current is not None and \
            current.data(1, Qt.UserRole) != self.FilterTreeRoleTop

    def _current_filter_changed(self, current):
        self.current_filter_changed.emit()

    def _context_menu(self, pos):
        if self.menuFilter:
            self.menuFilter.popup(self.filterTreeWidget.mapToGlobal(pos))

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