from PyQt4.QtGui import QMessageBox

from spykeutils.plugin import analysis_plugin, gui_data
from spykeutils.spyke_exception import SpykeException
import spykeutils.conversions as convert
import spykeutils.plot as plot
import spykeutils.plot.helper as helper

class SignalPlotPlugin(analysis_plugin.AnalysisPlugin):
    """ Signal Plot
    """
    domain = gui_data.ChoiceItem('Domain', ('Recording Channel Group',
                                            'Recording Channel'))
    show_events = gui_data.BoolItem('Show events', default=True)
    show_epochs = gui_data.BoolItem('Show epochs', default=True)
    show_waveforms = gui_data.BoolItem('Show spike waveforms', default=False)
    st_mode = gui_data.ChoiceItem('Spike Trains', ('Not used',
                                                   'Show spike events',
                                                   'Show spike waveforms'),
                                 default=2)
    
    def get_name(self):
        return 'Signal Plot'

    @helper.needs_qt
    def start(self, current, selections):
        # Handle too little and too much data
        if current.num_analog_signal_arrays() + \
            current.num_analog_signals() < 1:
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
            #if seg in signals:
            #    seg_signals.extend(signals[seg])
            if seg in signal_arrays:
                for sa in signal_arrays[seg]:
                    seg_signals.extend(
                        convert.analog_signals_from_analog_signal_array(sa))

            for s in seg_signals:
                plot.signal(s, events=seg_events, epochs=seg_epochs, 
                        spike_trains=seg_trains,
                        spike_waveforms=seg_spikes,
                        spike_train_waveforms=self.st_mode==2,
                        progress=current.progress)