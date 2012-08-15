from spykeviewer.plugin_framework.analysis_plugin import AnalysisPlugin
import spykeutils.plot as plot

import quantities as pq
import guidata.dataset.dataitems as di

class RasterPlotPlugin(AnalysisPlugin):
    domain = di.ChoiceItem('Domain', ('Units', 'Segments'))
    show_lines = di.BoolItem('Show lines', default=True)
    show_events = di.BoolItem('Show events', default=True)
    show_epochs = di.BoolItem('Show epochs', default=True)

    def __init__(self):
        super(RasterPlotPlugin, self).__init__()
        self.unit = pq.ms

    def get_name(self):
        return 'Raster Plot'

    def start(self, current, selections):
        if self.domain == 0: # Units
            d = current.spike_trains_by_unit()
        else: # Segments
            d = current.spike_trains_by_segment()

        # Only show first spike train for each index
        for k in d.keys():
            if d[k]:
                d[k] = d[k][0]
            else:
                d.pop(k)
        
        events = None
        if self.show_events:
            if self.domain == 0: # Only events for displayed trial
                ev = current.events()
                if ev:
                    events = ev.values()[0]
            else: # Events for all trials
                events = [e for seg_events in current.events().values()
                          for e in seg_events]

        epochs = None
        if self.show_epochs:
            if self.domain == 0: # Only events for displayed trial
                ep = current.epochs()
                if ep:
                    epochs = ep.values()[0]
            else: # Events for all trials
                epochs = [e for seg_epochs in current.epochs().values()
                          for e in seg_epochs]

        plot.raster_plot(d, self.unit, self.show_lines, events, epochs)