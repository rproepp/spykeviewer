from PyQt4.QtCore import QTimer

try:
    from IPython.zmq.ipkernel import IPKernelApp
    from IPython.frontend.qt.kernelmanager import QtKernelManager
    from IPython.frontend.qt.console.rich_ipython_widget \
        import RichIPythonWidget
    from IPython.config.application import catch_config_error
    from IPython.lib.kernel import connect_qtconsole

    class IPythonLocalKernelApp(IPKernelApp):
        """ A version of the IPython kernel that does not block the Qt event
            loop.
        """
        @catch_config_error
        def initialize(self, argv=None):
            if argv is None:
                argv = []
            super(IPythonLocalKernelApp, self).initialize(argv)
            self.kernel.eventloop = self.loop_qt4_nonblocking
            self.kernel.start()
            self.start()

        def loop_qt4_nonblocking(self, kernel):
            """ Non-blocking version of the ipython qt4 kernel loop """
            kernel.timer = QTimer()
            kernel.timer.timeout.connect(kernel.do_one_iteration)
            kernel.timer.start(1000 * kernel._poll_interval)

        def get_connection_file(self):
            """ Return current kernel connection file. """
            return self.connection_file

        def get_user_namespace(self):
            """ Returns current kernel userspace dict. """
            return self.kernel.shell.user_ns

    ipython_available = True
except ImportError:
    ipython_available = False
