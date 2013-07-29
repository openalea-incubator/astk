#-*- coding:utf-8 -*-

#******************************************************************************
#
# File AdelCaribu.py
#
#------------------------------------------------------------------------------
#
# Un modele Dynamics partiel
#
#------------------------------------------------------------------------------
#
#******************************************************************************

# !!! AdelCaribu installe sous pkgs-1.1/pydynamics/pythonsrc
# PyDynamics et convert installes sous pkgs-1.1/pydynamics_wrapper/wrapping

import PyDynamics
import convert

from openalea.core.alea import load_package_manager, function
import sys
print sys.path
###############################################################################

class OpenAlea(PyDynamics.Dynamics):

    def __init__(self, model, events): 
        PyDynamics.Dynamics.__init__(self, model, events)
        valeur_python = convert.to_pyvalue( events )
        if "modelname" in valeur_python.keys() :
            self.m_name = valeur_python["modelname"]
        print ""
        print "-----------------------------------------------"
	print "-------- ", self.m_name, " : __init__ --------------"            
        self.m_choix = 1

        print "valeur python de events : ", valeur_python
        print "lecture des elements  1 a 1 : "
        for k,v in valeur_python.iteritems() :
            print "key : ", k, "value : ", v

        self.conditions = valeur_python

        pm = load_package_manager()
        node_factory = pm[self.conditions['openalea_pkgname']][self.conditions['openalea_nodename']]
        self.eval = function(node_factory)
        # /!\ on suppose l'unicité des noms entre paramètres et attributs des ports
        self.eval_args = dict([(d['name'],-1.) for d in node_factory.inputs])
        self.out_names = [d['name'] for d in node_factory.outputs]
        self.outputs = self.eval(**self.eval_args)
        for k in self.conditions.keys() :
            if k in self.eval_args.keys() :        
                self.eval_args[k] = self.conditions[k]

        if "delay" in valeur_python.keys() :
            self.p_delay = valeur_python["delay"]
            print "Le 'delay' est de : ", self.p_delay 
        else : 
            self.p_delay = 1.0

        print ""

    def init(self, time): 
        print ""
        print "-----------------------------------------------"
	print "---------- ", self.m_name, " : init ----------------"
        print "valeur python de time : ", time
        print ""
        print "Construction de 'Values'"
	self.ports={}
        # /!\ donc convert.py -> gérer le none
        #self.ALAI = -1.0
        #self.RadPlant = -1.0
        print ""
        return 0.0 

    def timeAdvance(self):
        print ""
        print "-----------------------------------------------"
	print "----- ", self.m_name, " : Time Advance -------------"
        print "Delay : ", self.p_delay
        print ""
        return self.p_delay


    def output(self,time,events):
        print ""
        print "-----------------------------------------------"
	print "--------- ", self.m_name, " : output ---------------" 
        print "valeur python de time : ", time

        eventOut= self.buildEvent("Out")
        # /!\ on suppose que la fonction d'openalea renvoie un type convenu
        for i,name in enumerate(self.out_names) :
            print " Valeurs outputs", name, self.outputs[i],convert.to_vlevalue(self.outputs[i])
            eventOut.putAttribute(name,convert.to_vlevalue(self.outputs[i]))      
            print "Event Ok !!!!!"

        events.append(eventOut)
        
        for event in events :
            print "Envoie de l'évènement :", eventOut.getPortName()
        print ""

    def confluentTransitions(self, time, events):
        print ""
        print "-----------------------------------------------"
	print "--- ", self.m_name, " : confluentTransition --------" 
        print "valeur python de time : ", time      
        internalTransition(time)
        externalTransition(events, time)
        print ""
    
    def observation(self, events):
        #print ""
        #print "-----------------------------------------------"
	#print "------- ", self.m_name, " : observation ------------" 
        #print ""
        for i,name in enumerate(self.out_names) :
             if events.onPort(name) :
                 return convert.to_vlevalue(self.outputs[i])

        if events.onPort("RAD_recu") :
	    try:
                return convert.to_vlevalue(self.ports['In']['RAD'])      	    
	    except KeyError:
	        return convert.to_vlevalue(0)
        elif events.onPort("TT_recu") :
	    try:
                return convert.to_vlevalue(self.ports['In']['TT'])      	    
	    except KeyError:
	        return convert.to_vlevalue(0)
        else :
            return convert.to_vlevalue(0)
 
  
    def internalTransition(self, time):
        self.m_choix = self.m_choix + 1
        self.density = 5.0
	#print "AttrRad:",self.ports['RAD']['AttrRAD']
        print "Ports :", self.ports

        for d in self.ports.values() : 
            for k in d.keys() :
                if k in self.eval_args.keys() :        
                    self.eval_args[k] = d[k]
      	    
        self.outputs = self.eval(**self.eval_args)

        print ""
        print "-----------------------------------------------"
	print "--- ", self.m_name, " : internalTransition ---------" 
        print "valeur python de time : ", time
        #self.ALAI = self.ALAI+1;
        #self.RadPlant = self.RadPlant+2;
        #print "valeur python de ALAI : ", self.ALAI
        #print "valeur python de RadPlant : ", self.RadPlant
        print "valeur python de Outputs : ", self.outputs
        print ""
        
    def externalTransition(self, events, time):
        print ""
        print "-----------------------------------------------"
	print "--- ", self.m_name, " : externalTransition ---------" 
        print "valeur python de time : ", time
        for event in events : 
            self.ports.update(GetEventValue( event ))
            print ""
        print ""

###############################################################################
##
## Get the values of events of an EventList
##
###############################################################################
def GetEventValue( x ) :

    Name = x.getPortName ()
    print "Evenement(s) du port %s."%Name
    if x.haveAttributes () == True :
        map = convert.to_pyvalue(x.getAttributes())
        for k,v in map.iteritems() :
            print "L'evenement recus du port %s est :"%k, v
    else:
	print "Pas d'attribut pour l'evenement du port", Name
    return {Name:map}
	
    
##############################################################

