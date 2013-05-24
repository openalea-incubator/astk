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

class TimeControl:

    def __init__(self, delay=1, steps=1, model=None, weather=None):
        """ create a generator-like timecontrol object """
        self.delay = delay
        self.steps = steps
        self.model = model
        self.weather = weather
        
        try:
            self._timing = model.get_timing(delay=delay, steps = steps, model = model, weather = weather)
        except:
            self._timing = (TimeControlSet(dt=delay) if not i % delay  else TimeControlSet(dt=0) for i in range(steps)) # a generator of timecontrolset objects to be used during a simulation

    def __iter__(self):
        return self
    
    def next(self):
        return self._timing.next()
        
    def reset(self):
        new = TimeControl(delay = self.delay, steps = self.steps, model = self.model, weather = self.weather) 
        self._timing = new._timing
        
    def check_dt(self):
        l = [tc.dt for tc in self._timing]
        self.reset()
        return l
                  
            
class TimeControler:

    def __init__(self, TimeControl_list):
        """ create a controler for parallel run of time controls
            Allows to emulate 'discrete event'-like evaluation of timecontrol objects in a script
        """
        self._timelist = TimeControl_list
        
    def __iter__(self):
        return self
    
    def next(self):
        return map(next, self._timelist)
        
    def reset(self):
        map(lambda(x): x.reset(), self._timelist)

    