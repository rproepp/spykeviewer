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
`homepage <http://www.ni.tu-berlin.de/software/spykeviewer>`_
and select the most recent version for your operating system. The downloaded
file contains an installer (for OS X) or executable (main\\spykeviewer.exe
for Windows). The rest of this page deals with source installation, you can
go to :ref:`usage` to learn how to use Spyke Viewer.

Source
------
If you use the NeuroDebian_ repositories and a recent version of Debian
(>= Wheezy or Sid) or Ubuntu (>= 12.04), you can install the source version
of Spyke Viewer using your package manager::

$ sudo apt-get install spykeviewer

After you install the spykeviewer package, you can start Spyke Viewer from
your menu (it should appear in the "Science" or "Education" category) or
using::

$ spykeviewer

The next sections describe how to install Spyke Viewer if you do not have
access to the NeuroDebian_ repositories (e.g. on Windows or OS X) or want
to install using the Python packaging system.

Dependencies
############
First you need Python 2.7. In addition, the following packages and
their respective dependencies need to be installed:

* spykeutils_
* scipy_
* guiqwt_
* matplotlib_
* tables_
* spyder_ >= 2.1.0
* neo_ >= 0.2.1

Please see the respective websites for instructions on how to install them if
they are not present on your computer. On a recent version of Debian/Ubuntu
(e.g. Ubuntu 12.04 or newer), you can install all dependencies that are not
automatically installed by ``pip`` or ``easy_install`` with::

$ sudo apt-get install python-guiqwt python-tables python-matplotlib

On Windows, you can use `Python(x,y)`_ if you do yet not have a Python
distribution installed. It includes the same dependencies.

spykeviewer
###########
Once the requirements are fulfilled, you need to install the package
spykeviewer.  If you use Linux, you might not
have access rights to your Python package installation directory, depending
on your configuration. In this case, you will have to execute all shell
commands in this section with administrator privileges, e.g. by using
``sudo``. The easiest way to get it is from the Python Package
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

$ spykeviewer

.. _`Python`: http://python.org/
.. _`spykeutils`: http://spykeutils.readthedocs.org/
.. _`guiqwt`: http://packages.python.org/guiqwt/
.. _`tables`: http://www.pytables.org/
.. _`neo`: http://neo.readthedocs.org/
.. _`pip`: http://pypi.python.org/pypi/pip
.. _`scipy`: http://scipy.org/
.. _`setuptools`: http://pypi.python.org/pypi/setuptools
.. _`spyder`: http://packages.python.org/spyder/
.. _`Python(x,y)`: http://www.pythonxy.com/
.. _`matplotlib`: http://matplotlib.org/
.. _`NeuroDebian`: http://neuro.debian.net