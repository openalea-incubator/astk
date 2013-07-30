def new_canopy(plant_model, age = 0):
    g = plant_model.setup_canopy(age)
    return g

def grow_canopy(g,plant_model,time_control):
    plant_model.grow(g,time_control)
    return g

def plot_canopy(g,plant_model):
    plant_model.plot()