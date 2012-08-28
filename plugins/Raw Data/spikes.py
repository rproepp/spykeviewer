from spykeutils.plugin import analysis_plugin, gui_data
import spykeutils.plot

class SpikePlotPlugin(analysis_plugin.AnalysisPlugin):
    """ Spike Waveform Plot"""
    anti_aliased = gui_data.BoolItem('Antialiased lines (smoothing)',
                                    default=True)
    plot_type = gui_data.ChoiceItem('Plot type', ('Separate Axes',
                                                 'Split vertically',
                                                 'Split horizontally'))
    
    def get_name(self):
        return 'Spike Waveform Plot'

    def start(self, current, selections):
        spykeutils.plot.spikes(current.spikes_by_unit(), self.plot_type + 1,
                               anti_alias=self.anti_aliased)