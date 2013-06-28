"""
Provides utilities for scheduling models in simulation
"""

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
        
    