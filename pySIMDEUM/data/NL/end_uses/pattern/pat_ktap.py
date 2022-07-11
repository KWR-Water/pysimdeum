import os
import pandas as pd


def ktap_daily_pattern(filename=None, resolution='1s'):

    if filename is None:

        pathname = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(pathname, 'dp_kitchen_tap.txt')

    data = pd.read_csv(filename, header=None).squeeze().values
    index = pd.timedelta_range(start='00:00:00', freq='15Min', end='24:00:00')
    s = pd.Series(data=data, index=index)
    s = s.resample(resolution).mean().interpolate(method='linear')
    # print(s.shape)
    s = s[s.index.days == s.index[0].days]
    # print(s.shape)
    return s
