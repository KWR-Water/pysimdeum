from pysimdeum.core.statistics import Statistics
from pysimdeum.core.house import Property, HousePattern, House
import pandas as pd
from datetime import datetime


def built_house(house_type: str = "", date=None, duration='1 day', frequency='1s') -> House:

    stats = Statistics()
    prop = Property(statistics=stats)
    house = prop.built_house(house_type=house_type)
    house.populate_house()
    house.furnish_house()
    
    if date is None:
        date = datetime.now().date()
    try:
        timedelta = pd.to_timedelta(duration)
    except:
        print('Warning: duration unrecognized defaulted to 1 day')
        timedelta = pd.to_timedelta('1 day')

    house.date = date
    house.timedelta = timedelta
    house.frequency = frequency

    for user in house.users:
        for day in range(0, timedelta.days):
            if date.weekday() < 5:
                weekday = True
            else:
                weekday = False

            user.compute_presence(statistics=stats, weekday=weekday, day=day, frequency = frequency)
        user.presence = user.presence[~user.presence.index.duplicated(keep='first')]
    #house.simulate(num_patterns=100)

    return house
