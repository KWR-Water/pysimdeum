from pySIMDEUM.core.statistics import Statistics
from pySIMDEUM.core.house import Property
from datetime import datetime
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from pySIMDEUM.post_processor_utilities.ApplianceWaterUse import ApplianceWaterUse
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
    house.simulate(num_patterns=10)

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

#plot_diurnal_pattern(statistics=stats)
#test = get_max_time_diurnal_pattern(statistics=stats)
#print(test)

# house functions
house = simulate_house(2)
#house.save_house('test')

#prop = Property(statistics=stats)
#house2 = prop.built_house(housefile='test.house')
#test2 = 2 
#number_of_houses = 16
#houses = list(map(simulate_house, range(number_of_houses)))
#write_simdeum_patterns_to_epanet(houses, '../Hanoi.inp', 900, {'2':2, '23': 1, '30': 3},'testname')
#write_simdeum_house_to_epanet(houses[10])
#test = get_demand_nodes_epanet('../Hanoi.inp')
#print(test)
#water_use = ApplianceWaterUse(house)
#water_use.plot(plotsubject='pppd')
#enduseresults = list(map(calculate_sum_users, houses, ['enduse']*number_of_houses))
#total_enduse = calculate_total(enduseresults)

#total_number_of_users = sum([len(x.users) for x in houses])
#meanflow = total_enduse.mean(axis=0).mean(axis=0)
#print('average number of users per house is: ', total_number_of_users/number_of_houses)
#print('average water use per person per day is :', total_enduse/total_number_of_users)

#write_simdeum_patterns_to_xlsx(['test.house'], 300, 'm3_h', 1, 'test.xlsx')
plot_demand(house)
createQcfdplot(house)
#print('average flow velocity (in time) is: ', meanflow)
#total_enduse.plot(alpha=0.3)
#total1h = total.rolling('1H').mean()
#print('maximum flow is at: ', total1h.idxmax())
#print('maximum flow is: ', total1h.max())
#print('minimum flow is at: ', total1h.idxmin())
#print('minimum flow is: ', total1h.min())
#total1h.plot(color='k')
#plt.ylim((0, None))
#plt.show()





