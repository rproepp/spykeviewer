from PyQt4 import QtCore
from PyQt4.QtGui import QProgressDialog
from spykeutils.progress_indicator import (ProgressIndicator,
                                           CancelException)

class ProgressIndicatorDialog(ProgressIndicator, QProgressDialog):
    """ This class implements
    :class:`~SpikeUtils.progress_indicator.ProgressIndicator` as a
    QProgressDialog. It can be used to indicate progress in a graphical
    user interface. Qt needs to be initialized in order to use it.
    """
    def __init__(self, parent, title='Processing...'):
        QProgressDialog.__init__(self, parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(500)
        self.setAutoReset(False)

    def set_ticks(self, ticks):
        self.setMaximum(ticks)
        if self.isVisible():
            self.setValue(0)

    def begin(self, title='Processing...'):
        self.setWindowTitle(title)
        self.setLabelText('')
        self.setValue(0)

        if not self.isVisible():
            self.reset()
            self.open()

    def step(self, num_steps = 1):
        if not self.isVisible():
            return

        self.setValue(self.value() + num_steps)
        QtCore.QCoreApplication.instance().processEvents()
        if self.wasCanceled():
            self.done()
            raise CancelException()

        super(ProgressIndicatorDialog, self).step()

    def set_status(self, status):
        self.setLabelText(status)

    def done(self):
        self.reset()
