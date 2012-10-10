from spykeutils.plugin import analysis_plugin, gui_data
from spykeutils import SpykeException
import spykeutils.conversions as convert
from spykeutils import plot
from copy import copy

spike_prop = gui_data.ValueProp(False)

class SignalPlotPlugin(analysis_plugin.AnalysisPlugin):
    """ Signal Plot
    """
    subplots = gui_data.BoolItem('Use subplots', default=True)
    which_signals = gui_data.ChoiceItem('Included signals',
                                        ('AnalogSignal',
                                         'AnalogSignalArray', 'Both'),
                                        default=2)
    show_events = gui_data.BoolItem('Show events', default=True)
    show_epochs = gui_data.BoolItem('Show epochs', default=True)
    
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
        num_signals = 0
        if (self.which_signals == 0 or self.which_signals == 2):
            num_signals += current.num_analog_signals()
        if self.which_signals > 0:
            num_signals += current.num_analog_signal_arrays()
        if num_signals < 1:
            raise SpykeException('No signals selected!')

        current.progress.begin('Creating signal plot...')

        signal_arrays = current.analog_signal_arrays_by_segment()
        signals = current.analog_signals_by_segment()

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

        # Create a plot for each segment
        segments = set(signals.keys())
        segments = segments.union(set(signal_arrays.keys()))
        for seg in segments:
            current.progress.begin('Creating signal plot...')
            current.progress.set_status('Constructing plot')
            seg_events = None
            if events and events.has_key(seg):
                seg_events = events[seg]

            seg_epochs = None
            if epochs and epochs.has_key(seg):
                seg_epochs = epochs[seg]

            seg_trains = None
            if spike_trains and spike_trains.has_key(seg):
                seg_trains = spike_trains[seg]

            seg_spikes = None
            if spikes and spikes.has_key(seg):
                seg_spikes = spikes[seg]

            # Prepare AnalogSignals
            seg_signals = []
            if (self.which_signals == 0 or self.which_signals == 2)\
                and seg in signals:
                seg_signals.extend(signals[seg])
            if self.which_signals > 0 and seg in signal_arrays:
                for sa in signal_arrays[seg]:
                    seg_signals.extend(
                        convert.analog_signal_array_to_analog_signals(sa))
            
            # Prepare template spikes
            if self.spike_form == 0 and self.template_mode:
                if seg_spikes is None:
                    seg_spikes = []

                template_spikes = {}
                for s in seg_spikes:
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

            plot.signals(seg_signals, events=seg_events, 
                         epochs=seg_epochs, spike_trains=seg_trains,
                         spikes=seg_spikes, use_subplots=self.subplots, 
                         show_waveforms=(self.spike_form==0),
                         progress=current.progress)
            
            # Only do one plot
            break
        