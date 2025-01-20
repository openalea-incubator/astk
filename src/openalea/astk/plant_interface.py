# -*- python -*-
#
#       Copyright 2016-2025 Inria - CIRAD - INRAe
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       WebSite : https://github.com/openalea/astk
#
#       File author(s): Christian Fournier <christian.fournier@inrae.fr>
#
# ==============================================================================

def new_canopy(plant_model, age = 0):
    g = plant_model.setup_canopy(age)
    return g, plant_model

def grow_canopy(g,plant_model,time_control):
    g = plant_model.grow(g,time_control)
    return g, plant_model

def plot_canopy(g,plant_model):
    s = plant_model.plot(g)
    return s, plant_model