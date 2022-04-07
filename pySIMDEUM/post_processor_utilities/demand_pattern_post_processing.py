from traits.api import Either, Str, Instance, Float, List, Any, Int
from pySIMDEUM.core.house import HousePattern, Property, House
import matplotlib.pyplot as plt
import pandas as pd
import glob

def plot_demand(houses):
    # houses can either be a house or a list of housefiles
    # if it is a single house it will plot per user, per enduse an a total of pattern 1 and a total of all patterns/num patterns
    #consumption, users, enduses = get_consumption_data(houses)
    if type(houses) == House:
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2,2, sharey=True)
        for user in houses.consumption.user.values:
            ax1.plot(houses.consumption['time'].values, houses.consumption.sel(user=user, patterns=0).sum('enduse').values, label=user)
        ax3.plot(houses.consumption['time'].values, houses.consumption.sel(patterns=0).sum('user').sum('enduse').values, label='total')
        for enduse in houses.consumption.enduse.values:
            ax2.plot(houses.consumption['time'].values, houses.consumption.sel(enduse=enduse, patterns=0).sum('user').values, label=enduse)
        ax4.plot(houses.consumption['time'].values, houses.consumption.sum('user').sum('enduse').sum('patterns').values/len(houses.consumption.patterns), label='average')
        ax1.legend()
        ax1.set_xlabel('time')
        ax1.set_ylabel('demand (l/s)')
        ax2.set_xlabel('time')
        ax3.legend()
        ax3.set_xlabel('time')
        ax3.set_ylabel('demand (l/s)')
        ax4.set_xlabel('time')
        ax2.legend()
        ax4.legend()
        plt.show()
    else:
        #list of housefiles not implemented yet
        test=2

def write_simdeum_patterns_to_xlsx(houses, timestep, Q_option, patternfile_option, output_file):
    # after writeSimdeumPatternToXls (Matlab)
    # house can eithwer be a list of filenames or a list of houses
    # timestep the output timestep of the pattern
    # Q_option for now only 'm3/h' TODO is this true? are the units not L/s?????
    # for now only 1 all patterns in 1 file
    # output_file file to write to
    
    if type(houses[0]) == str:
        count = 0
        output = pd.DataFrame()
        if '.housepattern' in houses[0]: #it are housepattern files
            for housepattern in houses:
                loadedhousepattern = HousePattern(housepattern)
                get_housepattern_output(count, output, loadedhousepattern)
                count +=1
        else: #assumed to be house files
            for house in houses:
                prop = Property()
                loadedhouse = prop.built_house(housefile=house)
                get_house_output(count, output, loadedhouse)
                count +=1
        summedoutput = pd.DataFrame()
        summedoutput['date'] = output['date'].values[0::timestep]
        for column in output.columns:
            if column != 'date':
                summedoutput[column] = output[column].groupby(output.index // timestep).sum().values
        summedoutput.to_excel(output_file)

    else: #.houses
        for house in houses:
            get_house_output(count, output, loadedhouse)
        summedoutput = pd.DataFrame()
        summedoutput['date'] = output['date'].values[0::timestep]
        for column in output.columns:
            if column != 'date':
                summedoutput[column] = output[column].groupby(output.index // timestep).sum().values
        summedoutput.to_excel(output_file)


def get_house_output(count, output, loadedhouse):
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

def get_housepattern_output(count, output, loadedhousepattern):
    if count == 0:
        datelist = []
        valueslist = []
        for i in range(0, len(loadedhousepattern.consumption.patterns)):
            datelist.extend(loadedhousepattern.consumption['time'].values)
            valueslist.extend(loadedhousepattern.consumption.sel(patterns=i).values)
        output['date'] = datelist
    else:
        valueslist = []
        for i in range(0, len(loadedhousepattern.consumption.patterns)):
            valueslist.extend(loadedhousepattern.consumption.sel(patterns=i).values)
    output['pysimdeum ' + str(count)] = valueslist
      

def createQcfdplot(houses, timeinterval=1):
    
    if type(houses) == House:
        n_bins = 100
        fig, ax = plt.subplots()
        x = houses.consumption.sel(patterns=0).sum('user').sum('enduse').values
        n, bins, patches = ax.hist(x, n_bins, density=True, histtype='step',
                            cumulative=True, label='Empirical')
        plt.show()
    else:
        # list of housefiles not implemented yet
        test = 2



