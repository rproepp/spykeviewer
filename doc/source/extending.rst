.. _extending:

Extending Spyke Viewer
======================
There are two ways of extending Spyke Viewer: Analysis plugins and IO plugins.
Both are created by placing a Python file with an appropriate class into one
of the plugin directories defined in the :ref:`settings`. In addition, Spyke
Viewer include a customizable script that is run each time the program is
started. :ref:`startup` describes possible applications and how to edit this
script. This section describes how to create plugins and how to use the
startup script. If you create a useful extension, please share it at the
`Spyke Repository <http://spyke-viewer.g-node.org/>`_!


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

    import matplotlib.pyplot as plt

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
a regular Neo IO class [#relative]_ (see
http://neo.readthedocs.org/en/latest/io_developers_guide.html to learn how
to do it) and placing the Python file with the class in a plugin directory
(the search for IO plugins is not recursive, so you have to place the file
directly in one of the directories that you defined in the :ref:`settings`).
The filename has to end with "IO.py" or "io.py" (e.g. "MyFileIO.py") to
signal that it contains an io plugin.
If you create an IO class for a file format that is also used outside of your
lab, please consider sharing it with the Neo community.


.. _startup:

Startup script
--------------

The startup script is run whenever Spyke Viewer is started, after the GUI is
setup and before plugins are loaded. To edit the startup script, select the
"Edit startup script" item in the "File" menu.

One important use case for this file is manipulating your Python path. For
example, you may have a Python file or package that you want to use in your
plugins. If it is not on your Python path (for example because it cannot be
installed or you are using a binary version of Spyke Viewer, where Python
packages installed on the system are not accessible by default), you can
modify ``sys.path`` to include the path to your files::

    import sys
    sys.path.insert(0, '/path/to/my/files')

You can also use the startup script to configure anything that is accessible
by Python code. In particular, you can use the Spyke Viewer :ref:`api` to
access configuration options and the main window itself. For example, if you
want the Enter key to always finish a line in the console and only
use the Tab key for autocompletion::

    spyke.config.codecomplete_console_enter = False

To change the font size of the Python console (effective for new input) and
title of the window::

    import spykeviewer.api as spyke  # This line is included in the default startup script
    f = spyke.window.console.font()
    f.setPointSize(18) # Gigantic!
    spyke.window.console.set_pythonshell_font(f)
    spyke.window.setWindowTitle('Big is beatiful')


As a final example, you can customize the colors that are used
in spykeutils plots (for colored items like spikes in a rasterplot)::

    # Let's make everything pink!
    from spykeutils.plot import helper
    helper.set_color_scheme(['#F52887', '#C12267'])


Footnotes
---------

.. [#relative] There is one small difference between regular Neo IO classes
               and IO plugins: In plugins, you cannot use relative imports.
               For example, instead of::

                   from .tools import create_many_to_one_relationship

               as in the Neo example IO, you would write::

                   from neo.io.tools import create_many_to_one_relationship

