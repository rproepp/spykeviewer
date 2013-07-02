.. _plugins:

Plugins
=======

This section describes the configuration options of the plugins that are
included with Spyke Viewer. All included plugins create plots. For
information on how to create your own plugins, see :ref:`analysisplugins`.

Signal Plot
-----------
Shows the selected analog signals. A number of options enable to include
additional information in the plot.

.. image:: /img/plugin-signals.png

Use Subplots
  Determines whether multiple subplots are used or all signals are shown in
  one large plot.

Show subplot names
    Only valid when subplots are used. Determines if each subplot has a title
    with the signal name (if available) or the recording channel name.

Included signals
  This option can be used to tune which type of signals are shown:
  AnalogSignal objects, AnalogSignalArray objects or both. In most cases, a
  file will only include one of the signal types, so the default option of
  including both will work well (you probably never need to change it if you
  do not know the difference between the signal objects).

Show events
  When this is checked, events in the selected trial will be shown in the
  plot.

Show epochs
  When this is checked, periods in the selected trial will be shown in the
  plot.

One plot per segment
    When this is not checked, only one plot with signals from the first
    selected segment is created. Otherwise, one plot for each selected
    segment is created.

Show spikes
  Determines whether spikes are included in the plot. The following options
  are used to select from what data how the spikes are displayed:

  Display as
    Spikes can be shown as their waveform overlaid on the analog signal or a
    vertical line marking their occurrence.

  Included data
    Determines whether to include spikes from SpikeTrain objects, Spike
    objects, or both.

  Use first spike as template
    This option can be used for a special case: All spikes in the SpikeTrain
    objects have the same waveform (e.g. because they use the same template
    from spike sorting). If this option is checked, the plugin assumes that
    each unit has a SpikeTrain and a single Spike. The waveform from the
    Spike object is used for every spike in the SpikeTrain. The data in the
    example file is structured in this way.

Spectrogram
-----------
Shows spectrograms of the selected analog signals.

.. image:: /img/plugin-spectrogram.png

Interpolate
  Determines whether the dipslayed spectrogram is interpolated.

Show color bar
  If this is checked, a colorbar will be shown with each plot, illustrating
  the logarithmic power represented by the colors.

FFT samples
  The number of signal samples used in each FFT window.

Included signals
  This option can be used to tune which type of signals are shown:
  AnalogSignal objects, AnalogSignalArray objects or both. In most cases, a
  file will only include one of the signal types, so the default option of
  including both will work well (you probably never need to change it if you
  do not know the difference between the signal objects).

Spike Waveform Plot
-------------------
Shows waveforms of selected spikes.

.. image:: /img/plugin-waveforms.png

Antialiased lines
  Determines if antialiasing (smoothing) is used for the plot. If you want to
  display thousands of spikes or more, unchecking this option will improve the
  plotting performance considerably.

Included spikes
  Determines whether to include spikes from SpikeTrain objects, Spike
  objects, or both.

Plot type
  Three different plot types can be selected: "One plot per channel" creates a
  subplot for each channel, "One plot per unit" creates a subplot for each
  unit and "Single plot" creates one plot containing all channels and units.

Split channels
  Multichannel waveforms can be split either horizontally or vertically.

Correlogram
-----------
Creates auto- and crosscorrelograms for selected spike trains.

.. image:: /img/plugin-correlogram.png

Bin size (ms)
  The bin size used in the calculation of the correlograms.

Cut off (ms)
  The maximum time lag for which the correlogram will be calculated and
  displayed.

Data source
  The plugin supports two ways of organizing the data from which the
  correlograms are created: If "Units" is selected, the spike trains for each
  currently selected unit are treated as a dataset. For example, if two units
  are selected, the plugin creates three subplots: one autocorrelogram for
  each unit and a cross-correlogram between them.

  If "Selections" are chosen, spike trains from each saved selection are
  treated as a dataset. Note that the plot can only be created if all
  selections contain the same number of spike trains.

Counts per
  Determines if the counts are displayed per second or per segment.

Border correction
  Determines if an automatic correction for less data at higher timelags is
  applied.

Interspike Interval Histogram
-----------------------------
Creates an interspike interval histogram for one or more units.

.. image:: /img/plugin-isi.png

Bin size (ms)
  The bin size used in the calculation of the histogram.

Cut off (ms)
  The maximum interspike interval that is displayed.

Type
  Determines the type of histogram. If "Bar" is selected, only the histogram
  for the first selected unit is displayed. If "Line" is selected, all
  selected units are included in the plot.

Peristimulus Time Histogram
---------------------------
Creates a peristimulus time histogram (PSTH) for one or multiple units.

.. image:: /img/plugin-psth.png

Bin size (ms)
  The bin size used in the calculation of the histogram.

Start time (ms)
  An offset from the alignment event or start of the spike train. Calculation
  of the PSTH begins at this offset. Negative values are allowed (this can be
  useful when using an alignment event).

Stop time
  A fixed stop time for calculation of the PSTH. If this is not activated,
  the smallest stop time of all included spike trains is used. If the smallest
  stop time is smaller than the value entered here, it will be used instead.

Alignment event
  An event (identified by label) on which all spike trains are aligned before
  the PSTH is calculated. After alignment, the event is a time 0 in the plot.
  The event has to be present in all selected segments that include spike
  trains for the PSTH.

Type
  Determines the type of histogram. If "Bar" is selected, only the histogram
  for the first selected unit is displayed. If "Line" is selected, all
  selected units are included in the plot.

Raster Plot
-----------
Creates a raster plot from multiple spiketrains.

.. image:: /img/plugin-rasterplot.png

Domain
  The raster plot can either be created from multiple units and one segment
  ("Units") or one unit over multiple segments ("Segments").

Show lines
  Determines if a small horizontal black line is displayed for each spike
  train.

Show events
  When this is checked, events in the selected trial will be shown in the
  plot. If the selected domain is "Segments", events from all selected
  segments are included.

Show epochs
  When this is checked, periods in the selected trial will be shown in the
  plot. If the selected domain is "Segments", epochs from all selected
  segments are included.

Spike Density Estimation
------------------------
Creates a spike density estimation (SDE) for one or multiple units. Optionally
computes the best kernel width for each unit.

.. image:: /img/plugin-sde.png

Kernel size (ms)
  The width of the kernel used for the plot. If kernel width optimization is
  enabled, this parameter is not used.

Start time (ms)
  An offset from the alignment event or start of the spike train. Calculation
  of the SDE begins at this offset. Negative values are allowed (this can be
  useful when using an alignment event).

Stop time
  A fixed stop time for calculation of the SDE. If this is not activated,
  the smallest stop time of all included spike trains is used. If the smallest
  stop time is smaller than the value entered here, it will be used instead.

Alignment event
  An event (identified by label) on which all spike trains are aligned before
  the SDE is calculated. After alignment, the event is a time 0 in the plot.
  The event has to be present in all selected segments that include spike
  trains for the SDE.

Kernel width optimization
  When this option is enabled, the best kernel width for each unit is
  determined using the algorithm from [1]_.

  Minimum kernel size (ms)
    The minimum kernel width that the algorithm should try.

  Maximum kernel size (ms)
    The maximum kernel width that the algorithm should try.

  Kernel size steps
    The number of steps from minimum to maximum kernel size that the algorithm
    should try. The steps are distributed equidistant on a logarithmic scale.


.. [1] Shimazaki, Shinomoto. (2010). Kernel bandwidth optimization in spike
       rate estimation. *Journal of Computational Neuroscience*, 29, 171-182.