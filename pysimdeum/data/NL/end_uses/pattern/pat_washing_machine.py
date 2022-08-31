import pandas as pd
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


def washingmachine_enduse_pattern(resolution='1s', periods=7200):

    value = 1/6

    index = pd.timedelta_range(start='00:00:00', freq=resolution, periods=periods)
    s = pd.Series(0, index=index)

    s.iloc[0:121] = value
    s.iloc[3600:3660] = value
    s.iloc[4920:4980] = value
    s.iloc[6120:6180] = value

    # s.index = s.index - s.index[0]

    return s


