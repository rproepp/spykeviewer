.. |br| raw:: html

   <br />

Welcome to the Spyke Viewer documentation!
==========================================

Spyke Viewer is a multi-platform GUI application for navigating, analyzing and
visualizing electrophysiological datasets. It is based on the
`Neo <http://neo.readthedocs.org>`_ library, which enables it to load a wide
variety of data formats used in electrophysiology. At its core, Spyke Viewer
includes functionality for navigating Neo object hierarchies and performing
operations on them.

A central design goal of Spyke Viewer is flexibility. For this purpose, it
includes an embedded Python console and a plugin system. It comes with a
variety of plugins implementing common neuroscientific analyses and plots
(e.g. rasterplot, peristimulus time histogram, correlogram and signal plot).
Plugins can be easily created and modified using the integrated Python editor
or external editors.

A mailinglist for discussion and support is available at
https://groups.google.com/d/forum/spyke-viewer

Users can download and share plugins and other extensions at
http://spyke-viewer.g-node.org

If you use Spyke Viewer in work that leads to a scientific publication,
please cite:|br|
Pröpper, R. and Obermayer, K. (2013). Spyke Viewer: a flexible and extensible
platform for electrophysiological data analysis.
*Front. Neuroinform.* 7:26. doi: 10.3389/fninf.2013.00026

Contents:

.. toctree::
   :maxdepth: 2

   installation
   usage
   plugins
   extending
   api
   lazy
   changelog
   acknowledgements

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

