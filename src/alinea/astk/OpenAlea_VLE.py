""" A generic module embeding an OpenAlea model for use in VLE Platform
"""

# -*- coding:utf-8 -*-

# ******************************************************************************
#
# File OpenAlea_VLE.py
#
#
# ******************************************************************************

# !!! AdelCaribu installe sous pkgs-1.1/pydynamics/pythonsrc
# PyDynamics et convert installes sous pkgs-1.1/pydynamics_wrapper/wrapping

from __future__ import print_function
import PyDynamics
import convert

from openalea.core.alea import load_package_manager, function


###############################################################################

class OpenAlea(PyDynamics.Dynamics):
    def __init__(self, model, events):
        PyDynamics.Dynamics.__init__(self, model, events)
        # get init partameters
        self.conditions = convert.to_pyvalue(events)

        pm = load_package_manager()
        node_factory = pm[self.conditions['openalea_pkgname']][
            self.conditions['openalea_nodename']]
        self.eval = function(node_factory)
        # /!\ on suppose l'unicite des noms entre parametres et attributs des ports
        self.eval_args = dict([(d['name'], -1.) for d in node_factory.inputs])
        self.out_names = [d['name'] for d in node_factory.outputs]
        self.outputs = self.eval(**self.eval_args)
        # set model parameters, if any
        for k in self.conditions.keys():
            if k in self.eval_args.keys():
                self.eval_args[k] = self.conditions[k]

        if "delay" in self.conditions.keys():
            self.p_delay = self.conditions["delay"]
            print("Le 'delay' est de : ", self.p_delay)
        else:
            self.p_delay = 1.0

        print("")

    def init(self, time):
        pass

    def timeAdvance(self):
        return self.p_delay

    def output(self, time, events):
        eventOut = self.buildEvent("Out")
        # /!\ on suppose que la fonction d'openalea renvoie un type convenu
        for i, name in enumerate(self.out_names):
            # print " Valeurs outputs", name, self.outputs[i],convert.to_vlevalue(self.outputs[i])
            eventOut.putAttribute(name, convert.to_vlevalue(self.outputs[i]))
        events.append(eventOut)

    def confluentTransitions(self, time, events):
        internalTransition(time)
        externalTransition(events, time)

    def observation(self, events):
        for i, name in enumerate(self.out_names):
            if events.onPort(name):
                return convert.to_vlevalue(self.outputs[i])

        if events.onPort("RAD_recu"):
            try:
                return convert.to_vlevalue(self.ports['In']['RAD'])
            except KeyError:
                return convert.to_vlevalue(0)
        elif events.onPort("TT_recu"):
            try:
                return convert.to_vlevalue(self.ports['In']['TT'])
            except KeyError:
                return convert.to_vlevalue(0)
        else:
            return convert.to_vlevalue(0)

    def internalTransition(self, time):

        for d in self.ports.values():
            for k in d.keys():
                if k in self.eval_args.keys():
                    self.eval_args[k] = d[k]

        self.outputs = self.eval(**self.eval_args)

    def externalTransition(self, events, time):
        for event in events:
            self.ports.update(GetEventValue(event))


###############################################################################
##
## Get the values of events of an EventList
##
###############################################################################
def GetEventValue(x):
    Name = x.getPortName()
    if x.haveAttributes() == True:
        map = convert.to_pyvalue(x.getAttributes())
    return {Name: map}

##############################################################
