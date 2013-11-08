# Time control
from alinea.astk.TimeControl import *
import pandas


# Models
from openalea.deploy.shared_data import shared_data
from alinea.echap.microclimate_leaf import *
import alinea.septo3d
from alinea.septo3d.Rapilly import *

meteo_path = shared_data(alinea.septo3d, 'meteo00-01.txt')
t_deb = "2000-10-01 01:00:00"
weather = Weather(data_file=meteo_path, sep="\t")
seq = pandas.date_range(start = "2000-10-02", periods=24, freq='H', tz='UTC')

delays, datas = rain_split(seq, weather.data)
rain_timing = Timing(delays,datas)

delays,_ = time_split(seq, delay = 3)
wheat_timing = Timing(delays)

for i,controls in enumerate(zip(rain_timing, wheat_timing)):
    raining,growing = controls
    print '\niteration %d'%(i)
    if raining:
        print 'it s raining'
        print raining.data
    else:
        print 'It s not raining'
        
    if growing:
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


    
    
    
