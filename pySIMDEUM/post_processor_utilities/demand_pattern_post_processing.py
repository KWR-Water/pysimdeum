from traits.api import Either, Str, Instance, Float, List, Any, Int
from pySIMDEUM.core.house import Property, House
import matplotlib.pyplot as plt
import pandas as pd
import glob


def get_consumption_data(houses):
    consumption = pd.DataFrame()
    users = []
    enduses = []
    if type(houses) == House:   
        consumption, users, enduses = _create_house_data(houses)
    elif type(houses) == list:
        for house in houses:
            consumption, users, enduses = _create_house_data(house)
            users.append(users.tolist())
            enduses.append(enduses.tolist())
            for column in consumption.columns:
                if ('user' not in column) and ('household' not in column):
                    if (column in consumption.columns) and (column != 'time'):
                        consumption[column] += consumption[column]
                    else:
                        consumption[column] = consumption[column] 

    else:
        print("Error: input should either be a House or a list of Houses")
    
    return consumption, users, enduses
    
def _create_house_data(house):
    consumption = pd.DataFrame()
    consumption['time'] = house.consumption['time'].values
    users = house.consumption['user'].values
    enduses = house.consumption['enduse'].values
    for user in users:
        for enduse in enduses:
            consumption[user + ' ' + enduse] = house.consumption.sel(user=user, enduse=enduse, patterns=0).values
        consumption[user + ' total'] = house.consumption.sel(user=user, patterns=0).sum('enduse').values
    for enduse in enduses:
        consumption[enduse + ' total'] = house.consumption.sel(enduse=enduse, patterns=0).sum('user').values
    consumption['total'] = house.consumption.sel(patterns=0).sum('user').sum('enduse').values

    return consumption, users, enduses

def plot_demand(houses):
    consumption, users, enduses = get_consumption_data(houses)
    if type(houses) == House:
        fig, (ax1, ax2, ax3) = plt.subplots(1,3, sharey=True)
        for user in users:
            ax1.plot(consumption['time'], consumption[user + ' total'], label=user)
        ax3.plot(consumption['time'], consumption['total'], label='total')
        for enduse in enduses:
            ax2.plot(consumption['time'], consumption[enduse + ' total'], label=enduse)
        ax1.legend()
        ax1.set_xlabel('time')
        ax1.set_ylabel('demand (l/s)')
        ax2.set_xlabel('time')
        ax3.legend()
        ax3.set_xlabel('time')
        ax2.legend()
        plt.show()
    else:
        # it makes no sense to create user and enduse plots for multiple houses therefore only a total plot
        fig, ax1 = plt.subplots()
        ax1.plot(consumption['time'], consumption['total'], label='total')
        ax1.legend()
        ax1.set_xlabel('time')
        ax1.set_ylabel('demand (l/s)')
        plt.show()

def write_simdeum_patterns_to_xlsx(houses, timestep, Q_option, patternfile_option, output_file):
    # after writeSimdeumPatternToXls (Matlab)
    # house can eithwer be a list of filenames or a list of houses
    # timestep the output timestep of the pattern
    # Q_option for now only 'm3/h'
    # for now only 1 all patterns in 1 file
    # output_file file to write to
    
    if type(houses[0]) == str:
        count = 0
        output = pd.DataFrame()
        for house in houses:
            prop = Property()
            loadedhouse = prop.built_house(housefile=house)
            if count == 0:
                datelist = []
                valueslist = []
                for i in range(0, len(loadedhouse.consumption.patterns)):
                    datelist.extend(loadedhouse.consumption['time'].values)
                    valueslist.extend(loadedhouse.consumption.sel(patterns=i).sum('user').sum('enduse').values)
                output['date'] = datelist
            else:
                valueslist = []
                for i in range(0, len(loadedhouse.consumption.patterns)):
                    valueslist.extend(loadedhouse.consumption.sel(patterns=i).sum('user').sum('enduse').values)
            output['pysimdeum ' + str(count)] = valueslist
        summedoutput = pd.DataFrame()
        summedoutput['date'] = output['date'].values[0::timestep]
        for column in output.columns:
            if column != 'date':
                summedoutput[column] = output[column].groupby(output.index // timestep).sum().values
        summedoutput.to_excel(output_file)


        
    else: #.houses
        number_of_houses = len(houses)


        

def createQcfdplot(houses, timeinterval=1):
    consumption, users, enduse = get_consumption_data(houses)
    n_bins = 100
    fig, ax = plt.subplots()
    x = consumption['total']
    n, bins, patches = ax.hist(x, n_bins, density=True, histtype='step',
                        cumulative=True, label='Empirical')
    plt.show()



