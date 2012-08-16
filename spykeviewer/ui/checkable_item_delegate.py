from PyQt4.QtCore import Qt
from PyQt4.QtGui import QStyledItemDelegate, QStyle, QApplication

class CheckableItemDelegate(QStyledItemDelegate):
    """ A StyledItemDelegate for checkable items with support for both
    checkboxes and radio buttons.
    """
    CheckTypeRole = Qt.UserRole + 102
    CheckedRole = Qt.UserRole + 103
    CheckBoxCheckType = 1
    RadioCheckType = 2

    def __init__(self, viewWidget):
        QStyledItemDelegate.__init__(self)
        self.viewWidget = viewWidget
        self.counter = 0

    def paint(self, painter, option, index):
        #noinspection PyArgumentList
        style = QApplication.instance().style()

        if index.data(CheckableItemDelegate.CheckTypeRole):
            # Size and spacing in current style
            is_radio = index.data(CheckableItemDelegate.CheckTypeRole) ==\
                       CheckableItemDelegate.RadioCheckType
            if is_radio:
                button_width = style.pixelMetric(
                    QStyle.PM_ExclusiveIndicatorWidth, option)
                spacing = style.pixelMetric(
                    QStyle.PM_RadioButtonLabelSpacing, option)
            else:
                button_width = style.pixelMetric(
                    QStyle.PM_IndicatorWidth, option)
                spacing = style.pixelMetric(
                    QStyle.PM_CheckBoxLabelSpacing, option)


            # Draw default appearance shifted to right
            myOption = option
            left = myOption.rect.left()
            myOption.rect.setLeft(left + spacing + button_width)
            QStyledItemDelegate.paint(self, painter, myOption, index)

            # Draw check button to open space (where expand indicator would be)
            myOption.rect.setLeft(left)
            myOption.rect.setWidth(button_width)

            if index.data(CheckableItemDelegate.CheckedRole):
                myOption.state |=  QStyle.State_On
            else:
                myOption.state |= QStyle.State_Off

            if is_radio:
                style.drawPrimitive(QStyle.PE_IndicatorRadioButton, myOption, painter)
            else:
                style.drawPrimitive(QStyle.PE_IndicatorCheckBox, myOption, painter)
        else:
            QStyledItemDelegate.paint(self, painter, option, index)

    def sizeHint(self, option, index):
        s = QStyledItemDelegate.sizeHint(self, option, index)
        # sizeHint is for some reason only called once, so set
        # size globally
        #if index.data(CheckableItemDelegate.CheckTypeRole):
        #    # Determine size of check buttons in current style
        #    #noinspection PyArgumentList
        #    button_height = QApplication.style().pixelMetric(QStyle.PM_ExclusiveIndicatorHeight, option)
        #    # Ensure that row is tall enough to draw check button
        #    print button_height
        #    s.setHeight(max(s.height(), button_height))
        radio_height = QApplication.style().pixelMetric(
            QStyle.PM_ExclusiveIndicatorHeight, option)
        check_height = QApplication.style().pixelMetric(
            QStyle.PM_IndicatorHeight, option)
        s.setHeight(max(s.height(), radio_height, check_height))
        return s