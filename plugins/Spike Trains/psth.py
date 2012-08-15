from spykeviewer.plugin_framework.analysis_plugin import AnalysisPlugin
from spykeutils.plot.psth import psth

import quantities as pq
import guidata.dataset.datatypes as dt
import guidata.dataset.dataitems as di
from PyQt4.Qt import QMessageBox

# Needed for activatable parameters
stop_prop = dt.ValueProp(False)
align_prop = dt.ValueProp(False)
optimize_prop = dt.ValueProp(False)

class PSTHPlugin(AnalysisPlugin):
    """ PSTH Plugin
    """
    # Configurable parameters
    bin_size = di.FloatItem('Bin size', min=1.0, default=500.0, unit='ms')
    start_time = di.FloatItem('Start time', default=0.0, unit='ms')

    stop_enabled = di.BoolItem('Stop time enabled',
        default=False).set_prop('display', store=stop_prop)
    stop = di.FloatItem('Time', default=10001.0,
        unit='ms').set_prop('display', active=stop_prop)

    align_enabled = di.BoolItem('Alignment event enabled',
        default=False).set_prop('display', store=align_prop)
    align = di.StringItem('Event label',
        default='lastSt').set_prop('display', active=align_prop)
    diagram_type = di.ChoiceItem('Type', ('Bar', 'Line'))

    def __init__(self):
        super(PSTHPlugin, self).__init__()
        self.unit = pq.ms

    def get_name(self):
        return 'Peri Stimulus Time Histogram'

    def start(self, current, selections):
        # Prepare quantities
        start = float(self.start_time)*self.unit
        stop = None
        if self.stop_enabled:
            stop = float(self.stop)*self.unit
        bin_size = float(self.bin_size)*self.unit

        # Load data
        current.progress.begin()
        trains = current.spike_trains_by_unit_and_segment()
        if self.align_enabled:
            events = current.labeled_events(self.align)
        else:
            events = None

        psth(trains, events, start, stop, bin_size, self.diagram_type == 0,
            progress=current.progress)