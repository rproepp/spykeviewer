from PyQt4.QtGui import QMessageBox

from spykeutils.plugin import analysis_plugin, gui_data
from spykeutils.spyke_exception import SpykeException
import spykeutils.conversions as convert
import spykeutils.plot as plot
import spykeutils.plot.helper as helper

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
    show_waveforms = gui_data.BoolItem('Show spike waveforms', 
                                       default=False)
    st_mode = gui_data.ChoiceItem('Spike Trains', 
                                  ('Not used', 'Show spike events',
                                   'Show spike waveforms'),
                                  default=2)
    
    def get_name(self):
        return 'Signal Plot'

    @helper.needs_qt
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
        if self.st_mode > 0:
            current.progress.set_status('Loading spike trains')
            spike_trains = current.spike_trains_by_segment()

        spikes = None
        if self.show_waveforms:
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

            seg_signals = []
            if (self.which_signals == 0 or self.which_signals == 2)\
                and seg in signals:
                seg_signals.extend(signals[seg])
            if self.which_signals > 0 and seg in signal_arrays:
                for sa in signal_arrays[seg]:
                    seg_signals.extend(
                        convert.analog_signals_from_analog_signal_array(sa))
            
            if self.st_mode==2:
                if seg_spikes is None:
                    seg_spikes = []
                for st in seg_trains:
                    if st.waveforms is not None:
                        seg_spikes.extend(
                            convert.spikes_from_spike_train(st))
                seg_trains = None
                    
            plot.signals(seg_signals, events=seg_events, 
                         epochs=seg_epochs, spike_trains=seg_trains,
                         spikes=seg_spikes, use_subplots=self.subplots,
                         progress=current.progress)