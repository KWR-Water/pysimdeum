import pandas as pd
import matplotlib.pyplot as plt 

from pySIMDEUM.core.house import House, Property

def plot_diurnal_pattern(statistics):

    # plot a diurnal pattern based on statistics object
    # after plot_diurnal_pattern.m
    # 
    # Input: statistics object

    diurnal_pattern = __create_diurnal_pattern(statistics)
    

    plt.plot(diurnal_pattern.index, diurnal_pattern.values)
    plt.show()

def get_max_time_diurnal_pattern(statistics):

    # get the time of maximum usage form a statistics object
    # meant for automatic testing
    #
    # Input: statistics object
    # Output: timedelta of moment of maximum usage days, HH:MM:SS
    
    diurnal_pattern = __create_diurnal_pattern(statistics)
    return diurnal_pattern.idxmax()

def __create_diurnal_pattern(statistics):
    num_sim = 1000
    time = pd.timedelta_range(start='00:00:00', end='23:59:59', freq='1S')
    diurnal_pattern = pd.Series(index=time).fillna(0)

    for i in range(num_sim):
        prop = Property(statistics=statistics)
        house = prop.built_house()
        house.populate_house()

        for user in house.users:
            presence = user.compute_presence(weekday=True, statistics=statistics)
            presence = presence.fillna(0)
            diurnal_pattern = diurnal_pattern + presence
    return diurnal_pattern
