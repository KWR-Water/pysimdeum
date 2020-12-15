from traits.api import Either, Str, Instance, Float, List, Any, Int
from pySIMDEUM.core.house import Property, House
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

class ApplianceWaterUse():
    _property = Instance(Property)
    _propertylist = List
    _total_water_usage = Float
    _total_users = Int
    _appliance_data = Any
    _total_number_of_days = Int

    def __init__(self, inputproperty):
        if type(inputproperty) == list:
            self._appliance_data = pd.DataFrame()
            self._total_water_usage = 0
            self._total_users = 0
            self._total_number_of_days = 0
            self._appliance_data['total'] = 0
            for inputp in inputproperty:
                appliance_data, total_water_usage, total_users, total_number_of_days = self._create_data(inputp)
                for appliance in appliance_data.index.values:
                    if appliance in self._appliance_data.index.values:
                        self._appliance_data.loc[appliance, 'total'] += appliance_data.loc[appliance, 'total']
                    else:
                        self._appliance_data.loc[appliance, 'total'] = appliance_data.loc[appliance, 'total']
                self._total_water_usage += total_water_usage
                self._total_users += total_users
                self._total_number_of_days = total_number_of_days
            self._appliance_data['percentage'] = (self._appliance_data['total']/self._total_water_usage)*100
            self._appliance_data['pp'] = self._appliance_data['total']/self._total_users
            self._appliance_data['pppd'] = self._appliance_data['pp']/self._total_number_of_days

        elif type(inputproperty) == House:
            self._property = inputproperty
            self._appliance_data, self._total_water_usage, self._total_users, self._total_number_of_days = self._create_data(inputproperty)
        else:
            print("Error: input should either be a House or a list of Houses")

    def _create_data(self, inputproperty):
        total_water_usage = float(inputproperty.consumption.sum('user').sum('time').sum('enduse').values)
        total_users = len(inputproperty.users)
        appliance_data = inputproperty.consumption.sum('user').sum('time').to_dataframe('total')
        appliance_data['percentage'] = (appliance_data['total']/total_water_usage)*100
        appliance_data['pp'] = appliance_data['total']/total_users
        number_of_seconds = len(inputproperty.consumption)
        total_number_of_days = number_of_seconds/(60*60*24)
        appliance_data['pppd'] = appliance_data['pp']/total_number_of_days
        return appliance_data, total_water_usage, total_users, total_number_of_days
    
    def plot(self, plotsubject='percentage'):
        def func(pct, allvals):
            absolute = pct/100.*np.sum(allvals)
            return "{:.1f}L\n({:.1f}%)".format(absolute, pct)
        if plotsubject != 'total' and plotsubject != 'percentage' and plotsubject != 'pp' and plotsubject != 'pppd':
            print('Plotting subject not known. options are total, percentage (default), pppd (per person per day) and pp (per person)')
        else:
            labels = self._appliance_data.index.values
            sizes = self._appliance_data[plotsubject].values
            fig1, ax1 = plt.subplots()
            if plotsubject == 'percentage':
                ax1.pie(sizes, labels=labels, startangle=90, autopct='%1.1f%%')
            else:
                ax1.pie(sizes, labels=labels, startangle=90, autopct=lambda pct: func(pct, sizes))
            fig1.suptitle(plotsubject)
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            plt.show()

    def print(self):
        print('Appliance water use distribution')
        print(self._appliance_data)
        print('Total water usage: ', str(self._total_water_usage))
        print('Total number of users: ', str(self._total_users))
    
    def export(self, name='ApplianceWaterUse.xlsx'):
        writer = pd.ExcelWriter(name, engine = 'xlsxwriter')
        metadata = pd.DataFrame(index=['info'])
        metadata['Total number of Users'] = self._total_users
        metadata['Total water consumption'] = self._total_water_usage
        metadata['Total number of days'] = self._total_number_of_days
        metadata['Calculation date'] = datetime.now().date()
        self._appliance_data.to_excel(writer, sheet_name = 'data')
        metadata.to_excel(writer, sheet_name = 'metadata')
        writer.close()
    
    def get_data(self):
        return self._appliance_data
