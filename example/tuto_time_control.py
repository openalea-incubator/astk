# Time control
from alinea.astk.TimeControl import *

# Models
from openalea.deploy.shared_data import get_shared_data_path
from alinea.echap.microclimate_leaf import *
from alinea.septo3d.Rapilly import *

meteo01_filepath = get_shared_data_path(['alinea/echap'], 'meteo01.csv')
t_deb = "2000-10-01 01:00:00"
climate_model = MicroclimateLeaf()
weather = Weather(data_file=meteo01_filepath)
rain_interception_model = RapillyInterceptionModel()

rain_timing = TimeControl(delay = 24, steps = 1, model = rain_interception_model, weather = weather)
time_control = rain_timing.next()
print time_control.rain
time_control = rain_timing.next()
print time_control.rain


    
    
    
