# <img src="https://raw.githubusercontent.com/openalea/openalea.rtfd.io/master/doc/_static/openalea_web.svg" width="70"/> alinea.astk

**Authors:** Christian Fournier [@christian34](https://github.com/christian34), christian.fournier@inrae.fr

**Institutes:** INRAE

**Status** : Python package

**License** : [Cecill-C](https://cecill.info/licences/Licence_CeCILL-C_V1-en.html)

**URL** : https://github.com/openalea-incubator/astk

## Descriptions

alinea.astk package provides utilities for FSPM model. It include particularly equation to calculate sun irradiance according to sun position and manage weather data.

## Contents

- meteorology : functions to calculate sun irradiance according to sun position
    - sky_irradiance: Equation for determining global horizontal irradiance (GHI), direct normal irradiance (DNI) and diffuse horizontal irradiance under clearsky
condition or estimate them from meteorological data using pvlib library.
    - sun_position: Sun position using pvlib library.
    - sun_position_astk : Astronomical equation for determining sun position.
- OpenAlea_VLE: A generic module embeding an OpenAlea model for use in VLE Platform.
- TimeControl: Provides utilities for scheduling models in simulation.
- Weather: Provides utilities for weather protocol and conversion of some weather variable.
- data_access: Set of function to work with resources that are located inside this package data.
- icosphere : Generation of regular spherical polyhedrons: icospheres and their hexagonal/pentagonal duals.
- plant_interface: ?
- plantgl_utils: A generic module to get plant variable from scene.
- sun_and_sky: A collection of equation for modelling sun position, sun irradiance and sky irradiance.

## Installation

### Requierments

- python > 3.7
- pvlib-python
- numpy
- pandas
- openalea.plangl
- snappy (for windows)

### Users

```
conda create -n astk -c openalea3 - c conda-forge alinea.astk
```

### Developpers

```
conda create -n astk -c openalea3 - c conda-forge alinea.astk
git clone 'https://github.com/openalea-incubator/astk.git'
cd astk
python setup.py install (or develop)
```

## Quick Start

TODO found example

## Documentation
TODO Doc in Readthedoc

## Contributing

All contributions, bug reports, bug fixes, documentation improvements, enhancements, and ideas are welcome.

A detailed overview on how to contribute can be found in the [contributing guide](http://virtualplants.github.io/contribute/devel/git-workflow.html)

