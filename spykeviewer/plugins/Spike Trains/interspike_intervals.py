import quantities as pq
import neo

from spykeutils.plugin import analysis_plugin, gui_data
from spykeutils import plot


class ISIPlugin(analysis_plugin.AnalysisPlugin):
    bin_size = gui_data.FloatItem('Bin size', 1.0, 0.1, 10000.0, unit='ms')
    cut_off = gui_data.FloatItem('Cut off', 50.0, 2.0, 10000.0, unit='ms')
    diagram_type = gui_data.ChoiceItem('Type', ('Bar', 'Line'))
    data_source = gui_data.ChoiceItem('Data source', ('Units', 'Selections'))

    def get_name(self):
        return 'Interspike Interval Histogram'

    def start(self, current, selections):
        current.progress.begin('Creating Interspike Interval Histogram')
        if self.data_source == 0:
            d = current.spike_trains_by_unit()
        else:
            # Prepare dictionary for isi():
            # One entry of spike trains for each selection
            d = {}
            for s in selections:
                d[neo.Unit(s.name)] = s.spike_trains()
        current.progress.done()
        plot.isi(
            d, self.bin_size * pq.ms, self.cut_off * pq.ms,
            self.diagram_type == 0, time_unit=pq.ms)





