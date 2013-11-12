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

def time_control(time_sequence, eval_filter, weather=None):
    """ Produces controls for multi-delay or weather dependant models 
    return splited weather data (if given) and delays
      
    :Parameters:
    ----------
    - `time_sequence` (panda dateTime index)
        A sequence of TimeStamps indicating the dates of all elementary time steps of the simulation
    - `eval_filter` a list (same length as time_sequence) of bools indicating the steps at which an evaluation is needed
    - `data` (panda dataframe indexed by date)
        data for the model   
    - `weather' a weather object containing the data
    """
    
    starts = time_sequence[eval_filter]
    ends = starts[1:].tolist() + [time_sequence[-1] + 1]
    if weather is not None:
        controls = [((end - start).total_seconds() / 3600, weather.data.truncate(before = start, after = end).ix[:-1,]) for start,end in zip(starts,ends)]
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
    return time_sequence, filter, weather
   
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
            return delay

        except TypeError, e:
            self.outputs[0] = self.inputs[0]
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