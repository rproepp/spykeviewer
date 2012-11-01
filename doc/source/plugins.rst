.. _plugins:

Plugins
=======

This section describes the plugins that are included with Spyke Viewer. All
included plugins create plots and will automatically use only the first
selected object if using the whole selection would require multiple plot
windows (e.g. the signal plot plugin will only create a plot for the first
selected segment).

For information on how to create your own plugins, see
:ref:`analysisplugins`.

Signal Plot
-----------
Shows the selected analog signals. A number of options enable to include
additional information in the plot.

.. image:: /img/plugin-signals.png

Use Subplots
  Determines whether multiple subplots are used or all signals are shown in
  one large plot.

Included signals
  This option can be used to tune which type of signals are shown:
  AnalogSignal objects, AnalogSignalArray objects or both. In most cases, a
  file will only include one of the signal types, so the default option of
  including both will work well (you probably never need to change it if you
  do not know the difference between the signal objects).

  Note that while only AnalogSignals for selected channels are be included in
  the plot, all channels for AnalogSignalArrays are always included as these
  objects are directly attached to RecordingChannelGroups.

Show events
  When this is checked, events in the selected trial will be shown in the
  plot.

Show epochs
  When this is checked, periods in the selected trial will be shown in the
  plot.

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
  Three different plot types can be selected: "Separate Axes" creates a
  subplot for each channel, "Split Horizontally" creates one plot where the
  channels are concatenated and "Split Vertically" creates one plot where the
  channels are stacked vertically.

Correlogram
-----------
Creates auto- and crosscorrelogram the selected units.

.. image:: /img/plugin-correlogram.png

Bin size (ms)
  The bin size used in the calculation of the correlograms.

Cut off (ms)
  The maximum time lag for which the correlogram will be calculated and
  displayed.

Data source
  The

Interspike Interval Histogram
-----------------------------

.. image:: /img/plugin-isi.png

Peristimulus Time Histogram
---------------------------

.. image:: /img/plugin-psth.png

Raster Plot
-----------

.. image:: /img/plugin-rasterplot.png

Spike Density Estimation
------------------------

.. image:: /img/plugin-sde.png

