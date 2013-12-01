import sys
import logging

ipython_available = False
try:  # Ipython 0.12, 0.13
    import IPython
    from IPython.zmq.ipkernel import IPKernelApp
    from IPython.frontend.qt.kernelmanager import QtKernelManager
    from IPython.frontend.qt.console.rich_ipython_widget \
        import RichIPythonWidget
    from IPython.lib.kernel import find_connection_file
    from PyQt4.QtCore import QTimer
    import atexit

    class LocalKernelApp(IPKernelApp):
        def initialize(self, argv=None):
            if argv is None:
                argv = []

            super(LocalKernelApp, self).initialize(argv)
            self.kernel.eventloop = self.loop_qt4_nonblocking
            self.kernel.start()
            self.start()

        def loop_qt4_nonblocking(self, kernel):
            """ Non-blocking version of the ipython qt4 kernel loop """
            kernel.timer = QTimer()
            kernel.timer.timeout.connect(kernel.do_one_iteration)
            kernel.timer.start(1000 * kernel._poll_interval)

        def push(self, d):
            for k, v in d.iteritems():
                self.kernel.shell.user_ns[k] = v

    class IPythonConnection():
        def __init__(self):
            self._stdout = sys.stdout
            self._stderr = sys.stderr
            self._dishook = sys.displayhook
            sys.stderr = sys.__stderr__  # Prevent message on kernel creation

            self.kernel_app = LocalKernelApp.instance()
            self.kernel_app.initialize()

            sys.stdout = self._stdout
            sys.stderr = self._stderr
            sys.displayhook = self._dishook

        def get_widget(self, droplist_completion=True):
            if IPython.__version__ < '0.13':
                completion = droplist_completion
            else:
                completion = 'droplist' if droplist_completion else 'plain'
            widget = RichIPythonWidget(gui_completion=completion)

            cf = find_connection_file(self.kernel_app.connection_file)
            km = QtKernelManager(connection_file=cf, config=widget.config)
            km.load_connection_file()
            km.start_channels()
            widget.kernel_manager = km
            atexit.register(km.cleanup_connection_file)

            sys.stdout = self._stdout
            sys.stderr = self._stderr
            sys.displayhook = self._dishook

            return widget

        def push(self, d):
            self.kernel_app.push(d)

    ipython_available = True
except ImportError:
    try:  # Ipython >= 1.0
        from IPython.qt.inprocess import QtInProcessKernelManager
        from IPython.qt.console.rich_ipython_widget import RichIPythonWidget

        class IPythonConnection():
            def __init__(self):
                self.kernel_manager = QtInProcessKernelManager()
                self.kernel_manager.start_kernel()
                self.kernel = self.kernel_manager.kernel
                self.kernel.gui = 'qt4'

                self.kernel_client = self.kernel_manager.client()
                self.kernel_client.start_channels()

                # Suppress debug messages
                self.kernel.log.setLevel(logging.WARNING)

            def get_widget(self, droplist_completion=True):
                completion = 'droplist' if droplist_completion else 'plain'
                widget = RichIPythonWidget(gui_completion=completion)
                widget.kernel_manager = self.kernel_manager
                widget.kernel_client = self.kernel_client

                return widget

            def push(self, d):
                self.kernel.shell.push(d)

        ipython_available = True
    except ImportError:
        pass

