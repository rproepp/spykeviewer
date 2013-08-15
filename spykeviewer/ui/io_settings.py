from guidata.qt.QtCore import SIGNAL, SLOT
from PyQt4.QtGui import QVBoxLayout, QDialog, QDialogButtonBox, QMessageBox

from guidata.dataset.datatypes import DataSet
from guidata.dataset.dataitems import (FloatItem, IntItem, BoolItem,
                                       ChoiceItem, StringItem)

from guidata.dataset.qtwidgets import DataSetEditGroupBox, DataSetEditLayout

from guidata.dataset.qtitemwidgets import LineEditWidget


class IntOrNoneItem(IntItem):
    """ Like the normal guidata IntItem, but allows empty input
    that is interpreted as None.
    """
    def check_value(self, value):
        #raise Exception
        if value is None:
            return True
        return super(IntOrNoneItem, self).check_value(value)

    def from_string(self, value):
        if value == 'None' or value == '':  # None is allowed
            return None

        ret = super(IntOrNoneItem, self).from_string(value)
        if ret is None:  # But None from super is an error
            return 'Error'
        return ret


class FloatOrNoneItem(FloatItem):
    """ Like the normal guidata FloatItem, but allows empty input
    that is interpreted as None.
    """
    def check_value(self, value):
        #raise Exception
        if value is None:
            return True
        return super(FloatOrNoneItem, self).check_value(value)

    def from_string(self, value):
        if value == 'None' or value == '':  # None is allowed
            return None

        ret = super(FloatOrNoneItem, self).from_string(value)
        if ret is None:  # But None from super is an error
            return 'Error'
        return ret

DataSetEditLayout.register(IntOrNoneItem, LineEditWidget)
DataSetEditLayout.register(FloatOrNoneItem, LineEditWidget)


def valid_params(params):
    if not params:
        return False
    if not params.values()[0]:
        return False
    return True


def has_ui_params(io):
    if valid_params(io.read_params):
        return True
    return valid_params(io.write_params)


class ParamDialog(QDialog):
    """ A Dialog with read and write option for a Neo IO.
    """
    def __init__(self, io, params_read, params_write, parent):
        super(ParamDialog, self).__init__(parent)

        self.setWindowTitle('Options for %s' % (io.name or io.__name__))
        self.io = io

        self.setModal(True)
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.connect(buttons, SIGNAL("accepted()"), SLOT("accept()"))
        self.connect(buttons, SIGNAL("rejected()"), SLOT("reject()"))

        self.read_params_edit = None
        self.read_params = params_read
        if valid_params(io.read_params):
            params = self.neo_to_guidata(io.read_params.values()[0], self.read_params)
            self.read_params_edit = DataSetEditGroupBox(
                "Read", params, show_button=False)
            self.mainLayout.addWidget(self.read_params_edit)

        self.write_params_edit = None
        self.write_params = params_write
        if valid_params(io.write_params):
            params = self.neo_to_guidata(io.write_params.values()[0], self.write_params)
            self.write_params_edit = DataSetEditGroupBox(
                "Write", params, show_button=False)
            self.mainLayout.addWidget(self.write_params_edit)

        self.mainLayout.addWidget(buttons)

    def neo_to_guidata(self, paramlist, param_dict):
        """ Take a list of parameter description in Neo format and return
        a respective guidata DataSet.

        :param list paramlist: List of (name, parameters) tuples that describe
            load or save parameters Neo style.
        :param dict param_dict: Dictionary with default values. Is modified to
            include new default values when the respective parameter is not
            present.
        """
        # Normal widgets
        guidata_types = {
            bool: BoolItem,
            float: FloatItem,
            int: IntItem,
            str: StringItem,
            unicode: StringItem
        }
        # Widgets where parameter can be None
        guidata_types_with_none = {
            bool: BoolItem,
            float: FloatOrNoneItem,
            int: IntOrNoneItem,
            str: StringItem,
            unicode: StringItem
        }

        # Build up parameter items dictionary
        items = {}
        for name, params in paramlist:
            if 'label' in params:
                label = params['label']
            else:
                label = name

            if name in param_dict:
                default = param_dict[name]
            else:
                if 'value' in params:
                    default = params['value']
                else:
                    default = None

            if 'type' in params:
                if default is None:
                    classitem = guidata_types_with_none[params['type']]
                else:
                    classitem = guidata_types[params['type']]
            else:
                if default is None:
                    classitem = guidata_types_with_none[type(default)]
                else:
                    classitem = guidata_types[type(default)]

            if 'possible' in params:
                possible = params['possible'][:]
                for i, p in enumerate(possible):
                    if possible[i] == ' ':
                        possible[i] = 'Space'
                    elif possible[i] == '\t':
                        possible[i] = 'Tab'

                def_choice = 0
                if name in param_dict and name in params['possible']:
                    def_choice = params['possible'].index(param_dict[name])
                elif default in params['possible']:
                    def_choice = params['possible'].index(default)
                items[name] = ChoiceItem(label, possible,
                                         default=def_choice)
            else:
                items[name] = classitem(label, default=default)
            if name not in param_dict:
                param_dict[name] = default

        guidata_class = type('Parameters', (DataSet,), items)
        return guidata_class

    def accept(self):
        """ Validate inputs """
        ok = True
        if self.read_params_edit:
            if self.read_params_edit.edit.check_all_values():
                self.read_params_edit.edit.accept_changes()
            else:
                ok = False

        if self.write_params_edit:
            if self.write_params_edit.edit.check_all_values():
                self.write_params_edit.edit.accept_changes()
            else:
                ok = False

        if not ok:
            QMessageBox.warning(self, 'Invalid parameters',
                                "Some required entries are incorrect.\n",
                                "Please check highlighted fields.")
        else:
            QDialog.accept(self)

    def _get_choice_value(self, name, value, params):
        """ Make sure that a parameter value is the actual value, not an index
        into the choises for parameters with a list of possible values.
        """
        for n, d in params.values()[0]:
            if name != n:
                continue
            if not 'possible' in d:
                return value
            return d['possible'][value]

        # Should not happen, just return original value
        return value

    def get_read_params(self):
        """ Return a dictionary of read parameter values suitable for passing
        to Neo IO read function.
        """
        d = {}
        for name in self.read_params.iterkeys():
            d[name] = self._get_choice_value(
                name, getattr(self.read_params_edit.dataset, name),
                self.io.read_params)
        return d

    def get_write_params(self):
        """ Return a dictionary of write parameter values suitable for passing
        to Neo IO write function.
        """
        d = {}
        for name in self.write_params.iterkeys():
            d[name] = self._get_choice_value(
                name, getattr(self.write_params_edit.dataset, name,),
                self.io.write_params)
        return d