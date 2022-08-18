from pysimdeum.core.statistics import Statistics
from pysimdeum.core.house import Property, HousePattern
from datetime import datetime
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from pysimdeum.tools.plot import view_statistics, plot_demand, createQcfdplot, plot_water_use_distribution
from pysimdeum.tools.write import write_simdeum_patterns_to_ddg
import time
import os
import copy
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
    house.simulate(num_patterns=1)

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
#plot_diurnal_pattern(stats)

test = simulate_house(2)
test2 = simulate_house(2)
ax = plot_water_use_distribution([test, test2])
plt.show()
#write_simdeum_patterns_to_ddg([test], 3600, 'm3/h', 1, 'test.ddg')


# statistics functions
#houselist = []
#outputdir = 'workdir'
#os.mkdir(outputdir)
if False:
    list_number_of_houses = [2, 10, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600]
    house = simulate_house(2)
    housepattern = HousePattern(house)
    prevmin1use = housepattern.consumption.resample(time='1Min').sum(dim='time')/len(housepattern.users)
    prevmin15use = housepattern.consumption.resample(time='15Min').sum(dim='time')/len(housepattern.users)
    prevhouruse = housepattern.consumption.resample(time='1H').sum(dim='time')/len(housepattern.users)
    prevdayuse = housepattern.consumption.resample(time='1D').sum(dim='time')/len(housepattern.users)
    data = pd.DataFrame()
    for number_of_houses in list_number_of_houses:
        print('running number of houses: ')
        print(number_of_houses)
        for n in range(0, number_of_houses):
            i = 0
            house = simulate_house(2)
        #    patternname = 'housepattern' + str(n)
        #    houselist.append(outputdir + '/' + patternname + '.housepattern')
            housepattern = HousePattern(house)
            tempmin1use = housepattern.consumption.resample(time='1Min').sum(dim='time')/len(housepattern.users)
            tempmin15use = housepattern.consumption.resample(time='15Min').sum(dim='time')/len(housepattern.users)
            temphouruse = housepattern.consumption.resample(time='1H').sum(dim='time')/len(housepattern.users)
            tempdayuse = housepattern.consumption.resample(time='1D').sum(dim='time')/len(housepattern.users)
            if i == 0:
                newdayuse = tempdayuse
                newhouruse = temphouruse
                newmin1use = tempmin1use
                newmin15use = tempmin15use
                totusers = len(housepattern.users)
            else:
                newdayuse += tempdayuse
                newhouruse += temphouruse
                newmin1use += tempmin1use
                newmin15use += tempmin15use
                totusers += len(housepattern.users)
            i +=1
        newdayuse = newdayuse/number_of_houses
        newhouruse = newhouruse/number_of_houses	
        newmin1use = newmin1use/number_of_houses
        newmin15use = newmin15use/number_of_houses
        data.at[number_of_houses, 'day dif'] = (abs(newdayuse-prevdayuse)).sum('time').values[0]
        data.at[number_of_houses, 'hour dif'] = (abs(newhouruse-prevhouruse)).sum('time').values[0]
        data.at[number_of_houses, '15 min dif'] = (abs(newmin15use-prevmin15use)).sum('time').values[0]
        data.at[number_of_houses, '1 min dif'] = (abs(newmin1use-prevmin1use)).sum('time').values[0]
        prevdayuse = copy.deepcopy(newdayuse)
        prevhouruse = copy.deepcopy(newhouruse)
        prevmin15use = copy.deepcopy(newmin15use)
        prevmin1use = copy.deepcopy(newmin1use)

    data.to_csv('difference_house_patterns.csv', sep=';')
        #    housepattern.save_house_pattern(outputdir + '/' + patternname)


    #write_simdeum_patterns_to_xlsx(houselist, 1, 'm3_h', 1, 'test400_1second.xlsx')
    #write_simdeum_patterns_to_xlsx(houselist, 900, 'm3_h', 1, 'test10pat_15minute.xlsx')







