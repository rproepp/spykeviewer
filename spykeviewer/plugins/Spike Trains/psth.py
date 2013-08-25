import quantities as pq
import neo

from spykeutils.plugin import analysis_plugin, gui_data
from spykeutils import plot

# Needed for activatable parameters
stop_prop = gui_data.ValueProp(False)
align_prop = gui_data.ValueProp(False)
optimize_prop = gui_data.ValueProp(False)


class PSTHPlugin(analysis_plugin.AnalysisPlugin):
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
    data_source = gui_data.ChoiceItem('Data source', ('Units', 'Selections'))


    def get_name(self):
        return 'Peristimulus Time Histogram'

    def start(self, current, selections):
        # Prepare quantities
        start = float(self.start_time) * pq.ms
        stop = None
        if self.stop_enabled:
            stop = float(self.stop) * pq.ms
        bin_size = float(self.bin_size) * pq.ms

        # Load data
        current.progress.begin('Creating PSTH')
        events = None
        if self.data_source == 0:
            trains = current.spike_trains_by_unit()
            if self.align_enabled:
                events = current.labeled_events(self.align) 
        else:
            # Prepare dictionaries for psth():
            # One entry of spike trains for each selection,
            # an event for each segment occuring in any selection
            trains = {}
            if self.align_enabled:
                events = {}
            for s in selections:
                trains[neo.Unit(s.name)] = s.spike_trains()
                if self.align_enabled:
                    events.update(s.labeled_events(self.align))
        
        if events:
            for s in events:  # Align on first event in each segment
                events[s] = events[s][0]

        plot.psth(
            trains, events, start, stop, bin_size, 
            rate_correction=True, time_unit=pq.ms,
            bar_plot=self.diagram_type == 0, 
            progress=current.progress)