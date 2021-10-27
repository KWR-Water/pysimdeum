from pySIMDEUM.core.statistics import Statistics
from pySIMDEUM.core.house import Property
from datetime import datetime
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from pySIMDEUM.post_processor_utilities.water_use_distribution_post_processing import plot_water_use_distribution 
from pySIMDEUM.post_processor_utilities.demand_pattern_post_processing import write_simdeum_patterns_to_xlsx, plot_demand, createQcfdplot
from pySIMDEUM.pre_processor_utilities.statistics_utilities import plot_diurnal_pattern, get_max_time_diurnal_pattern
from pySIMDEUM.post_processor_utilities.epanet_integration import write_simdeum_patterns_to_epanet, write_simdeum_house_to_epanet, get_demand_nodes_epanet
import time
#from guppy import hpy
#from pympler import asizeof, classtracker

# test edit to see if test is run
# Simulations for multiple houses:
def simulate_house(x):
    stats = Statistics()
    prop = Property(statistics=stats)
    house = prop.built_house()
    house.populate_house()
    house.furnish_house()
    for user in house.users:
        user.compute_presence(statistics=stats)
    house.simulate(num_patterns=100)

    return house

def calculate_sum_users(house, use):

    #house = simulate_house()
    cons = house.consumption
    data = cons.sum('user').sum(use).to_pandas()
    data.name = house._id
    return data

def calculate_total(inresults):
    results = pd.concat(inresults, axis=1)
    total = results.sum(axis=1)
    total_use = total.sum(axis=0)
    return total_use

#def return_and_plot_water_usage(house):
#    classname_appliances =  [x.statistics['classname'] for x in house.appliances]
#    name_appliances =  [x.name for x in house.appliances]
#    usage_dataframe = pd.Dataframe(columns=classname_appliances)
#     i = 0
#    for name in name_appliances:
#        data = cons.sum('user').sum(name).to_pandas()
#        usage_dataframe[classname_appliances[]]


# statistics functions
#number_of_houses = 10
house = simulate_house(2)
plot_diurnal_pattern(statistics=house.statistics)
#test = get_max_time_diurnal_pattern(statistics=stats)
#print(test)

# house functions

#house.save_house('test')

plot_water_use_distribution(house, plotsubject='pppd')

#write_simdeum_patterns_to_xlsx(['test.house'], 300, 'm3_h', 1, 'test.xlsx')
plot_demand(house)
createQcfdplot(house)






