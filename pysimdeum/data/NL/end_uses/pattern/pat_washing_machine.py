import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

def washingmachine_daily_pattern(x=None, resolution='1s'):

    if x is None:
        x = '34 24 17 43 41 57 57 212 290 338 392 325 226 222 200 175 124 106 139 185 133 165 101 147 34'
    data = list(map(float, x.split(' ')))
    index = pd.timedelta_range(start='00:00:00', freq='1H', periods=25)
    s = pd.Series(data=data, index=index)
    s = s.resample(resolution).mean().interpolate(method='linear')
    s = s[s.index.days == s.index[0].days]
    return s

mean = 50 # To-do link this to the data in the toml files
dev = 1
average_water_use = np.random.normal(mean, dev)/300 #here we convert the average water use of the washing machine to a water use intensity during the intake moments

def washingmachine_enduse_pattern_normal(resolution='1s', periods=7200, avg = average_water_use):

    value = avg
    
    #value = 1/6 #original value 
    
    index = pd.timedelta_range(start='00:00:00', freq=resolution, periods=periods)
    s = pd.Series(0, index=index)

    s.iloc[0:121] = value
    s.iloc[3600:3660] = value
    s.iloc[4920:4980] = value
    s.iloc[6120:6180] = value

    # s.index = s.index - s.index[0]

    return s

def washingmachine_enduse_pattern_eco(resolution='1s', periods=7200, avg = average_water_use):

    value = avg
    
    #value = 1/6 #original value  
    
    index = pd.timedelta_range(start='00:00:00', freq=resolution, periods=periods)
    s = pd.Series(0, index=index)

    s.iloc[0:121] = value
    s.iloc[4920:4980] = value
    s.iloc[6120:6180] = value

    # s.index = s.index - s.index[0]

    return s

def washingmachine_enduse_pattern_long(resolution='1s', periods=7200, avg = average_water_use):

    value = avg
    
    #value = 1/6 #original value 
    
    index = pd.timedelta_range(start='00:00:00', freq=resolution, periods=periods)
    s = pd.Series(0, index=index)

    s.iloc[0:121] = value
    s.iloc[3600:3660] = value
    s.iloc[4920:4980] = value
    s.iloc[6120:6240] = value

    # s.index = s.index - s.index[0]

    return s


