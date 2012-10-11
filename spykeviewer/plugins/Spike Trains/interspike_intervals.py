import quantities as pq

from spykeutils.plugin import analysis_plugin, gui_data
from spykeutils import plot

class ISIPlugin(analysis_plugin.AnalysisPlugin):
    bin_size = gui_data.FloatItem('Bin size', 1.0, 0.1, 10000.0, unit='ms')
    cut_off = gui_data.FloatItem('Cut off', 50.0, 2.0, 10000.0, unit='ms')
    diagram_type = gui_data.ChoiceItem('Type', ('Bar', 'Line'))

    def get_name(self):
        return 'Interspike Interval Histogram'

    def start(self, current, selections):
        current.progress.begin('Creating Interspike Interval Histogram...')
        d = current.spike_trains_by_unit()
        current.progress.done()
        plot.ISI(d, self.bin_size*pq.ms,
            self.cut_off*pq.ms, self.diagram_type == 0, pq.ms)



