.. _extending:

Extending Spyke Viewer
======================
There are two ways of extending Spyke Viewer: Analysis plugins and IO plugins.
Both are created by placing a Python file with an appropriate class into one
of the plugin directories defined in the :ref:`settings`. This section
describes how to create them.

Analysis plugins
----------------

Guide with example coming soon...

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