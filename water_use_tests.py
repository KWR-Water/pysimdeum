from pySIMDEUM.statistics import Statistics
from pySIMDEUM.house import Property
from datetime import datetime
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from pySIMDEUM.utilitites.ApplianceWaterUse import ApplianceWaterUse
from pySIMDEUM.utilitites.DemandPatternPostProcessor import DemandPatternPostProcessor

# test edit to see if test is run
# Simulations for multiple houses:
def simulate_house(x):
    prop = Property(statistics=stats)
    house = prop.built_house()
    house.populate_house()
    house.furnish_house()
    for user in house.users:
        user.compute_presence(statistics=stats)
    house.simulate()
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




#number_of_houses = 2
stats = Statistics()
#houses = list(map(simulate_house, range(number_of_houses)))

prop = Property(statistics=stats)
house = prop.built_house()
house.populate_house()
house.furnish_house()
for user in house.users:
    user.compute_presence(statistics=stats)
house.simulate()
#enduseresults = list(map(calculate_sum_users, houses, ['enduse']*number_of_houses))
#total_enduse = calculate_total(enduseresults)

house2 = prop.built_house()
house2.populate_house()
house2.furnish_house()
for user in house2.users:
    user.compute_presence(statistics=stats)
house2.simulate()

#total_number_of_users = sum([len(x.users) for x in houses])
#meanflow = total_enduse.mean(axis=0).mean(axis=0)
#print('average number of users per house is: ', total_number_of_users/number_of_houses)
#print('average water use per person per day is :', total_enduse/total_number_of_users)

water_use = ApplianceWaterUse(house)
water_use.plot()
#water_use.print()
#water_use.export()

demandpatternpostprocessor = DemandPatternPostProcessor([house, house2])
demandpatternpostprocessor.plot_demand()
demandpatternpostprocessor.createQcfdplot()
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





