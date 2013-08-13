from PyQt4.QtCore import SIGNAL, QThread


class RemoteThread(QThread):
    """ A thread to catch either stdout or stderr of a remote process.
    Emits a signal ``output(id, message)`` whenever the remote process
    writes an output line and ``execution_complete(id)`` when the process
    exits.
    """
    def __init__(self, process, id_code, err, parent=None):
        QThread.__init__(self, parent)
        self.id = id_code
        self.err = err
        self.process = process

    def run(self):
        if self.err:
            it = iter(self.process.stderr.readline, b'')
            for line in it:
                self.emit(SIGNAL('output(int, QString)'),
                          self.id, line.rstrip().decode('ascii'))
        else:
            it = iter(self.process.stdout.readline, b'')
            for line in it:
                self.emit(SIGNAL('output(int, QString)'),
                          self.id, line.rstrip().decode('ascii'))
        self.emit(SIGNAL('execution_complete(int)'), self.id)