from spykeutils.plugin import analysis_plugin, gui_data
import spykeutils.plot
import spykeutils.conversions as convert

class SpikePlotPlugin(analysis_plugin.AnalysisPlugin):
    """ Spike Waveform Plot """
    anti_aliased = gui_data.BoolItem('Antialiased lines (slow for '
                                    'large amounts of spikes)',
                                     default=True)                  
    st_mode = gui_data.ChoiceItem('Included Spikes', ('Spikes', 
                                                      'Spike Trains',
                                                      'Both'))
    plot_type = gui_data.ChoiceItem('Plot type', ('Separate Axes',
                                                 'Split vertically',
                                                 'Split horizontally'))
    
    def get_name(self):
        return 'Spike Waveform Plot'

    def start(self, current, selections):
        current.progress.begin('Creating spike waveform plot...')
        
        current.progress.set_status('Loading spikes')
        if self.st_mode == 0 or self.st_mode == 2:
            spikes = current.spikes_by_unit()
        else:
            spikes = {}
        if self.st_mode > 0:
            current.progress.set_status('Loading spike trains')
            spike_trains = current.spike_trains_by_unit()
            for u, trains in spike_trains.iteritems():
                s = []
                for st in trains:
                    if st.waveforms is not None:
                        s.extend(convert.spikes_from_spike_train(st))
                if not s:
                    continue
                if u not in spikes:
                    spikes[u] = s
                else:
                    spikes[u].extend(s)

        spykeutils.plot.spikes(spikes, self.plot_type + 1,
                               anti_alias=self.anti_aliased, 
                               progress=current.progress)