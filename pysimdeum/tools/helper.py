import pandas as pd
from typing import Union

from pysimdeum.core.house import House, Property
from pysimdeum.core.statistics import Statistics

def create_diurnal_pattern(statistics: Statistics) -> pd.Series:
    
    num_sim = 500
    time = pd.timedelta_range(start='00:00:00', end='23:59:59', freq='1S')
    diurnal_pattern_week = pd.Series(index=time).fillna(0)
    diurnal_pattern_weekend = pd.Series(index=time).fillna(0)

    for i in range(num_sim):
        prop = Property(statistics=statistics)
        house = prop.built_house()
        house.populate_house()

        for user in house.users:
            user.compute_presence(statistics=statistics)
            presence_week = user.week_presence.fillna(0)
            presence_weekend = user.weekend_presence.fillna(0)
            diurnal_pattern_week = diurnal_pattern_week + presence_week
            diurnal_pattern_weekend = diurnal_pattern_weekend + presence_weekend
    return diurnal_pattern_week, diurnal_pattern_weekend

def create_usage_data(houses: Union[list, House]): #TODO I am not able to tell that it should be a list[str], list[House] or House
    if type(houses) == list:
        appliance_data = pd.DataFrame()
        total_water_usage = 0
        total_users = 0
        total_number_of_days = 0
        appliance_data['total'] = 0
        for inputp in houses:
            if type(inputp) == str: #input file list
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
    total_water_usage = float(inputproperty.consumption.sel(flowtypes='totalflow').sum('user').sum('time').sum('enduse').sum('patterns').values)
    total_patterns = len(inputproperty.consumption.patterns)
    total_users = len(inputproperty.users)
    appliance_data = inputproperty.consumption.sum(dim=['user', 'time', 'patterns']).sel(flowtypes='totalflow')
    appliance_data = appliance_data.as_numpy().to_dataframe('total')
    appliance_data['percentage'] = (appliance_data['total']/total_water_usage)*100
    appliance_data['pp'] = appliance_data['total']/total_users
    number_of_seconds = len(inputproperty.consumption)
    total_number_of_days = number_of_seconds/(60*60*24)
    appliance_data['pppd'] = (appliance_data['pp']/total_patterns)/total_number_of_days
    return appliance_data, total_water_usage, total_users, total_number_of_days, total_patterns