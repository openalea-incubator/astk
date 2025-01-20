
# This file has been generated at Tue Jul 02 10:08:48 2013

from openalea.core import *


__name__ = 'alinea.astk'

__editable__ = True
__description__ = ''
__license__ = 'CeCILL-C'
__url__ = 'http://openalea.gforge.inria.fr'
__alias__ = []
__version__ = '1.0.0'
__authors__ = ''
__institutes__ = None
__icon__ = ''


__all__ = []

iter_with_delays = Factory(name="iter with delays", 
                  description="Iteration ", 
                  category="flow control", 
                  nodemodule="alinea.astk.TimeControl",
                  nodeclass="IterWithDelaysNode",
                  inputs = (dict(name="generator", interface=None, value=None),
                            dict(name="delay generator", interface=None, value=None),
                            ),
                  outputs = ( dict(name="value", interface=None),
                              dict(name="delay", interface=None),
                              dict(name="trigger", interface=None),
                             ),

                  )
__all__.append('iter_with_delays')

astk_time_control = Factory(name="time_control", 
                  nodemodule="alinea.astk.TimeControl",
                  nodeclass="time_control",
                  outputs = ( dict(name="values", interface=None),
                              dict(name="delays", interface=None),),
                  )
__all__.append('astk_time_control')

astk_rain_filter = Factory(name="rain filter", 
                  nodemodule="alinea.astk.TimeControl",
                  nodeclass="rain_filter_node",
                  outputs = ( dict(name='time_sequence', interface = None),
                              dict(name='filter', interface = None),
                              dict(name='weather', interface = None),),
                  )
__all__.append('astk_rain_filter')

astk_time_filter = Factory(name="time filter", 
                  nodemodule="alinea.astk.TimeControl",
                  nodeclass="time_filter_node",
                  outputs = ( dict(name='time_sequence', interface = None),
                              dict(name='filter', interface = None),)
                  )
__all__.append('astk_time_filter')

astk_date_filter = Factory(name="date filter", 
                  nodemodule="alinea.astk.TimeControl",
                  nodeclass="date_filter_node",
                  outputs = ( dict(name='time_sequence', interface = None),
                              dict(name='filter', interface = None),
                              dict(name='time_data', interface = None),)
                  )
__all__.append('astk_date_filter')

astk_thermal_time_filter = Factory(name="thermal_time filter", 
                  nodemodule="alinea.astk.TimeControl",
                  nodeclass="thermal_time_filter_node",
                  outputs = ( dict(name='time_sequence', interface = None),
                              dict(name='filter', interface = None),
                              dict(name='weather', interface = None),
                              dict(name='model', interface = None),),
                  )
__all__.append('astk_thermal_time_filter')

astk_weather = Factory(name='Weather',
                nodemodule='alinea.astk.Weather',
                nodeclass='weather_node',
                inputs=[{'interface': IFileStr, 'name': 'data_file', 'value': None, 'desc': 'Path to the meteo data file'}],
               )
__all__.append('astk_weather')

default_check = ['temperature_air', 'PPFD', 'relative_humidity', 'wind_speed', 'rain', 'global_radiation', 'vapor_pressure']
astk_weather_check = Factory(name='Weather check',
                nodemodule='alinea.astk.Weather',
                nodeclass='weather_check_node',
                inputs=( dict(name= 'Weather', interface = None),
                         dict(name= 'Variables', interface = ISequence, value = default_check),
                         dict(name= 'Models', interface = IDict, value = {}),),
               )
__all__.append('astk_weather_check')

astk_weather_data = Factory(name='Weather data',
                nodemodule='alinea.astk.Weather',
                nodeclass='weather_data_node',
               )
__all__.append('astk_weather_data')

astk_weather_start = Factory(name='Weather at start',
                nodemodule='alinea.astk.Weather',
                nodeclass='weather_start_node',
               )
__all__.append('astk_weather_start')


panda_date_range = Factory(name="date_range", 
                  description="Time sequence creation", 
                  category="flow control", 
                  nodemodule="alinea.astk.Weather",
                  nodeclass="date_range_node",
                  inputs = (dict(name="start", interface=IDateTime, value=None),
                            dict(name="end", interface=IDateTime, value=None),
                            dict(name="periods", interface=IInt, value=None),
                            dict(name="freq", interface=IStr, value='H'),
                            dict(name="tz", interface=IStr, value=None),
                            dict(name="normalise", interface=IBool, value=False),
                            dict(name="name", interface=IStr, value=None),
                            ),
                  )
__all__.append('panda_date_range')

astk_DegreeDay = Factory(name="DegreeDay", 
                  nodemodule="alinea.astk.TimeControl",
                  nodeclass="degree_day_model",
                  )
__all__.append('astk_DegreeDay')

astk_TimeControl_TimeControl = Factory(name='TimeControl',
                authors=' (wralea authors)',
                description='',
                category='Unclassified',
                nodemodule='alinea.astk.TimeControl',
                nodeclass='TimeControl',
                inputs=[{'interface': IInt, 'name': 'delay', 'value': None, 'desc': ''}, {'interface': IInt, 'name': 'steps', 'value': None, 'desc': ''}, {'interface': None, 'name': 'model', 'value': None, 'desc': ''}, {'interface': None, 'name': 'weather', 'value': None, 'desc': ''}, {'interface': IStr, 'name': 'start_date', 'value': None, 'desc': ''}],
                outputs=[{'interface': None, 'name': 'out', 'desc': ''}],
                widgetmodule=None,
                widgetclass=None,
               )
__all__.append('astk_TimeControl_TimeControl') 



astk_plant_interface_new_canopy = Factory(name='new_canopy',
                authors=' (wralea authors)',
                description='',
                category='Unclassified',
                nodemodule='alinea.astk.plant_interface',
                nodeclass='new_canopy',
                outputs=[{'interface': None, 'name': 'g', 'desc': ''},{'interface': None, 'name': 'model', 'desc': ''}],
                widgetmodule=None,
                widgetclass=None,
               )
__all__.append('astk_plant_interface_new_canopy')



astk_plant_interface_grow_canopy = Factory(name='grow_canopy',
                authors=' (wralea authors)',
                description='',
                category='Unclassified',
                nodemodule='alinea.astk.plant_interface',
                outputs=[{'interface': None, 'name': 'g', 'desc': ''},{'interface': None, 'name': 'model', 'desc': ''}],
                nodeclass='grow_canopy',
                widgetmodule=None,
                widgetclass=None,
               )
__all__.append('astk_plant_interface_grow_canopy')



astk_plant_interface_plot_canopy = Factory(name='plot_canopy',
                authors=' (wralea authors)',
                description='',
                category='Unclassified',
                nodemodule='alinea.astk.plant_interface',
                nodeclass='plot_canopy',
                outputs=[{'interface': None, 'name': 'scene', 'desc': ''},{'interface': None, 'name': 'model', 'desc': ''}],
                widgetmodule=None,
                widgetclass=None,
               )
__all__.append('astk_plant_interface_plot_canopy')
