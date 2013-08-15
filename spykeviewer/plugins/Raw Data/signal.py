from spykeutils.plugin import analysis_plugin, gui_data
from spykeutils import SpykeException
from spykeutils import plot
from copy import copy

spike_prop = gui_data.ValueProp(False)
subplot_prop = gui_data.ValueProp(False)

class SignalPlotPlugin(analysis_plugin.AnalysisPlugin):
    subplots = gui_data.BoolItem('Use subplots', default=True).set_prop(
        'display', store=subplot_prop)
    subplot_titles = gui_data.BoolItem(
        'Show subplot names', default=True).set_prop('display', active=subplot_prop)
    which_signals = gui_data.ChoiceItem('Included signals',
                                        ('AnalogSignal',
                                         'AnalogSignalArray', 'Both'),
                                        default=2)
    show_events = gui_data.BoolItem('Show events', default=True)
    show_epochs = gui_data.BoolItem('Show epochs', default=True)
    multiple_plots = gui_data.BoolItem('One plot per segment', default=False)
    
    _g = gui_data.BeginGroup('Spikes')
    show_spikes = gui_data.BoolItem(
        'Show spikes').set_prop('display', store=spike_prop)
    spike_form = gui_data.ChoiceItem('Display as',
        ('Waveforms', 'Lines')).set_prop('display', active=spike_prop)
    spike_mode = gui_data.ChoiceItem('Included data', 
        ('Spikes', 'Spike Trains', 'Both'), 
        default=2).set_prop('display', active=spike_prop)
    template_mode = gui_data.BoolItem(
        'Use first spike as template').set_prop('display', active=spike_prop)
    _g_ = gui_data.EndGroup('Spikes')
    
    def get_name(self):
        return 'Signal Plot'

    def start(self, current, selections):
        current.progress.begin('Creating signal plot')

        signals = current.analog_signals_by_segment(self.which_signals + 1)

        if not signals:
            raise SpykeException('No signals selected!')
            
        # Load supplemental data
        events = None
        if self.show_events:
            current.progress.set_status('Loading events')
            events = current.events()

        epochs = None
        if self.show_epochs:
            current.progress.set_status('Loading epochs')
            epochs = current.epochs()

        spike_trains = None
        if self.show_spikes and self.spike_mode > 0:
            current.progress.set_status('Loading spike trains')
            spike_trains = current.spike_trains_by_segment()

        spikes = None
        if self.show_spikes and self.spike_mode != 1:
            current.progress.set_status('Loading spikes')
            spikes = current.spikes_by_segment()

        # Create plot
        segments = set(signals.keys())
        for seg in segments:
            current.progress.begin('Creating signal plot...')
            current.progress.set_status('Constructing plot')
            seg_events = None
            if events and events.has_key(seg):
                seg_events = events[seg]

            seg_epochs = None
            if epochs and epochs.has_key(seg):
                seg_epochs = epochs[seg]

            seg_trains = []
            if spike_trains and spike_trains.has_key(seg):
                seg_trains = spike_trains[seg]

            seg_spikes = []
            if spikes and spikes.has_key(seg):
                seg_spikes = spikes[seg]
            
            # Prepare template spikes
            if self.spike_form == 0 and self.template_mode:
                template_spikes = {}
                for s in seg_spikes[:]:
                    if s.unit not in template_spikes:
                        template_spikes[s.unit] = s
                for ts in template_spikes.itervalues():
                    seg_spikes.remove(ts)
                    
                for st in seg_trains[:]:
                    if st.unit not in template_spikes:
                        continue
                    for t in st:
                        s = copy(template_spikes[st.unit])
                        s.time = t
                        seg_spikes.append(s)
                    seg_trains.remove(st)

            plot.signals(signals[seg], events=seg_events, 
                         epochs=seg_epochs, spike_trains=seg_trains,
                         spikes=seg_spikes, use_subplots=self.subplots, 
                         show_waveforms=(self.spike_form==0),
                         subplot_names=self.subplot_titles,
                         progress=current.progress)
            
            if not self.multiple_plots:
                break
        