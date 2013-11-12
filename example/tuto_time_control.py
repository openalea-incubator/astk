# Time control
from alinea.astk.TimeControl import *
import pandas


# Models
from openalea.deploy.shared_data import shared_data
from alinea.echap.microclimate_leaf import *
import alinea.septo3d
from alinea.septo3d.Rapilly import *

from alinea.astk.Weather import Weather


meteo_path = shared_data(alinea.septo3d, 'meteo00-01.txt')
t_deb = "2000-10-01 01:00:00"
weather = Weather(data_file=meteo_path)
seq = pandas.date_range(start = "2000-10-02", periods=24, freq='H', tz='UTC')

every_rain = rain_filter(seq, weather)
every_3h = time_filter(seq, delay=3)

rain_timing = IterWithDelays(*time_control(seq, every_rain, weather))
wheat_timing = IterWithDelays(*time_control(seq, every_3h)) # no weather data as values

for i,controls in enumerate(zip(rain_timing, wheat_timing)):
    rain_eval,wheat_eval = controls
    print '\niteration %d'%(i)
    if rain_eval:
        if rain_eval.value.rain.sum() > 0:
            print 'it s raining'
            print rain_eval.value
    else:
        print 'It s not raining'
        
    if wheat_eval:
        print 'wheat is growing'
    else:
        print 'wheat is not growing'
 

    

#
# climate_model = MicroclimateLeaf()
# rain_interception_model = RapillyInterceptionModel()

# rain_timing = TimeControl(delay = 24, steps = 4, model = rain_interception_model, weather = weather)
# time_control = rain_timing.next()
# print time_control.rain
# time_control = rain_timing.next()
# print time_control.rain


    
    
    
