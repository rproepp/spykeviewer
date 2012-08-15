from spykeviewer.plugin_framework.analysis_plugin import AnalysisPlugin
import spykeutils.plot as plot

import quantities as pq
import guidata.dataset.dataitems as di

class ISIPlugin(AnalysisPlugin):
    bin_size = di.FloatItem('Bin size', 1.0, 0.1, 10000.0, unit='ms')
    cut_off = di.FloatItem('Cut off', 50.0, 2.0, 10000.0, unit='ms')
    diagram_type = di.ChoiceItem('Type', ('Bar', 'Line'))

    def get_name(self):
        return 'Interspike Interval Histogram'

    def start(self, current, selections):
        current.progress.begin('Creating Interspike Interval Histogram...')
        d = current.spike_trains_by_unit()
        current.progress.done()
        plot.ISI(d, self.bin_size*pq.ms,
            self.cut_off*pq.ms, self.diagram_type == 0, pq.ms)


