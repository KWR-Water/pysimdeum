from traits.api import Either, Str, Instance, Float, List, Any, Int
from pySIMDEUM.core.house import Property, House
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

def create_usage_data(houses):
    if type(houses) == list:
        appliance_data = pd.DataFrame()
        total_water_usage = 0
        total_users = 0
        total_number_of_days = 0
        appliance_data['total'] = 0
        for inputp in houses:
            if type(inputp == str): #input file list
                prop = Property()
                loadedhouse = prop.built_house(housefile=inputp)
            else:
                loadedhouse = inputp
            one_appliance_data, water_usage, users, number_of_days, patterns = _create_data(loadedhouse)
            for appliance in one_appliance_data.index.values:
                if appliance in appliance_data.index.values:
                    appliance_data.loc[appliance, 'total'] += one_appliance_data.loc[appliance, 'total']
                else:
                    appliance_data.loc[appliance, 'total'] = one_appliance_data.loc[appliance, 'total']
            total_water_usage += water_usage
            total_users += users
            total_number_of_days += number_of_days*patterns
        appliance_data['percentage'] = (appliance_data['total']/total_water_usage)*100
        appliance_data['pp'] = appliance_data['total']/total_users
        appliance_data['pppd'] = appliance_data['pp']/total_number_of_days

    elif type(houses) == House:
        appliance_data, total_water_usage, total_users, total_number_of_days, total_patterns = _create_data(houses)
        
    else:
        print("Error: input should either be a House or a list of Houses")
    
    return appliance_data, total_water_usage, total_users, total_number_of_days

def _create_data(inputproperty):
    total_water_usage = float(inputproperty.consumption.sum('user').sum('time').sum('enduse').sum('patterns').values)
    total_patterns = len(inputproperty.consumption.patterns)
    total_users = len(inputproperty.users)
    appliance_data = inputproperty.consumption.sum('user').sum('time').sum('patterns').to_dataframe('total')
    appliance_data['percentage'] = (appliance_data['total']/total_water_usage)*100
    appliance_data['pp'] = appliance_data['total']/total_users
    number_of_seconds = len(inputproperty.consumption)
    total_number_of_days = number_of_seconds/(60*60*24)
    appliance_data['pppd'] = (appliance_data['pp']/total_patterns)/total_number_of_days
    return appliance_data, total_water_usage, total_users, total_number_of_days, total_patterns
    
def plot_water_use_distribution(inputproperty, plotsubject='percentage'):
    appliance_data, total_water_usage, total_users, total_number_of_days = create_usage_data(inputproperty)
    def func(pct, allvals):
        absolute = pct/100.*np.sum(allvals)
        return "{:.1f}L\n({:.1f}%)".format(absolute, pct)
    if plotsubject != 'total' and plotsubject != 'percentage' and plotsubject != 'pp' and plotsubject != 'pppd':
        print('Plotting subject not known. options are total, percentage (default), pppd (per person per day) and pp (per person)')
    else:
        labels = appliance_data.index.values
        sizes = appliance_data[plotsubject].values
        fig1, ax1 = plt.subplots()
        if plotsubject == 'percentage':
            ax1.pie(sizes, labels=labels, startangle=90, autopct='%1.1f%%')
        else:
            ax1.pie(sizes, labels=labels, startangle=90, autopct=lambda pct: func(pct, sizes))
        fig1.suptitle(plotsubject)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.show()

def print_water_use_distribution(inputproperty):
    appliance_data, total_water_usage, total_users, total_number_of_days = create_usage_data(inputproperty)
    print('Appliance water use distribution')
    print(appliance_data)
    print('Total water usage: ', str(total_water_usage))
    print('Total number of users: ', str(total_users))

def export_water_use_distribution(inputproperty, name='ApplianceWaterUse.xlsx'):
    appliance_data, total_water_usage, total_users, total_number_of_days = create_usage_data(inputproperty)
    writer = pd.ExcelWriter(name, engine = 'xlsxwriter')
    metadata = pd.DataFrame(index=['info'])
    metadata['Total number of Users'] = total_users
    metadata['Total water consumption'] = total_water_usage
    metadata['Total number of days'] = total_number_of_days
    metadata['Calculation date'] = datetime.now().date()
    appliance_data.to_excel(writer, sheet_name = 'data')
    metadata.to_excel(writer, sheet_name = 'metadata')
    writer.close()

def get_data_water_use_distribution(inputproperty):
    appliance_data, total_water_usage, total_users, total_number_of_days = create_usage_data(inputproperty)
    return appliance_data
