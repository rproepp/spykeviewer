from spykeviewer.plugin_framework.analysis_plugin import AnalysisPlugin
import spykeutils.plot
import guidata.dataset.dataitems as di

class SpikePlotPlugin(AnalysisPlugin):
    """ Spike Waveform Plot"""
    anti_aliased = di.BoolItem('Antialiased lines (smoothing)', default=True)
    plot_type = di.ChoiceItem('Plot type', ('Separate Axes',
                                         'Split vertically',
                                         'Split horizontally'))
    
    def get_name(self):
        return 'Spike Waveform Plot'

    def start(self, current, selections):
        spykeutils.plot.spikes(current.spikes_by_unit(), self.plot_type + 1,
                               anti_alias=self.anti_aliased)