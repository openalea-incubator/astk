# Time control
from alinea.astk.TimeControl import *
import pandas



# Models
from openalea.deploy.shared_data import shared_data
#from alinea.echap.microclimate_leaf import *
import alinea.septo3d
#from alinea.septo3d.Rapilly import *

from alinea.astk.Weather import Weather
from alinea.echap.interception_leaf import pesticide_applications

meteo_path = shared_data(alinea.septo3d, 'meteo00-01.txt')
t_deb = "2000-10-01 01:00:00"
weather = Weather(data_file=meteo_path)
seq = pandas.date_range(start = "2000-10-02", periods=24, freq='H')

applications = """date,dose, product_name
2000-10-02 01:00:00, 1.5, Opus
2000-10-01 05:00:00, 2, Banko 500
2000-10-01 08:00:00, 1.2, Opus
"""
pest_calendar = pesticide_applications(applications)


TTmodel = DegreeDayModel(Tbase = -2)

every_rain = rain_filter(seq, weather)
every_3h = time_filter(seq, delay=3)
every_5dd = thermal_time_filter(seq, weather, TTmodel, delay = 5)
every_pest = date_filter(seq, pest_calendar)

rain_timing = IterWithDelays(*time_control(seq, every_rain, weather.data))
wheat_timing = IterWithDelays(*time_control(seq, every_3h)) # no weather data as values
septo_timing = IterWithDelays(*time_control(seq, filter_or([every_5dd, every_rain])))
pest_timing = IterWithDelays(*time_control(seq, every_pest, pest_calendar))

for i,controls in enumerate(zip(rain_timing, wheat_timing, septo_timing)):
    rain_eval,wheat_eval, septo_eval = controls
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
 
    if septo_eval:
        print 'septo is growing'
    else:
        print 'septo is not growing'
    

#
# climate_model = MicroclimateLeaf()
# rain_interception_model = RapillyInterceptionModel()

# rain_timing = TimeControl(delay = 24, steps = 4, model = rain_interception_model, weather = weather)
# time_control = rain_timing.next()
# print time_control.rain
# time_control = rain_timing.next()
# print time_control.rain


    
    
    
