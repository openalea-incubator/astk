"""
Provides utilities for scheduling models in simulation
"""
import numpy as np

class TimeControlSet:

    def __init__(self, **kwd):
        """  Create a TimeControlSet , that is a simple class container for named object"""
        self.__dict__.update(kwd)

    def check(self,attname,defaultvalue):
        """ Check if an attribute exists. If not create it with default value """
        if not hasattr(self,attname):
            setattr(self,attname,defaultvalue)


def simple_delay_timing(delay = 1, steps =1):
    return (TimeControlSet(dt=delay) if not i % delay  else TimeControlSet(dt=0) for i in range(steps))
            
            
class TimeControl:

    def __init__(self, delay=None, steps=None, model=None, weather=None, start_date=None):
        """ create a generator-like timecontrol object """
        self.delay = delay
        self.steps = steps
        self.model = model
        self.weather = weather
        self.start_date = start_date

        try:
            self._timing = model.timing(delay=delay, steps=steps, weather=weather, start_date=start_date)
        except:
            if model is not None:
                print('Warning : not able to call model.timing correctly !!!')
            try:
                self._timing =  simple_delay_timing(delay=delay, steps=steps)# a generator of timecontrolset objects to be used during a simulation
            except:
                self._timing = simple_delay_timing()

    def __iter__(self):
        return TimeControl(delay=self.delay, steps=self.steps, model=self.model, weather=self.weather, start_date=self.start_date) 

    def next(self):
        return self._timing.next()
                  
            
class TimeControler:

    def __init__(self, **kwd):
        """ create a controler for parallel run of time controls
            Allows to emulate 'discrete event'-like evaluation of timecontrol objects in a script
        """
        self._timedict = dict(kwd)
        self.numiter = 0
        
    def __iter__(self):
        self._timedict = dict((k,iter(v)) for k,v in self._timedict.iteritems())
        self.numiter = 0
        return self
    
    def next(self):
        d = dict((k,v.next()) for k,v in self._timedict.iteritems())
        if len(d) == 0:
            raise StopIteration
        self.numiter += 1
        return d
        

# new approach

    
def evaluation_sequence(delays):
    """ retrieve evaluation filter from sequence of delays
    """
    seq = [[True if i == 0 else False for i in range(int(d))] for d in delays]
    return reduce(lambda x,y: x + y, seq)

class EvalValue:
    
    def __init__(self, eval, value):
        self.eval = eval
        self.value = value
        
    def __nonzero__(self):
        return self.eval

class IterWithDelays:

    def __init__(self, values = [None], delays = [1]):
        self.delays = delays
        self.values = values
        self._evalseq = iter(evaluation_sequence(delays))
        self._iterable = iter(values)
        
    def __iter__(self):
        return IterWithDelays(self.values, self.delays)
        
    def next(self):
        self.ev = self._evalseq.next()
        if self.ev : 
            try: #prevent value exhaustion to stop iterating
                self.val = self._iterable.next()
            except StopIteration:
                pass
        return EvalValue(self.ev,self.val)


def _truncdata(data, before, after, last):
    d = data.truncate(before = before, after = after)
    if after.to_datetime() < last.to_datetime():
        d = d.ix[:-1,]
    return d
        
def time_control(time_sequence, eval_filter, data=None):
    """ Produces controls for multi-delay or weather dependant models 
    return splited weather data (if given) and delays
      
    :Parameters:
    ----------
    - `time_sequence` (panda dateTime index)
        A sequence of TimeStamps indicating the dates of all elementary time steps of the simulation
    - `eval_filter` a list (same length as time_sequence) of bools indicating the steps at which an evaluation is needed
    - `data` (panda dataframe indexed by date)
        data for the model   
    """
    
    starts = time_sequence[eval_filter]
    ends = starts[1:].tolist() + [time_sequence[-1]]
    last = time_sequence[-1]
    if data is not None:
        controls = [((end - start).total_seconds() / 3600, _truncdata(data, start, end, last)) for start,end in zip(starts,ends)]
    else:
        controls = [((end - start).total_seconds() / 3600, None) for start,end in zip(starts,ends)]
    delays, values = zip(*controls)
    return values, delays
 
  
  
def time_filter(time_sequence, delay = 1):
    """ return an evaluation filter being True at regular period
    
    :Parameters:
    ----------
    - `time_sequence` (panda dateTime index)
        A sequence of TimeStamps indicating the dates of all elementary time steps of the simulation
    - `delay` (int)
        The duration of each period

    """
    
    time = [(t - time_sequence[0]).total_seconds() / 3600 for t in time_sequence]
    filter = [t % delay == 0 for t in time]
    return filter

def time_filter_node(time_sequence, delay = 1):
    filter = time_filter(time_sequence, delay)
    return time_sequence, filter
#time_filter_node.__doc__ = time_filter.__doc__

def date_filter(time_sequence, time_data):
    """
    Return evaluation filter being True at date in time_data
   - time_data : a datetimle indexed panda dataframe
    """
    
    filter = [True if d.to_datetime() in time_data.index.to_datetime() else False for d in time_sequence]
    return filter
    
def date_filter_node(time_sequence, time_data):
    filter = date_filter(time_sequence, time_data)
    return time_sequence, filter, time_data
    
def rain_filter(time_sequence, weather):
    """ return an evaluation filter iterating every rain event and every  between-rain event
    
    :Parameters:
    ----------
    - `time_sequence` (panda dateTime index)
        A sequence of TimeStamps indicating the dates  of all elementary time steps of the simulation
    - `weather` (weather instance)
        weather database (should contain rain column) 
    """
    try:
        rain = weather.data.rain[time_sequence]
    except:
        #strange extract needed on visualea 1.0 (to test again with ipython in visualea)
        rain_data = weather.data[['rain']]
        rain = np.array([float(rain_data.loc[d]) for d in time_sequence])
    #rain = weather_data.rain[time_sequence]   
    rain[rain > 0] = 1
    filter = [True] +(rain[1:] != rain[:-1]).tolist()
    return filter
    
def rain_filter_node(time_sequence, weather):
    filter = rain_filter(time_sequence, weather)
    return time_sequence, filter, weather.data
   
class DegreeDayModel:
    """ Classical degreeday model equation
    """
    
    import numpy as np
    
    def __init__(self, Tbase = 0):
        self.Tbase = Tbase
        
    def __call__(self, time_sequence, weather_data):
        """ Compute thermal time accumulation over time_sequence
           
        :Parameters:
        ----------
        - `time_sequence` (panda dateTime index)
            A sequence of TimeStamps indicating the dates of all elementary time steps of the simulation
        - weather (alinea.astk.Weather instance)
            A Weather database

        """    

        try:
            Tair = weather_data.temperature_air[time_sequence]
        except:
            #strange extract needed on visualea 1.0 (to test again with ipython in visualea)
            T_data = weather_data[['temperature_air']]
            Tair = np.array([float(T_data.loc[d]) for d in time_sequence])
        Tcut = np.maximum(np.zeros_like(Tair), Tair - self.Tbase)
        days = [(t - time_sequence[0]).total_seconds() / 3600 / 24 for t in time_sequence]
        dt = np.array([0] + np.diff(days).tolist())
        return np.cumsum(Tcut * dt)
            
# functional call for nodes
def degree_day_model(Tbase = 0):
    return DegreeDayModel(Tbase)
            
def thermal_time(time_sequence, weather_data, model = DegreeDayModel(Tbase = 0)):
    return model(time_sequence, weather_data)
 
 
def thermal_time_filter(time_sequence, weather, model = DegreeDayModel(Tbase = 0), delay = 10):
    """ return an evaluation filter being True at regular thermal time period
    
    :Parameters:
    ----------
    - `time_sequence` (panda dateTime index)
        A sequence of TimeStamps indicating the dates of all elementary time steps of the simulation
    - weather (alinea.astk.Weather instance)
        A Weather database
    - `model` a model returning Thermal Time accumulation as a function of time_sequence and weather
    - `delay` (int)
        The duration of each period

    """
    
    TT = thermal_time(time_sequence, weather.data, model)
    intTT = np.array(map(int,TT / delay))
    filter = [True] +(intTT[1:] != intTT[:-1]).tolist()
    return filter
   
   
def thermal_time_filter_node(time_sequence, weather, model, delay):
    filter = thermal_time_filter(time_sequence, weather, model, delay)
    return time_sequence, filter, weather.data, model
   
def filter_or(filters):
    return reduce(lambda x,y: np.array(x) | np.array(y), filters)
 
def filter_and(filters):
    return reduce(lambda x,y: np.array(x) & np.array(y), filters)
 
from openalea.core.system.systemnodes import IterNode    
    
class IterWithDelaysNode(IterNode):
    """ Iteration Node """

    def eval(self):
        """
        Return True if the node need a reevaluation
        """
        try:
            if self.iterable == "Empty":
                self.iterable = iter(self.inputs[0])
                self.iterdelay = iter(self.inputs[1])
                self.wait = self.inputs[1][-1]

            if(hasattr(self, "nextval")):
                self.outputs[0] = self.nextval
            else:
                self.outputs[0] = self.iterable.next()
                
            self.nextval = self.iterable.next()
            delay = self.iterdelay.next()
            self.outputs[1] = delay
            return delay

        except TypeError, e:
            self.outputs[0] = self.inputs[0]
            self.outputs[1] = self.inputs[1]
            return False

        except StopIteration, e:
            if self.wait > 1:
                self.wait -= 1
                return True
            else:
                self.iterable = "Empty"
                if(hasattr(self, "nextval")):
                    del self.nextval

                return False


#from datetime import datetime, timedelta
#import pytz
##import numpy as np

# class TimeSequence(object):
    # """ Create / manipulate 'actual time' sequences for simulations 
    # """
    # def __init__(self, start_date ='2000-10-01 01:00:00', time_step = 1, steps = 24):
        # """ Create a datetime sequence from start_date to start_date + steps days, every time step hours
        # datetime object are created as UTC
        # """
        # start = pytz.utc.localize(datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S"))
        # self.steps = steps
        # self.time_steps = [time_step for i in range(steps)]
        # self.time = [start + i * timedelta(hours=time_step) for i in range(steps)]
           
    # def as_localtime(self, local_tz  = pytz.timezone('Europe/Paris'), format = "%Y-%m-%d %H:%M:%S"):
        # return [utc_dt.astimezone(local_tz) for utc_dt in self.time]
        
    # def formated(self, time = None, format = "%Y-%m-%d %H:%M:%S"):
        # if time is None:
            # return [t.strftime(format) for t in self.time]
        # else:
            # return [t.strftime(format) for t in time]