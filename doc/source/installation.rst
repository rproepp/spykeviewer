Installation
============
There are two ways to install Spyke Viewer on your system. The preferred way
is to install the spykeviewer package in your Python environment. Depending on
what already exists on your system, this might require installing Python
itself and a few additional packages for scientific data processing,
management and visualization.

On the other hand, there are also binary packages available for Windows and
OS X. These packages do not have any additional requirements and can be
started immediately (from an app in OS X or an executable file in Windows,
please use the source installation for Linux).
However, as they are independent of an existing Python installation, you will
not be able to use installed additional packages from your Python environment.
The binary packages are especially useful if you do not normally use Python
or just want to try Spyke Viewer quickly. You can switch to the source
installation at any time.

Binary
------
If you want to install the binary version, go to the
`download page on GitHub <https://github.com/rproepp/spykeviewer/downloads>`_
and select the most recent version for your operating system. The downloaded
file contains an installer (for OS X) or executable (main\\spykeviewer.exe
for Windows). The rest of this page deals with source installation, you can
go to :ref:`usage` to learn how to use Spyke Viewer.

Source
------
If you want to install Spyke Viewer to your Python environment, there are a
few requirements that need to be fulfilled. If you use Linux, you might not
have access rights to your Python package installation directory, depending
on your configuration. In this case, you will have to execute all shell
commands in this section with administrator privileges, e.g. by using
``sudo``.

Dependencies
############
First you need at least Python 2.7. In addition, the following packages and
their respective dependencies need to be installed:

* spykeutils_
* scipy_
* guiqwt_
* guidata_
* tables_
* spyder_

Please see the respective websites for instructions on how to install them if
they are not present on your computer. On a recent version of Debian/Ubuntu,
you can install all of the dependencies (except spykeutils) with::

    $ sudo apt-get install python-guiqwt python-tables

On windows, you can use `Python(x,y)`_ if you do yet not have a Python
distribution installed. It also includes all dependencies (except
spykeutils).

.. Note::
    The current version of Neo in the Python Package Index contains
    some bugs that prevent it from working properly with Spyke Viewer in some
    situations. Please install the latest version directly from GitHub:
    https://github.com/rproepp/python-neo

    You can download the repository from the GitHub page or clone it using
    git and then install from the resulting folder::

    $ python setup.py install

spykeviewer
###########
Once the requirements are fulfilled, you need to install the package
spykeviewer. The easiest way to get it is from the Python Package
Index. If you have pip_ installed::

$ pip install spykeviewer

Alternatively, if you have setuptools_::

$ easy_install spykeviewer

Alternatively, you can get the latest version directly from GitHub at
https://github.com/rproepp/spykeviewer.

The master branch (selected by default) always contains the current stable
version. If you want the latest development version (not recommended unless
you need some features that do not exist in the stable version yet), select
the develop branch. You can download the repository from the GitHub page
or clone it using git and then install from the resulting folder::

$ python setup.py install

Once the package is installed, you can start Spyke Viewer using::

$ spyke-viewer

.. _`Python`: http://python.org/
.. _`spykeutils`: http://spykeutils.readthedocs.org/
.. _`guiqwt`: http://packages.python.org/guiqwt/
.. _`guidata`: http://packages.python.org/guidata/
.. _`tables`: http://www.pytables.org/
.. _`pip`: http://pypi.python.org/pypi/pip
.. _`scipy`: http://scipy.org/
.. _`setuptools`: http://pypi.python.org/pypi/setuptools
.. _`spyder`: http://packages.python.org/spyder/
.. _`Python(x,y)`: http://www.python.org/