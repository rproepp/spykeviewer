from spykeviewer.plugin_framework.analysis_plugin import AnalysisPlugin

from spykeutils.plot.sde import sde

import quantities as pq
import guidata.dataset.datatypes as dt
import guidata.dataset.dataitems as di
from PyQt4.Qt import QMessageBox

# Needed for activatable parameters
stop_prop = dt.ValueProp(False)
align_prop = dt.ValueProp(False)
optimize_prop = dt.ValueProp(False)

class SDEPlugin(AnalysisPlugin):
    """ Spike Train Density Plugin
    """
    # Configurable parameters
    kernel_size = di.FloatItem('Kernel size', min=1.0, default=500.0,
        unit='ms')
    start_time = di.FloatItem('Start time', default=0.0, unit='ms')

    stop_enabled = di.BoolItem('Stop time enabled',
        default=False).set_prop('display', store=stop_prop)
    stop = di.FloatItem('Time', default=10001.0,
        unit='ms').set_prop('display', active=stop_prop)

    align_enabled = di.BoolItem('Alignment event enabled',
        default=False).set_prop('display', store=align_prop)
    align = di.StringItem('Event label',
        default='lastSt').set_prop('display', active=align_prop)

    _g = dt.BeginGroup('Kernel width optimization')
    optimize_enabled = di.BoolItem('Enabled',
        default=False).set_prop('display', store=optimize_prop)
    minimum_kernel = di.FloatItem('Minimum kernel size', default=10.0,
        unit='ms', min=0.5).set_prop('display', active=optimize_prop)
    maximum_kernel = di.FloatItem('Maximum kernel size', default=500.0,
        unit='ms', min=1.0).set_prop('display', active=optimize_prop)
    optimize_steps = di.IntItem('Kernel size steps', default=20,
        min=2).set_prop('display', active=optimize_prop)
    _g_ = dt.EndGroup('Kernel size optimization')

    def __init__(self):
        super(SDEPlugin, self).__init__()
        self.unit = pq.ms

    def get_name(self):
        return 'Spike Density Estimation'

    def start(self, current, selections):
        current.progress.begin()
        current.progress.set_status('Reading spike trains')

        # Prepare quantities
        start = float(self.start_time) * self.unit
        stop = None
        if self.stop_enabled:
            stop = float(self.stop) * self.unit
        kernel_size = float(self.kernel_size) * self.unit
        optimize_steps = 0
        if self.optimize_enabled:
            optimize_steps = self.optimize_steps
        minimum_kernel = self.minimum_kernel * self.unit
        maximum_kernel = self.maximum_kernel * self.unit

        # Load data
        trains = current.spike_trains_by_unit_and_segment()
        if self.align_enabled:
            events = current.labeled_events(self.align)
        else:
            events = None

        sde(trains, events, start, stop, kernel_size, optimize_steps, 
            minimum_kernel, maximum_kernel, self.unit, current.progress)

    def configure(self):
        super(SDEPlugin, self).configure()
        while self.optimize_enabled and \
              self.maximum_kernel <= self.minimum_kernel:
            QMessageBox.warning(None, 'Unable to set parameters',
                'Maximum kernel size needs to be larger than ' +
                'minimum kernel size!')
            super(SDEPlugin, self).configure()