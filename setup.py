#!/usr/bin/env python
# -*- coding: utf-8 -*-

# {# pkglts, pysetup.kwds
# format setup arguments

from os import walk
from os.path import abspath, normpath
from os.path import join as pj

from setuptools import setup, find_namespace_packages


short_descr = "The OpenAlea.astk package provides utilities for simulation of FSPM models builds under alinea standards"
readme = open('README.md').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')


def parse_requirements(fname):
    with open(fname, 'r') as f:
        txt = f.read()

    reqs = []
    for line in txt.splitlines():
        line = line.strip()
        if len(line) > 0 and not line.startswith("#"):
            reqs.append(line)

    return reqs

# find version number in src/openalea/astk/version.py
version = {}
with open("src/openalea/astk/version.py") as fp:
    exec(fp.read(), version)
version_astk = version["__version__"]

data_files = []

nb = len(normpath(abspath("src/openalea/astk/data"))) + 1


def data_rel_pth(pth):
    """ Return path relative to pkg_data
    """
    abs_pth = normpath(abspath(pth))
    return abs_pth[nb:]


for root, dnames, fnames in walk("src/openalea/astk/data"):
    for name in fnames:
        data_files.append(data_rel_pth(pj(root, name)))


setup_kwds = dict(
    name='openalea.astk',
    version=version_astk,
    description=short_descr,
    long_description=readme + '\n\n' + history,
    author="Christian Fournier, Guillaume Garin, Romain Chapuis, ",
    author_email="christian.fournier __at__ inrae.fr ",
    url='https://github.com/openalea/astk',
    license='cecill-c',
    zip_safe=False,

    packages=find_namespace_packages(where='src', include=['alinea.*', 'openalea.*']),
    package_dir={'': 'src'},
    
    include_package_data=True,
    package_data={'openalea.astk.data': data_files},
    #install_requires=parse_requirements("requirements.txt"),
    #tests_require=parse_requirements("dvlpt_requirements.txt"),
    entry_points={},
    keywords='',
)
# #}
# change setup_kwds below before the next pkglts tag

setup_kwds['entry_points']['wralea'] = ['astk = openalea.astk_wralea']

# do not change things below
# {# pkglts, pysetup.call
setup(**setup_kwds)
# #}
