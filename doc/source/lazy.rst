.. _lazy:

Lazy Features
-------------

Spyke Viewer offers two ways to deal with very large files.

Lazy Loading
############

With lazy loading, only the structure of a file is loaded when you first
open it, while big data chunks (e.g. signals, spike trains) are not.
This can result in faster loading times and much reduced memory usage and
enables you to use data files that are larger than your main memory. Spyke
Viewer will load the required data automatically once it is needed. This
means that while initial loading is faster, data access will be slower.
You can switch between regular and lazy loading from the "File" menu under
"Read Mode". The read mode affects newly loaded files and you can have
both regularly and lazily loaded files opened at the same time. Most
Neo IOs do not support this feature (currently, only the IO for HDF5
files does) - when using lazy mode with an unsopported IO, the file is loaded
as in regular mode.

There are two options for lazy loading in the menu: "Lazy Load" and
"Cached Lazy Load". In "Lazy Load", data objects are loaded on request
and discarded afterwards, so the memory usage stays low. In "Cached Lazy
Load", data objects are inserted into the object hierarchy when they are
requested, so they only have to be loaded once, but memory usage will grow
when more data objects are used while the file is open.

.. Note::
    If you create your own plugins or use the integrated console with lazy
    loading, you need to be aware that the data objects are only loaded
    when accessed through a
    DataProvider object (explained below). For example,
    ``current.spike_trains()`` would return correctly loaded objects.
    But ``current.segments()[0].spiketrains`` can contain lazy objects.
    To be safe, always use the DataProvider to access the data objects
    you are interested in.

Lazy Cascading
##############

Lazy cascading goes one step further than lazy loading: Not even the complete
structure of a file is loaded initially. When lazy cascading is active, each
object is automatically loaded when first accessed. For example, if you load
a file with multiple Blocks, the Segments of each Block are only loaded when
you select the Block in Spyke Viewer and the Segments need to be displayed.
Similarly, the spike trains of a segment are only loaded once they are
accessed. In contrast to lazy loading, with lazy cascading objects are loaded
automatically even if they are not accessed through a DataProvider. Once an
object has been accessed using lazy cascading, it stays in memory, making
future access faster but potentially filling up main memory. You can use lazy
cascading and lazy loading without caching at the same time to mitigate this.
You switch between regular and lazy cascading using "Cascade Mode" in the
"File" menu. Like lazy loading, lazy cascading depends on support of the
IO class and currently only works with the HDF5 IO. You can implement both
in your own IO plugins, the
`Neo documentation
<http://neo.readthedocs.org/en/latest/io_developers_guide.html>`_
describes what is needed.