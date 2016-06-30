#!/usr/bin/env python
# -*- coding: utf-8 -*-

# {# pkglts, pysetup.kwds
# format setup arguments

from setuptools import setup, find_packages


short_descr = "The Alinea.astk package provides utilities for simulation of FSPM models builds under alinea standards"
readme = open('README.rst').read()
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

# find version number in src/alinea/astk/version.py
version = {}
with open("src/alinea/astk/version.py") as fp:
    exec(fp.read(), version)


setup_kwds = dict(
    name='alinea.astk',
    version=version["__version__"],
    description=short_descr,
    long_description=readme + '\n\n' + history,
    author="Christian Fournier, Guillaume Garin, Romain Chapuis, ",
    author_email="christian.fournier __at__ supagro.inra.fr, guillaume.garin __at__ itk.fr, romain.chapuis __at__ supagro.inra.fr, ",
    url='https://github.com/Christian Fournier/astk',
    license='cecill-c',
    zip_safe=False,

    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=parse_requirements("requirements.txt"),
    tests_require=parse_requirements("dvlpt_requirements.txt"),
    entry_points={},
    keywords='',
    test_suite='nose.collector',
)
# #}
# change setup_kwds below before the next pkglts tag

setup_kwds['entry_points']['wralea'] = ['astk = alinea.astk_wralea']

# do not change things below
# {# pkglts, pysetup.call
setup(**setup_kwds)
# #}
