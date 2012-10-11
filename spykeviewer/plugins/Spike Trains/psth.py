import quantities as pq

from spykeutils.plugin import analysis_plugin, gui_data
from spykeutils import plot

# Needed for activatable parameters
stop_prop = gui_data.ValueProp(False)
align_prop = gui_data.ValueProp(False)
optimize_prop = gui_data.ValueProp(False)

class PSTHPlugin(analysis_plugin.AnalysisPlugin):
    """ PSTH Plugin
    """
    # Configurable parameters
    bin_size = gui_data.FloatItem('Bin size', min=1.0, default=500.0, unit='ms')
    start_time = gui_data.FloatItem('Start time', default=0.0, unit='ms')

    stop_enabled = gui_data.BoolItem('Stop time enabled',
        default=False).set_prop('display', store=stop_prop)
    stop = gui_data.FloatItem('Time', default=10001.0,
        unit='ms').set_prop('display', active=stop_prop)

    align_enabled = gui_data.BoolItem('Alignment event enabled',
        default=False).set_prop('display', store=align_prop)
    align = gui_data.StringItem(
        'Event label').set_prop('display', active=align_prop)
    diagram_type = gui_data.ChoiceItem('Type', ('Bar', 'Line'))

    def __init__(self):
        super(PSTHPlugin, self).__init__()
        self.unit = pq.ms

    def get_name(self):
        return 'Peristimulus Time Histogram'

    def start(self, current, selections):
        # Prepare quantities
        start = float(self.start_time)*self.unit
        stop = None
        if self.stop_enabled:
            stop = float(self.stop)*self.unit
        bin_size = float(self.bin_size)*self.unit

        # Load data
        current.progress.begin()
        trains = current.spike_trains_by_unit()
        if self.align_enabled:
            events = current.labeled_events(self.align)
            for s in events: # Align on first event in each segment
                events[s] = events[s][0]
        else:
            events = None

        plot.psth(trains, events, start, stop, bin_size, True,
             self.diagram_type == 0, progress=current.progress)