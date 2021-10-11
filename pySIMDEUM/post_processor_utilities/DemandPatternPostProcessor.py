from traits.api import Either, Str, Instance, Float, List, Any, Int
from pySIMDEUM.core.house import Property, House
import matplotlib.pyplot as plt
import pandas as pd

class DemandPatternPostProcessor():
    _propertytype = Any

    def __init__(self, inputproperty):
        self._consumption = pd.DataFrame()
        self._users = []
        self._enduses = []
        self._propertytype = type(inputproperty)  
        if type(inputproperty) == House:   
            self._consumption, self._users, self._enduses = self._create_house_data(inputproperty)
        elif type(inputproperty) == list:
            for house in inputproperty:
                consumption, users, enduses = self._create_house_data(house)
                self._users.append(users.tolist())
                self._enduses.append(enduses.tolist())
                for column in consumption.columns:
                    if ('user' not in column) and ('household' not in column):
                        if (column in self._consumption.columns) and (column != 'time'):
                            self._consumption[column] += consumption[column]
                        else:
                            self._consumption[column] = consumption[column] 

        else:
            print("Error: input should either be a House or a list of Houses")
    
    def _create_house_data(self, house):
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

    def plot_demand(self):
        if self._propertytype == House:
            fig, (ax1, ax2, ax3) = plt.subplots(1,3, sharey=True)
            for user in self._users:
                ax1.plot(self._consumption['time'], self._consumption[user + ' total'], label=user)
            ax3.plot(self._consumption['time'], self._consumption['total'], label='total')
            for enduse in self._enduses:
                ax2.plot(self._consumption['time'], self._consumption[enduse + ' total'], label=enduse)
            ax1.legend()
            ax1.set_xlabel('time')
            ax1.set_ylabel('demand (l/s)')
            ax2.set_xlabel('time')
            ax3.legend()
            ax3.set_xlabel('time')
            ax2.legend()
            plt.show()
        else:
            fig, ax1 = plt.subplots()
            ax1.plot(self._consumption['time'], self._consumption['total'], label='total')
            ax1.legend()
            ax1.set_xlabel('time')
            ax1.set_ylabel('demand (l/s)')
            plt.show() 

    def createQcfdplot(self, timeinterval=1):
        n_bins = 100
        fig, ax = plt.subplots()
        x = self._consumption['total']
        n, bins, patches = ax.hist(x, n_bins, density=True, histtype='step',
                           cumulative=True, label='Empirical')
        plt.show()



