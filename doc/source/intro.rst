Dependencies
============
Spyke Viewer uses :mod:`guiqwt` for plotting (alghough users can easily use
a different library like `matplotlib <http://matplotlib.sourceforge.net>`_
in their plugins) and therefore shares its dependencies (including scipy,
PyQt4 and PyQwt5). In addition, the I/O functionality requires neo and
tables, both are available at PyPi. Some of the existing plugins use
`spykeutils <http://spykeutils.readthedocs.org/>`_.

PyQt4 version needs to be 4.8.3 or newer.


Installation
============
At the moment, Spyke Viewer is not supposed to be installed. Just put it in
your python path and you're done. A setup will be added in the near future.

Currently, the neo version in PyPi contains bugs that affect some of the
functions in Spyke Viewer. Please install the most recent version from
`GitHub <https://github.com/python-neo/python-neo>`_.

Usage
=====
To start Spyke Viewer, execute the script ``bin/main.py`` in the Spyke
Viewer folder.