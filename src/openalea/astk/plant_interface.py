def new_canopy(plant_model, age = 0):
    g = plant_model.setup_canopy(age)
    return g, plant_model

def grow_canopy(g,plant_model,time_control):
    g = plant_model.grow(g,time_control)
    return g, plant_model

def plot_canopy(g,plant_model):
    s = plant_model.plot(g)
    return s, plant_model