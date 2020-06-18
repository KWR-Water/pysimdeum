from traits.api import Either, Str, Instance, Float, List, Any, Int
from house import Property, House
import matplotlib.pyplot as plt
import pandas as pd

class DemandPatternPostProcessor():
    _property = Instance(Property)

    def __init__(self, inputproperty):
        if type(inputproperty) == House:
            self._property = inputproperty
            self._create_data()
        else:
            print("Error: input should either be a House or a list of Houses")
    
    def _create_data(self):
        self._consumption = pd.DataFrame()
        self._consumption['time'] = self._property.consumption['time'].values
        self._users = self._property.consumption['user'].values
        self._enduses = self._property.consumption['enduse'].values
        for user in self._users:
            for enduse in self._enduses:
                self._consumption[user + ' ' + enduse] = self._property.consumption.sel(user=user, enduse=enduse).values
            self._consumption[user + ' total'] = self._property.consumption.sel(user=user).sum('enduse').values
        for enduse in self._enduses:
            self._consumption[enduse + ' total'] = self._property.consumption.sel(enduse=enduse).sum('user').values
        self._consumption['total'] = self._property.consumption.sum('user').sum('enduse').values

    def plot_demand(self):
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


