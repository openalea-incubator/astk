import pandas as pd
from openalea import astk
from openalea.astk.meteorology.sky_irradiance import sky_irradiance
from openalea.astk.sky_map import sky_grid, sky_map
from openalea.astk.meteorology.sky_luminance import sky_luminance
from openalea.astk.sky_sources import scale_sky_sources
from openalea.astk.icosphere import turtle_mesh, spherical_face_centers


fn = 'climsorj.meteo'

def day2hour(daydate, global_radiation, location):
    """
    Compute hourly global radiation from daily global radiation
    """
    # Compute hourly global radiation
    # 1. Compute the ratio of the global radiation at the hour to the global radiation at the day
    # 2. Multiply the ratio by the global radiation at the day
    # 3. Return the hourly global radiation


    
    # sky irradiance return in W/s
    factor = 3600/1e6
    cs=sky_irradiance(daydate=daydate, **location)
    attenuation = cs.ghi.sum()*factor/global_radiation
    cs=sky_irradiance(daydate=daydate, attenuation=attenuation, **location)


    return cs


def test_day_to_hour():
    names=['station', 'year', 'month', 'day', 'julian', 'min_temp', 'max_temp', 'rad', 'Penman PET', 'rainfall', 'wind', 'pressure', 'CO2']
    df = pd.read_csv(fn,  header=None, sep='\s+', names=names)
    df["Date"] = pd.to_datetime(df[["year", "month", "day"]])

    STICS_Montpellier ={
    'longitude': 3.87,
    'latitude': 45,
    'altitude': 56,
    'timezone': 'Europe/Paris'}


    for row in df.itertuples():
        cs = day2hour(daydate=row.Date, global_radiation=row.rad, location=STICS_Montpellier)
        sky_sources = data_to_caribu(cs)
        print(sky_sources)

def data_to_caribu(irradiance):
    """
    Convert irradiance data to Caribu format
    """
    # Convert irradiance data to Caribu format
    # 1. Create a Caribu scene
    # 2. Add the irradiance data to the Caribu scene
    # 3. Return the Caribu scene

    grid=sky_grid()
    #lum=sky_luminance(grid, 'all_weather', irradiance) # ERROR
    lum=sky_luminance(grid, 'blended', irradiance) # error

    sky_mesh = turtle_mesh(46)
    targets = spherical_face_centers(sky_mesh)
    sky_sources, skymap = sky_map(grid, lum, targets)

    assert((sky_sources<0).sum()==0)
    #sky_sources = scale_sky_sources(sky_sources, irradiance,'molPAR') # PAR luminance integrated over the time-periode


    # Then run caribu...
    return sky_sources

def bug1():
    location ={
    'longitude': 3.87,
    'latitude': 45,
    'altitude': 56,
    'timezone': 'Europe/Paris'}
    
    daydate= '1996-03-31'
    global_radiation= 1
    cs = day2hour(daydate, global_radiation, location)

