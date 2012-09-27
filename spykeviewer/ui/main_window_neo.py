import os
from collections import OrderedDict
import logging

import neo

from PyQt4.QtCore import (Qt, pyqtSignature, QThread, QMutex,
                          QSettings)
from PyQt4.QtGui import (QFileSystemModel, QHeaderView, QListWidgetItem,
                         QMessageBox, QTreeWidgetItem, QAbstractItemView,
                         QStyle, QApplication, QTreeWidget, QProgressDialog,
                         QFileDialog, QDesktopServices)

from spykeutils.progress_indicator import ignores_cancel
from spykeutils.spyke_exception import SpykeException
from spykeutils.plugin.data_provider_neo import NeoDataProvider
from spykeutils.plugin.data_provider_stored import NeoStoredProvider
from spykeutils.plugin.analysis_plugin import AnalysisPlugin

from main_window import MainWindow
from settings import SettingsWindow
from filter_dialog import FilterDialog
from filter_group_dialog import FilterGroupDialog
from plugin_editor_dock import PluginEditorDock
from checkable_item_delegate import CheckableItemDelegate
from plugin_model import PluginModel
from ..plugin_framework.data_provider_viewer import NeoViewerProvider
from ..plugin_framework.filter_manager import FilterManager


logger = logging.getLogger('spykeviewer')

#noinspection PyCallByClass,PyTypeChecker,PyArgumentList
class MainWindowNeo(MainWindow):
    """ Implements Neo functionality in the main window
    """
    FilterTreeRoleTop = 0
    FilterTreeRoleGroup = 1
    FilterTreeRoleFilter = 2

    def __init__(self):
        super(MainWindowNeo, self).__init__()

        self.file_system_model = None
        self.block_ids = {}
        self.block_names = OrderedDict() # Just for the display order
        self.block_files = {}
        self.channel_group_names = {}

        # Initialize filter sytem
        self.filter_domain_mappings = {'Block':0, 'Recording Channel':1,
                                       'Recording Channel Group':2,
                                       'Segment':3, 'Unit':4}
        self.filter_populate_function = \
            {'Block':self.populate_neo_block_list,
             'Recording Channel':self.populate_neo_channel_list,
             'Recording Channel Group':self.populate_neo_channel_group_list,
             'Segment':self.populate_neo_segment_list,
             'Unit':self.populate_neo_unit_list}

        settings = QSettings()
        if not settings.contains('filterPath'):
            data_path = QDesktopServices.storageLocation(
                QDesktopServices.DataLocation)
            self.filter_path = os.path.join(data_path, 'filters')
        else:
            self.filter_path = settings.value('filterPath')

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

        # Initialize plugin system
        self.pluginEditorDock = PluginEditorDock()
        self.pluginEditorDock.setObjectName('editorDock')
        self.addDockWidget(Qt.RightDockWidgetArea, self.pluginEditorDock)
        self.pluginEditorDock.setVisible(False)
        self.pluginEditorDock.plugin_saved.connect(self.reload_plugins)
        self.update_view_menu()

        # Initialize Neo navigation
        self.file_system_model = QFileSystemModel()
        self.file_system_model.setRootPath('')
        self.fileTreeView.setModel(self.file_system_model)
        self.fileTreeView.setCurrentIndex(
            self.file_system_model.index(self.dir))
        self.fileTreeView.expand(self.file_system_model.index(self.dir))

        self.fileTreeView.setColumnHidden(1, True)
        self.fileTreeView.setColumnHidden(2, True)
        self.fileTreeView.setColumnHidden(3, True)

        self.fileTreeView.header().setResizeMode(QHeaderView.ResizeToContents)

        self.activate_neo_mode()
        self.restore_state()
        self.reload_plugins()

    def load_current_selection(self):
        current_selection = os.path.join(
            self.selection_path, '.current.sel')
        if os.path.isfile(current_selection):
            self.load_selections_from_file(current_selection)
        else:
            self.populate_selection_menu()

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
                   MainWindowNeo.FilterTreeRoleGroup:
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
        above_target = item_above_target.text(0) if item_above_target\
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
        if source.data(1, Qt.UserRole) == MainWindowNeo.FilterTreeRoleGroup:
            if target.data(1, Qt.UserRole) == \
               MainWindowNeo.FilterTreeRoleGroup:
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
        if index.data(CheckableItemDelegate.CheckTypeRole) and\
           event.key() == Qt.Key_Space:
            self._switch_check_state(index)
            event.accept()
            # Hack to repaint the whole current item:
            self.filterTreeWidget.currentItem().setExpanded(False)
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
                siblings = (self.filterTreeWidget.topLevelItem(x) for x in \
                    xrange(self.filterTreeWidget.topLevelItemCount()))
            else:
                siblings = (parent.child(x) for x in \
                    xrange(parent.childCount()))

            for s in siblings:
                s.setData(0, CheckableItemDelegate.CheckedRole, s == item)
                f = self.filter_managers[top].get_item(s.text(0), group)
                f.active = (s == item)

        self.filter_populate_function[top]()

    def activate_neo_mode(self):
        self.provider = NeoViewerProvider(self)
        self.provider_factory = NeoStoredProvider.from_current_selection
        self.console.interpreter.locals['current'] = self.provider

    def reload_plugins(self):
        old_path = None
        if hasattr(self, 'analysisModel'):
            item = self.neoAnalysesTreeView.currentIndex()
            if item:
                old_path = self.analysisModel.data(item,
                    self.analysisModel.FilePathRole)

        try:
            self.analysisModel = PluginModel()
            for p in self.plugin_paths:
                self.analysisModel.add_path(p)
        except Exception, e:
            QMessageBox.critical(self, 'Error loading plugins', str(e))
            return

        self.neoAnalysesTreeView.setModel(self.analysisModel)

        selected_index = None
        if old_path:
            indices = self.analysisModel.get_indices_for_path(old_path)
            if indices:
                selected_index = indices[0]
                self.neoAnalysesTreeView.setCurrentIndex(selected_index)
        self.neoAnalysesTreeView.expandAll()
        self.neoAnalysesTreeView.selectionModel().currentChanged.connect(
            self.selected_analysis_changed)
        self.selected_analysis_changed(selected_index)

    def get_letter_id(self, id):
        """ Return a name consisting of letters given an integer
        """
        if id < 0:
            return ''

        name = ''
        id += 1
        start = ord('A') - 1
        while id >= 1:
            name += str(chr(start + (id%26)))
            id /= 26
        return name[::-1]


    class LoadWorker(QThread):
        def __init__(self, file_name, indices):
            QThread.__init__(self)
            self.file_name = file_name
            self.indices = indices
            self.blocks = []

        def run(self):
            self.blocks = NeoDataProvider.get_blocks(self.file_name, False)


    @ignores_cancel
    def load_file_callback(self):
        if not self.load_worker:
            self.progress.done()
            return

        # Load worker thread finished
        blocks = self.load_worker.blocks
        if blocks is None:
            logger.error('Could not read file "%s"' %
                          self.load_worker.file_name)

        for block in blocks:
            name = block.name
            if not name or name == 'One segment only':
                name = self.file_system_model.fileName(
                    self.load_worker.indices[0])
            name += ' (%s)' % self.get_letter_id(self.block_index)

            self.block_names[block] = name
            self.block_ids[block] = self.get_letter_id(self.block_index)
            self.block_files[block] = self.load_worker.file_name
            self.block_index += 1

        self.load_progress.reset()
        self.progress.step()

        # Create new load worker thread
        indices = self.load_worker.indices[1:]
        if not indices:
            self.progress.done()
            self.populate_neo_block_list()
            self.load_worker = None
            return

        f = indices[0]
        filepath = self.file_system_model.filePath(f)

        self.load_worker = self.LoadWorker(filepath, indices)
        self.load_progress.setLabelText(filepath)
        self.load_progress.show()
        self.load_worker.finished.connect(self.load_file_callback)
        self.load_worker.terminated.connect(self.load_file_callback)
        self.load_worker.start()

    @ignores_cancel
    def on_neoLoadFilesButton_pressed(self):
        self.neoBlockList.clear()
        self.block_ids.clear()
        self.block_files.clear()
        self.block_names.clear()

        indices = self.fileTreeView.selectedIndexes()
        self.block_index = 0
        self.progress.begin('Loading data files...')
        self.progress.set_ticks(len(indices))

        filepath = self.file_system_model.filePath(indices[0])

        self.load_worker = self.LoadWorker(filepath, indices)
        self.load_progress = QProgressDialog(self.progress)
        self.load_progress.setWindowTitle('Loading File')
        self.load_progress.setLabelText(filepath)
        self.load_progress.setMaximum(0)
        self.load_progress.setCancelButton(None)
        self.load_worker.finished.connect(self.load_file_callback)
        self.load_worker.terminated.connect(self.load_file_callback)
        self.load_progress.show()
        self.load_worker.start()

    def on_fileTreeView_doubleClicked(self, index):
        self.on_neoLoadFilesButton_pressed()

    def is_filtered(self, item, filters):
        """ Return if one of the filter functions in the given list
        applies to the given item
        """
        for f in filters:
            try:
                if not f.function()(item):
                    return True
            except Exception:
                if not f.on_exception:
                    return True
        return False

    def populate_neo_block_list(self):
        """ Fill the block list with appropriate entries.
            Qt.UserRole: The block itself
        """
        self.neoBlockList.clear()

        filters = self.filter_managers['Block'].get_active_filters()

        for b,n in self.block_names.iteritems():
            if self.is_filtered(b, filters):
                continue

            item = QListWidgetItem(n)
            item.setData(Qt.UserRole, b)
            self.neoBlockList.addItem(item)

        self.neoBlockList.setCurrentRow(0)

    def neo_blocks(self):
        return [t.data(Qt.UserRole) for t in
                self.neoBlockList.selectedItems()]

    def neo_block_file_names(self):
        """ Return a dictionary of filenames, indexed by blocks
        """
        return self.block_files

    def populate_neo_segment_list(self):
        self.neoSegmentList.clear()

        filters = self.filter_managers['Segment'].get_active_filters()

        for item in self.neoBlockList.selectedItems():
            block = item.data(Qt.UserRole)

            for i,s in enumerate(block.segments):
                if self.is_filtered(s, filters):
                    continue

                if s.name:
                    name = s.name + ' (%s-%i)' % (self.block_ids[s.block], i)
                else:
                    name = '%s-%i' % (self.block_ids[s.block], i)

                new_item = QListWidgetItem(name)
                new_item.setData(Qt.UserRole, s)
                self.neoSegmentList.addItem(new_item)

        self.neoSegmentList.setCurrentRow(0)

    def neo_segments(self):
        return [t.data(Qt.UserRole) for t in
                self.neoSegmentList.selectedItems()]

    def populate_neo_channel_group_list(self):
        self.neoChannelGroupList.clear()
        self.channel_group_names.clear()

        filters = self.filter_managers[
                  'Recording Channel Group'].get_active_filters()

        for item in self.neoBlockList.selectedItems():
            block = item.data(Qt.UserRole)

            for i,rcg in enumerate(block.recordingchannelgroups):
                if self.is_filtered(rcg, filters):
                    continue

                self.channel_group_names[rcg] = '%s-%i' % (
                    self.block_ids[rcg.block], i)
                if rcg.name:
                    name =  rcg.name + ' (%s)' % self.channel_group_names[rcg]
                else:
                    name = self.channel_group_names[rcg]
                new_item = QListWidgetItem(name)
                new_item.setData(Qt.UserRole, rcg)
                self.neoChannelGroupList.addItem(new_item)

        self.neoChannelGroupList.setCurrentRow(0)

    def neo_channel_groups(self):
        return [t.data(Qt.UserRole) for t in
                self.neoChannelGroupList.selectedItems()]

    def populate_neo_unit_list(self):
        self.neoUnitList.clear()

        filters = self.filter_managers['Unit'].get_active_filters()

        for item in self.neoChannelGroupList.selectedItems():
            rcg = item.data(Qt.UserRole)

            for i,u in enumerate(rcg.units):
                if self.is_filtered(u, filters):
                    continue
                if u.name:
                    name = u.name + ' (%s-%d)' %\
                                    (self.channel_group_names[rcg], i)
                else:
                    name = '%s-%d' % (self.channel_group_names[rcg], i)
                new_item = QListWidgetItem(name)
                new_item.setData(Qt.UserRole, u)
                self.neoUnitList.addItem(new_item)

    def neo_units(self):
        return [t.data(Qt.UserRole) for t in
                self.neoUnitList.selectedItems()]

    def populate_neo_channel_list(self):
        """ Fill the channel list with appropriate entries. There is only
            one entry for each channel index. Data slots:
            Qt.UserRole: The channel index
            Qt.UserRole+1: A list of channels with this index
        """
        self.neoChannelList.clear()

        channel_manager = self.filter_managers['Recording Channel']
        filters = channel_manager.get_active_filters()

        for item in self.neoChannelGroupList.selectedItems():
            channel_group = item.data(Qt.UserRole)

            for rc in channel_group.recordingchannels:
                if self.is_filtered(rc, filters):
                    continue

                identifier = '%s.%d' %\
                             (self.channel_group_names[channel_group],
                              rc.index)
                if rc.name:
                    name = rc.name + ' (%s)' % identifier
                else:
                    name = identifier
                new_item = QListWidgetItem(name)
                new_item.setData(Qt.UserRole, rc)
                new_item.setData(Qt.UserRole+1, rc.index)
                self.neoChannelList.addItem(new_item)
                self.neoChannelList.setItemSelected(new_item, True)

    def neo_channels(self):
        return [t.data(Qt.UserRole) for t in
                self.neoChannelList.selectedItems()]

    def on_neoBlockList_itemSelectionChanged(self):
        self.populate_neo_channel_group_list()
        self.populate_neo_segment_list()

    def on_neoChannelGroupList_itemSelectionChanged(self):
        self.populate_neo_channel_list()
        self.populate_neo_unit_list()

    def on_neoBlockList_itemDoubleClicked(self, item):
        print item.data(Qt.UserRole).annotations

    def on_neoSegmentList_itemDoubleClicked(self, item):
        print item.data(Qt.UserRole).annotations

    def on_neoChannelGroupList_itemDoubleClicked(self, item):
        print item.data(Qt.UserRole).annotations

    def on_neoChannelList_itemDoubleClicked(self, item):
        print item.data(Qt.UserRole).annotations

    def on_neoUnitList_itemDoubleClicked(self, item):
        print item.data(Qt.UserRole).annotations

    def selected_analysis_changed(self, current):
        enabled = True
        if not current:
            enabled = False
        elif not self.analysisModel.data(current, Qt.UserRole):
            enabled = False

        self.actionRunPlugin.setEnabled(enabled)
        self.actionEditPlugin.setEnabled(enabled)
        self.actionConfigurePlugin.setEnabled(enabled)
        self.actionRemotePlugin.setEnabled(enabled)

    def current_plugin(self):
        item = self.neoAnalysesTreeView.currentIndex()
        if not item:
            return None

        return self.analysisModel.data(item, self.analysisModel.DataRole)

    def current_plugin_path(self):
        item = self.neoAnalysesTreeView.currentIndex()
        if not item:
            return None

        return self.analysisModel.data(item, self.analysisModel.FilePathRole)

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
            top.setData(1, Qt.UserRole, MainWindowNeo.FilterTreeRoleTop)
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
                        MainWindowNeo.FilterTreeRoleGroup)
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
                            MainWindowNeo.FilterTreeRoleFilter)
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
                        MainWindowNeo.FilterTreeRoleFilter)
                    item.setFlags(Qt.ItemIsEnabled |
                                  Qt.ItemIsSelectable |
                                  Qt.ItemIsDragEnabled)
                    top.addChild(item)

    def on_filterTreeWidget_currentItemChanged(self, current):
        enabled = current is not None and \
            current.data(1, Qt.UserRole) != MainWindowNeo.FilterTreeRoleTop
        self.actionEditFilter.setEnabled(enabled)
        self.actionDeleteFilter.setEnabled(enabled)
        self.actionCopyFilter.setEnabled(enabled)

    def on_filterTreeWidget_customContextMenuRequested(self, pos):
        self.menuFilter.popup(self.filterTreeWidget.mapToGlobal(pos))

    @pyqtSignature("")
    def on_actionNewFilter_triggered(self):
        item = self.filterTreeWidget.currentItem()
        top = None
        group = None
        if item:
            parent = item.parent()
            if parent:
                if parent.parent():
                    top = parent.parent().text(0)
                    group = parent.text(0)
                else:
                    top = parent.text(0)
                    group = item.text(0)
            else:
                top = item.text(0)
                group = None

        dialog = FilterDialog(self.filter_group_dict(), type=top,
            group=group, parent=self)
        while dialog.exec_():
            try:
                self.filter_managers[dialog.type()].add_filter(dialog.name(),
                    dialog.code(), on_exception=dialog.on_exception(),
                    group_name=dialog.group())
                break
            except ValueError as e:
                QMessageBox.critical(self, 'Error creating filter', str(e))

        if dialog.result() == FilterDialog.Accepted:
            self.filters_changed = True
            self.populate_filter_tree()
            self.filter_populate_function[dialog.type()]()

    @pyqtSignature("")
    def on_actionDeleteFilter_triggered(self):
        item = self.filterTreeWidget.currentItem()
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
            self.filters_changed = True
            self.populate_filter_tree()
            self.filter_populate_function[top]()

    @pyqtSignature("")
    def on_actionEditFilter_triggered(self):
        self.editFilter(False)

    @pyqtSignature("")
    def on_actionCopyFilter_triggered(self):
        self.editFilter(True)

    def editFilter(self, copy):
        item = self.filterTreeWidget.currentItem()

        parent = item.parent()
        if parent.parent():
            top = parent.parent().text(0)
            group = parent.text(0)
        else:
            top = parent.text(0)
            group = None
        group_items = None
        if item.data(1, Qt.UserRole) == MainWindowNeo.FilterTreeRoleGroup:
            group_items = self.filter_managers[top].get_group_filters(
                item.text(0))

        if group_items is None:
            f = self.filter_managers[top].get_item(item.text(0), group)
            dialog = FilterDialog(self.filter_group_dict(), top, group,
                item.text(0),
                f.code, f.on_exception, self)
        else:
            g = self.filter_managers[top].get_item(item.text(0))
            dialog = FilterGroupDialog(top, item.text(0), g.exclusive, self)

        while dialog.exec_():
            try:
                if not copy and item.text(0) != dialog.name():
                    self.filter_managers[top].remove_item(item.text(0), group)
                if item.data(1, Qt.UserRole) == \
                   MainWindowNeo.FilterTreeRoleFilter:
                    self.filter_managers[top].add_filter(dialog.name(),
                        dialog.code(), on_exception=dialog.on_exception(),
                        group_name=dialog.group(), overwrite=True)
                else:
                    self.filter_managers[top].add_group(dialog.name(),
                        dialog.exclusive(), group_items, overwrite=True)
                break
            except ValueError as e:
                QMessageBox.critical(self, 'Error saving filter', str(e))

        if dialog.result() == FilterDialog.Accepted:
            self.filters_changed = True
            self.populate_filter_tree()
            self.filter_populate_function[top]()

    @pyqtSignature("")
    def on_actionNewFilterGroup_triggered(self):
        item = self.filterTreeWidget.currentItem()
        top = None
        if item:
            while item.parent():
                item = item.parent()
            top = item.text(0)

        dialog = FilterGroupDialog(top, parent=self)
        while dialog.exec_():
            try:
                self.filter_managers[dialog.type()].add_group(dialog.name(),
                    dialog.exclusive())
                break
            except ValueError as e:
                QMessageBox.critical(self, 'Error creating group', str(e))

        if dialog.result() == FilterDialog.Accepted:
            self.filters_changed = True
            self.populate_filter_tree()

    @pyqtSignature("")
    def on_actionClearCache_triggered(self):
        NeoDataProvider.clear()

        self.neoBlockList.clear()
        self.block_ids.clear()
        self.block_files.clear()
        self.block_names.clear()

        self.populate_neo_block_list()

    def closeEvent(self, event):
        """ Saves all filters and plugins before closing
        """
        if not self.pluginEditorDock.close_all():
            event.ignore()
        else:
            data_path = QDesktopServices.storageLocation(
                QDesktopServices.DataLocation)
            filter_path = os.path.join(data_path, 'filters')
            # Ensure that filters folder exists
            if not os.path.exists(filter_path):
                try:
                    os.makedirs(filter_path)
                except OSError:
                    QMessageBox.critical(self, 'Error',
                        'Could not create filter directory!')
            for m in self.filter_managers.itervalues():
                m.save()
            event.accept()
            super(MainWindowNeo, self).closeEvent(event)

            # Prevent lingering threads
            self.fileTreeView.setModel(None)
            del self.file_system_model
            self.neoAnalysesTreeView.setModel(None)
            del self.analysisModel

    def add_neo_selection(self, data):
        """ Adds a new neo selection provider with the given data
        """
        self.selections.append(NeoStoredProvider(data, self.progress))

    def set_neo_selection(self, data):
        """ Sets the current selection according to the given provider data
        """
        self.progress.begin('Loading selection data...')
        self.progress.set_ticks(len(data['blocks']))

        # Load blocks which are not currently displayed
        i = len(self.block_names)
        for b in data['blocks']:
            # File already loaded?
            if unicode(b[1]) in self.block_files.values():
                self.progress.step()
                continue

            QApplication.setOverrideCursor(Qt.WaitCursor)
            blocks = NeoDataProvider.get_blocks(b[1], False)
            QApplication.restoreOverrideCursor()
            if not blocks:
                logger.error('Could not read file "%s"' % b[1])
                self.progress.step()
                continue

            for block in blocks:
                name = block.name
                if not name or name == 'One segment only':
                    name = os.path.basename(b[1])
                name += ' (%s)' % self.get_letter_id(i)

                self.block_names[block] = name
                self.block_ids[block] = self.get_letter_id(i)
                self.block_files[block] = b[1]
                i += 1

            self.progress.step()

        self.progress.done()

        self.populate_neo_block_list()

        block_list = [NeoDataProvider.get_block(b[1], b[0], False)
                      for b in data['blocks']]
        rcg_list = [block_list[rcg[1]].recordingchannelgroups[rcg[0]]
                        for rcg in data['channel_groups']]

        # Select blocks
        for i in self.neoBlockList.findItems('*',
            Qt.MatchWrap | Qt.MatchWildcard):
            block = i.data(Qt.UserRole)
            t = [NeoDataProvider.block_indices[block],
                 self.block_files[block]]
            i.setSelected(t in data['blocks'])

        # Select segments
        for i in self.neoSegmentList.findItems('*',
            Qt.MatchWrap | Qt.MatchWildcard):
            segment = i.data(Qt.UserRole)
            if not segment.block in block_list:
                i.setSelected(False)
                continue

            seg_idx = segment.block.segments.index(segment)
            block_idx = block_list.index(segment.block)
            i.setSelected([seg_idx, block_idx] in data['segments'])

        # Select recording channel groups
        for i in self.neoChannelGroupList.findItems('*',
            Qt.MatchWrap | Qt.MatchWildcard):
            rcg = i.data(Qt.UserRole)
            if not rcg.block in block_list:
                i.setSelected(False)
                continue

            rcg_idx = rcg.block.recordingchannelgroups.index(rcg)
            block_idx = block_list.index(rcg.block)
            i.setSelected([rcg_idx, block_idx] in data['channel_groups'])

        # Select channels
        rcg_set = set(rcg_list)
        for i in self.neoChannelList.findItems('*',
            Qt.MatchWrap | Qt.MatchWildcard):
            i.setSelected(False)
            channel = i.data(Qt.UserRole)
            if not set(channel.recordingchannelgroups).intersection(rcg_set):
                continue

            for rcg in channel.recordingchannelgroups:
                if [rcg.recordingchannels.index(channel),
                    rcg_list.index(rcg)] in data['channels']:
                    i.setSelected(True)
                    break

        # Select units
        for i in self.neoUnitList.findItems('*',
            Qt.MatchWrap | Qt.MatchWildcard):
            unit = i.data(Qt.UserRole)
            if unit.recordingchannelgroup not in rcg_list:
                i.setSelected(False)
                continue

            rcg_idx = rcg_list.index(unit.recordingchannelgroup)
            unit_idx = unit.recordingchannelgroup.units.index(unit)
            i.setSelected([unit_idx, rcg_idx] in data['units'])


    class SaveWorker(QThread):
        def __init__(self, file_name, block):
            QThread.__init__(self)
            self.file_name = file_name
            self.block = block
            self.io = None
            self.terminated.connect(self.cleanup)
            self.finished.connect(self.cleanup)

        def run(self):
            self.io = neo.io.hdf5io.NeoHdf5IO(filename=self.file_name)
            self.io.save(self.block)

        def cleanup(self):
            if self.io:
                self.io.close()
                self.io = None


    @pyqtSignature("")
    def on_actionSave_data_triggered(self):
        d = QFileDialog(self, 'Choose where to save selected data')
        d.setAcceptMode(QFileDialog.AcceptSave)
        d.setNameFilter("HDF5 files (*.h5)")
        d.setDefaultSuffix('h5')
        d.setConfirmOverwrite(False) # No overwrites, just append to HDF5
        if d.exec_():
            file_name = unicode(d.selectedFiles()[0])
        else:
            return

        self.progress.begin('Collecting data to save...')
        block = self.provider.selection_blocks()[0]
        self.progress.set_ticks(0)
        self.progress.setWindowTitle('Writing data...')
        self.progress.set_status('')
        self.worker = self.SaveWorker(file_name, block)
        self.worker.finished.connect(self.progress.done)
        self.progress.canceled.connect(self.worker.terminate)
        self.worker.start()

    def on_refreshAnalysesButton_pressed(self):
        self.reload_plugins()

    @pyqtSignature("")
    def on_actionSettings_triggered(self):
        settings = SettingsWindow(self.selection_path, self.filter_path,
            AnalysisPlugin.data_dir, self.remote_script, self.plugin_paths,
            self)

        if settings.exec_() == settings.Accepted:
            self.selection_path = settings.selection_path()
            self.filter_path = settings.filter_path()
            self.remote_script = settings.remote_script()
            self.plugin_paths = settings.plugin_paths()
            self.reload_plugins()

    @pyqtSignature("")
    @ignores_cancel
    def on_actionRunPlugin_triggered(self):
        ana = self.current_plugin()
        if not ana:
            return

        try:
            ana.start(self.provider, self.selections)
        except SpykeException, err:
            self.progress.done()
            QMessageBox.critical(self, 'Error executing analysis', str(err))

    def on_neoAnalysesTreeView_doubleClicked(self, index):
        self.on_actionRunPlugin_triggered()

    @pyqtSignature("")
    def on_actionEditPlugin_triggered(self):
        item = self.neoAnalysesTreeView.currentIndex()
        path = ''
        if item:
            path = self.analysisModel.data(item,
                self.analysisModel.FilePathRole)
        if not path and self.plugin_paths:
            path = self.plugin_paths[0]
        self.pluginEditorDock.add_file(path)

    @pyqtSignature("")
    def on_actionConfigurePlugin_triggered(self):
        ana = self.current_plugin()
        if not ana:
            return

        ana.configure()

    @pyqtSignature("")
    def on_actionRefreshPlugins_triggered(self):
        self.reload_plugins()

    @pyqtSignature("")
    def on_actionNewPlugin_triggered(self):
        path = ''
        if self.plugin_paths:
            path = self.plugin_paths[0]
        self.pluginEditorDock.add_file(path)

    @pyqtSignature("")
    def on_actionSavePlugin_triggered(self):
        self.pluginEditorDock.save_current()

    @pyqtSignature("")
    def on_actionRemotePlugin_triggered(self):
        import subprocess
        import pickle
        selections = self.serialize_selections()
        config = pickle.dumps(self.current_plugin().get_parameters())
        f = open(self.remote_script, 'r')
        code = f.read()
        subprocess.Popen(['python', '-c', '%s' % code,
                          type(self.current_plugin()).__name__,
                          self.current_plugin_path(),
                          selections, '-cf', '-c', config])

    def on_neoAnalysesTreeView_customContextMenuRequested(self, pos):
        self.menuPlugins.popup(self.neoAnalysesTreeView.mapToGlobal(pos))