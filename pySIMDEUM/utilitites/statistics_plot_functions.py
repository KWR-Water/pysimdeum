from pySIMDEUM.house import House

def plot_diurnal_pattern(statistics):

    # plot a diurnal pattern based on statistics file
    # after plot_diurnal_pattern.m
    # 
    # Input: statistics object

    num_sim = 1000
    diurnal_pattern = []

    for i in range(num_sim):
        prop = Property(statistics=stats)
        house = prop.built_house()
        house.populate_house()
        house.furnish_house()
        
