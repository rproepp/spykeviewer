from spykeutils.plugin import analysis_plugin, gui_data
import scipy as sp
import matplotlib.mlab as mlab
from guiqwt.plot import BaseImageWidget
from guiqwt.builder import make
from spykeutils.plot.dialog import PlotDialog
import spykeutils.plot.helper as helper
from spykeutils import SpykeException
import quantities as pq


class SpectrogramPlugin(analysis_plugin.AnalysisPlugin):
    nfft_index = (32, 64, 128, 256, 512, 1024, 2048, 4096, 8192)
    nfft_names = (str(s) for s in nfft_index)
    interpolate = gui_data.BoolItem('Interpolate', default=True)
    show_color_bar = gui_data.BoolItem('Show color bar', default=False)
    fft_samples = gui_data.ChoiceItem('FFT samples', nfft_names, default=3)
    which_signals = gui_data.ChoiceItem('Included signals',
                                        ('AnalogSignal',
                                         'AnalogSignalArray', 'Both'),
                                        default=2)
    
    def get_name(self):
        return 'Signal Spectogram'

    @helper.needs_qt
    def start(self, current, selections):
        current.progress.begin('Creating Spectogram')
        signals = current.analog_signals(self.which_signals + 1)
        if not signals:
            current.progress.done()
            raise SpykeException('No signals selected!')
            
        num_signals = len(signals)

        columns = int(round(sp.sqrt(num_signals)))
    
        current.progress.set_ticks(num_signals)
        samples = self.nfft_index[self.fft_samples]
        win = PlotDialog(toolbar=True, 
                         wintitle="Signal Spectogram (FFT window size %d)" 
                         % samples)
                         
        for c in xrange(num_signals):
            pW = BaseImageWidget(win, yreverse=False,
                lock_aspect_ratio=False)
            plot = pW.plot
            
            s = signals[c]
            
            # Calculate spectrogram and create plot
            v = mlab.specgram(s, NFFT=samples, noverlap=samples/2,
                              Fs=s.sampling_rate.rescale(pq.Hz))
            interpolation = 'nearest'
            if self.interpolate:
                interpolation = 'linear'
            img = make.image(sp.log(v[0]), ydata=[v[1][0],v[1][-1]], 
                             xdata=[v[2][0] + s.t_start.rescale(pq.s), 
                                    v[2][-1] + s.t_start.rescale(pq.s)],
                             interpolation=interpolation)
            plot.add_item(img)
            
            # Labels etc.
            if not self.show_color_bar:
                plot.disable_unused_axes()
            title = ''
            if s.recordingchannel and s.recordingchannel.name:
                title = s.recordingchannel.name
            if s.segment and s.segment.name:
                if title:
                    title += ' , '
                title += s.segment.name
            plot.set_title(title)
            plot.set_axis_title(plot.Y_LEFT, 'Frequency')
            plot.set_axis_unit(plot.Y_LEFT,
                               s.sampling_rate.dimensionality.string)
            plot.set_axis_title(plot.X_BOTTOM, 'Time')
            time_unit = (1 / s.sampling_rate).simplified
            plot.set_axis_unit(plot.X_BOTTOM, 
                               time_unit.dimensionality.string)
            win.add_plot_widget(pW, c, column=c%columns)
            current.progress.step()
    
        current.progress.done()
        win.add_custom_image_tools()
        win.add_x_synchronization_option(True, range(num_signals))
        win.add_y_synchronization_option(True, range(num_signals))
        win.show()
        