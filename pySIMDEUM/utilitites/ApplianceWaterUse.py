from traits.api import Either, Str, Instance, Float, List, Any, Int
from pySIMDEUM.house import Property, House
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

class ApplianceWaterUse():
    _property = Instance(Property)
    _propertylist = List
    _total_water_usage = Float
    _total_users = Int
    _appliance_data = Any
    _total_number_of_days = Int

    def __init__(self, inputproperty):
        if type(inputproperty) == List:
            self._propertylist = inputproperty
            print("A list of properties is not implemented yet")
        elif type(inputproperty) == House:
            self._property = inputproperty
            self._create_data()
        else:
            print("Error: input should either be a House or a list of Houses")

    def _create_data(self):
        self._total_water_usage = float(self._property.consumption.sum('user').sum('time').sum('enduse').values)
        self._total_users = len(self._property.users)
        self._appliance_data = self._property.consumption.sum('user').sum('time').to_dataframe('Total consumption per appliance')
        self._appliance_data['percentage'] = (self._appliance_data['Total consumption per appliance']/self._total_water_usage)*100
        self._appliance_data['per person'] = self._appliance_data['Total consumption per appliance']/self._total_users
        number_of_seconds = len(self._property.consumption)
        self._total_number_of_days = number_of_seconds/(60*60*24)
        self._appliance_data['per person per day'] = self._appliance_data['per person']/self._total_number_of_days
    
    def plot(self, plotsubject='percentage'):
        if plotsubject != 'total' and plotsubject != 'percentage' and plotsubject != 'pp' and plotsubject != 'pppd':
            print('Plotting subject not known. options are total, percentage (default), pppd (per person per day) and pp (per person)')
        else:
            labels = self._appliance_data.index.values
            sizes = self._appliance_data[plotsubject].values
            fig1, ax1 = plt.subplots()
            ax1.pie(sizes, labels=labels, startangle=90, autopct='%1.1f%%')
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
