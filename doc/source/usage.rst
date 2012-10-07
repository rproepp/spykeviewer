.. _usage:

Usage
=====
This section gives a tutorial of the main functionality of Spyke Viewer. To
follow the examples, you need to download and unpack the sample data file:
https://github.com/downloads/rproepp/spykeviewer/sampledata.zip

When you start Spyke Viewer for the first time, you will see the following
layout:

.. image:: /img/screenshot-initial.png

All elements of the user interface are contained in docks and can be
rearranged to suit your needs. Their layout is saved when you close Spyke
Viewer.

Loading Data
------------
The first thing you want to do when using Spyke Viewer is to load your data.
The ``Files`` dock contains a view of all the files on your system. You can
use it to select one or more files, then click on the "Load" button below to
load the selected files into Spyke Viewer. For each selected file, the
filetype is selected automatically from the extension (folder-based formats
are currently not supported). For now, find and select the file "sample.h5"
that you just unpacked (an HDF5 File) and load it.

The data file input/output is based on :mod:`neo` and supports most of the
formats that have a
`Neo IO class <http://neo.readthedocs.org/en/latest/io.html>`_. If you want
to use a file format that is not supported by Neo, you can write a plugin:
:ref:`ioplugins`.

Selections
----------
Now that a file was loaded, some entries have appeared in the ``Navigation``
dock. To understand how to navigate data with Spyke Viewer, you need to know
the Neo object model. The following picture is a complete representation:



Filters
-------

Using Plugins
-------------

Using the Console
-----------------

.. _settings:

Settings
--------
