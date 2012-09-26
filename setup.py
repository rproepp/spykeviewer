# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

def find_version():
    try:
        f = open(os.path.join('spykeviewer', '__init__.py'), 'r')
        try:
            for line in f:
                if line.startswith('__version__'):
                    rval = line.split()[-1][1:-1]
                    break
        finally:
            f.close()
    except Exception:
        rval = '0'
    return rval


if __name__ == "__main__":
    version = find_version()
    setup(
        name="spykeviewer",
        version=version,
        packages=find_packages(),
        install_requires=['guidata', 'guiqwt', 'spyder',
                          'spykeutils[plot,plugin]=='+version],
        entry_points = {
            'gui_scripts':
                ['spyke-viewer = spykeviewer.start:main']
        },
        author='Robert Pröpper',
        maintainer='Robert Pröpper',
        description='A multi-platform GUI application for navigating, analyzing and visualizing electrophysiological datasets',
        long_description=open('README.rst', 'r').read(),
        license='BSD',
        url='https://github.com/rproepp/spykeviewer',
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: BSD License',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Scientific/Engineering :: Bio-Informatics'])
