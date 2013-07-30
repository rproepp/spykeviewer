from spykeutils.plugin import analysis_plugin, gui_data
from spykeutils import plot
from spykeutils.tools import extract_spikes
import spykeutils.conversions as convert
import quantities as pq


extract_prop = gui_data.ValueProp(False)


class SpikePlotPlugin(analysis_plugin.AnalysisPlugin):
    anti_aliased = gui_data.BoolItem('Antialiased lines (slow for '
                                     'large amounts of spikes)',
                                     default=True)        
    
    _g = gui_data.BeginGroup('Include spikes from')
    spike_mode = gui_data.ChoiceItem('Spikes', ('Do not include', 
                                                'Regular', 
                                                'Emphasized'),
                                     default=1)
    inc_spikes = gui_data.BoolItem('Spike Trains')
    inc_extracted = gui_data.BoolItem(
        'Extracted from signal').set_prop('display', store=extract_prop)
    length = gui_data.FloatItem(
        'Spike length', unit='ms', default=1.0).set_prop(
            'display', active=extract_prop)
    align = gui_data.FloatItem(
        'Alignment offset', unit='ms', default=0.5).set_prop(
            'display', active=extract_prop)
    _g_ = gui_data.EndGroup('Include spikes from')
    plot_type = gui_data.ChoiceItem('Plot type', ('One plot per channel',
                                                  'One plot per unit',
                                                  'Single plot'))
    split_type = gui_data.ChoiceItem('Split channels', ('Vertically', 
                                                        'Horizontally'))
    layout = gui_data.ChoiceItem('Subplot layout', ('Linear', 'Square'))
    fade = gui_data.BoolItem('Fade earlier spikes')
    
    def get_name(self):
        return 'Spike Waveform Plot'

    def start(self, current, selections):
        current.progress.begin('Creating spike waveform plot')
        current.progress.set_status('Loading spikes')
        
        spikes = {}
        strong = {}
        if self.spike_mode == 1:
            spikes = current.spikes_by_unit()
        elif self.spike_mode == 2:
            strong = current.spikes_by_unit()
        
        spike_trains = None
        if self.inc_spikes:
            current.progress.set_status('Loading spike trains')
            spike_trains = current.spike_trains_by_unit_and_segment()
            
            for u, trains in spike_trains.iteritems():
                s = []
                for st in trains.values():
                    if st.waveforms is not None:
                        s.extend(convert.spike_train_to_spikes(st))
                if not s:
                    continue
                spikes.setdefault(u, []).extend(s)
                
        if self.inc_extracted:
            current.progress.set_status('Extracting spikes from signals')
            signals = current.analog_signals_by_segment_and_channel(
                conversion_mode=3)
            if spike_trains is None:
                spike_trains = current.spike_trains_by_unit_and_segment()
                
            for u, trains in spike_trains.iteritems():
                s = []
                rcg = u.recordingchannelgroup
                for seg, train in trains.iteritems():
                    if seg not in signals:
                        continue
                    
                    train_sigs = []
                    for rc in signals[seg]:
                        if rcg in rc.recordingchannelgroups:
                            train_sigs.append(signals[seg][rc])
                    if not train_sigs:
                        continue
                    s.extend(extract_spikes(
                        train, train_sigs,
                        self.length * pq.ms, self.align * pq.ms))
                if not s:
                    continue
                spikes.setdefault(u, []).extend(s)

        fade = 0.2 if self.fade else 1.0
        plot.spikes(spikes, self.plot_type * 2 + self.split_type + 1,
                    strong, anti_alias=self.anti_aliased, fade=fade,
                    subplot_layout=self.layout, progress=current.progress)