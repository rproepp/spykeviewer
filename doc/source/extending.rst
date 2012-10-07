.. _extending:

Extending Spyke Viewer
======================
How to make it do more!

Analysis plugins
----------------
Creating a plugin by example. Links to spykeutils docs.

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