[![Docs](https://readthedocs.org/projects/openalea-astk/badge/?version=latest)](https://openalea-astk.readthedocs.io/)
[![Build Status](https://github.com/openalea-incubator/astk/actions/workflows/conda-package-build.yml/badge.svg?branch=master)](https://github.com/openalea-incubator/astk/actions/workflows/conda-package-build.yml?query=branch%3Amaster)
[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License--CeCILL-C-blue)](https://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html)
[![Anaconda-Server Badge](https://anaconda.org/openalea3/openalea.astk/badges/version.svg)](https://anaconda.org/openalea3/openalea.astk)

# Astk

**Astk** allows to calculate sky luminance and sky sources to be used with FSPM light models from weather data.

## Contents

- sky_irradiance: Equation for determining global horizontal irradiance (GHI), direct normal irradiance (DNI) and diffuse horizontal irradiance under clearsky
condition or estimate them from meteorological data using pvlib library.
- sun_position: Sun position using pvlib library.
- sun_position_astk : Astronomical equation for determining sun position.
- TimeControl: Provides utilities for scheduling models in simulation.
- Weather: Provides utilities for weather protocol and conversion of some weather variable.
- data_access: Set of function to work with resources that are located inside this package data.
- icosphere : Generation of regular spherical polyhedrons: icospheres and their hexagonal/pentagonal duals.
- plantgl_utils: A generic module to get plant variable from scene.
- sky_sources: A collection of equation for modelling sun position, sun irradiance and sky irradiance.

## Installation

### Users

```
mamba create -n astk -c openalea3 -c conda-forge openalea.astk openalea.plantgl matplotlib
```

### Developpers

```bash
git clone 'https://github.com/openalea-incubator/astk.git'
cd astk
# this will create a fresh astk_dev env for you
mamba env create -f ./conda/environment.yml
# As an alternative, if you want to work in an existing environment:
mamba install --only-deps -c openalea3 - c conda-forge openalea.astk
pip install -e .[doc,test,plot]
```

## Quick start

```python
from openalea.astk.sky_irradiance import sky_irradiance
from openalea.astk.sky_sources import sky_sources

irradiance = sky_irradiance()
sources = sky_sources('all-weather', irradiance)
```

See other example in the documentation

## Credits

The package was mainly developed by Christian Fournier [@christian34](https://github.com/christian34), researcher at INRAE.

All contributions, bug reports, bug fixes, documentation improvements, enhancements, and ideas are welcome.

A detailed overview on how to contribute can be found in the [contributing guide](http://virtualplants.github.io/contribute/devel/git-workflow.html)

### Contributors

Thanks to all that ontribute making this package what it is !

<a href="https://github.com/openalea-incubator/astk/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=openalea-incubator/astk" />
</a>


