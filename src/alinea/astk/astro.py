""" Astronommic computations (copy of caribu/skytools/spitters-horaire
"""
from math import *

def DecliSun(DOY):
    """ Declinaison (rad) du soleil en fonction du jour de l'annee """
    alpha = 2 * pi * (DOY - 1) / 365
    return (0.006918 - 0.399912 * cos(alpha) + 0.070257 * sin(alpha))

def DayLength(latitude, decli):
    """ photoperiode (radians) en fonction de latitude (degre) et declinaison du soleil (rad) """
    lat = radians(latitude)
    d = acos(-tan(decli) * tan(lat))
    if d < 0:
        d = d + pi    
    return 2 * d

def dH(angleH):
    """ duration (hour) from  daylength angle (radians)"""
    return 24 / (2 * pi) * angleH
    
def extra(Rg, DOY, heureTU, latitude):
    """ rayonnement extraterrestre horarire """
    hrad = 2 * pi / 24 * (heureTU - 12)
    lat = radians(latitude)
    dec = DecliSun (DOY)
    costheta = sin(lat) * sin(dec) + cos(lat) * cos(dec) * cos(hrad)
    Io = 1370 * (1 + 0.033 * cos(2 * pi * (DOY - 4) / 366))#eclairement (w/m2) a la limitte de l'atmosphere dans un plan perpendiculaire aux rayons du soleil, fonction du jour
    So = Io * costheta #eclairement dans un plan parallele a la surface du sol
    return So

    

