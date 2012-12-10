.. _extending:

Extending Spyke Viewer
======================
There are two ways of extending Spyke Viewer: Analysis plugins and IO plugins.
Both are created by placing a Python file with an appropriate class into one
of the plugin directories defined in the :ref:`settings`. This section
describes how to create them.

.. _analysisplugins:

Analysis plugins
----------------

The easiest way to create a new analysis plugin is directly from the GUI.
Alternatively, you can use your favourite Python editor to create and edit
plugin files. This section describes the creation of an example plugin.

From console to plugin
######################

In many cases, you will want to turn code that you have written in the console
into a plugin for easy usage and sharing. See :ref:`console` for an
introduction to the integrated console. Here, a similar example will be
expanded into a plugin. Load the example data file (see :ref:`usage`), select
all segments and units and enter the following code in the console:

>>> trains = current.spike_trains_by_unit()
>>> for u, st in trains.iteritems():
...     print u.name, '-', sum((len(train) for train in st)), 'spikes'

This will print the total number of spikes for each selected unit in all
selected trials. Note that these lines have now appeared in the
*Command History* dock. Now select "New plugin" from the "Plugins" menu or
toolbar. The *Plugin Editor* dock will appear with a tab named "New Plugin"
containing a code template. The template is already a working plugin, although
without any functionality. It contains a class (which subclasses
:class:`spykeutils.plugin.analysis_plugin.AnalysisPlugin`) with two methods:
``get_name()`` and ``start(current, selections)``. ``get_name()`` is very
simple - it just returns a string to identify the plugin in the *Plugins*
dock. Replace the string "New Plugin" by a name for your plugin, for example
"Spike Counts".

The ``start`` method gets called whenever you start a plugin. The two
parameters are the same objects as the identically named objects that can be
used in the console (see :ref:`console`): ``current`` gives access to the
currently selected data, ``selections`` is a list containing the stored
selections. Both ``current`` and the entries of ``selections`` are
:class:`spykeutils.plugin.data_provider.DataProvider` objects, refer to the
documentation for details of the methods provided by this class.

Replace the contents of the ``start`` method by the code you entered into the
console (you can copy and paste the code from the *Command History* dock).
Now click on "Save plugin" in the "Plugins" menu or toolbar. A Save dialog
will appear. Select one of the plugin paths (or a subfolder) that you have
configured in the :ref:`settings` and choose a name (e.g. "spikecount.py").
When you save the plugin, it will appear in the *Plugins* dock. You can now
use it just like the included plugins. Try selecting different subsets of
segments and units and observe how the output of the plugin (on the console)
always reflects the current selection.

Plugin configuration
####################
This section shows how to make your plugin configurable and use matplotlib to
create a plot. Your newly created plugin currently only prints to the console.
In order to create a configuration option, add the following line above the
``get_name`` method::

    output_type = gui_data.ChoiceItem('Output type', ('Total count', 'Count plot'))

Now, when you select your plugin and click on "Configure plugin", a window
with a configuration option (a choice between "Total count" and "Count plot"
will appear. The ``gui_data`` module encapsulates :mod:`guidata`. You can
look at the documentation or the code of existing plugins for its more
information.

Next, you will modify the ``start`` method so it uses the configuration option
and creates a plot if it is configured for "Count plot". Since you will be
using ``matplotlib`` for the plot, you first have to import it by adding::

    import numpy as np

at the top of the plugin file.

Next, replace the code in the ``start`` method by::

    trains = current.spike_trains_by_unit()
    for u, st in trains.iteritems():
        if self.output_type == 0: # Total count
            print u.name, '-', sum((len(train) for train in st)), 'spikes'
        else: # Count plot
            plt.plot([len(train) for train in st])

If you now set the configuration of the plugin to "Count plot", you will see
a plot with the spike count for each unit in all trials.

.. _ioplugins:

IO plugins
----------
If you have data in a format that is not supported by Neo, you can still load
it with Spyke Viewer by creating an IO plugin. This is identical to writing
a regular Neo IO class (see
http://neo.readthedocs.org/en/latest/io_developers_guide.html to learn how
to do it) and placing the Python file with the class in a plugin directory
(the search for IO plugins is not recursive, so you have to place the file
directly in one of the directories that you defined in the :ref:`settings`).
If you create an IO class for a file format that is also used outside of your
lab, please consider sharing it with the Neo community.