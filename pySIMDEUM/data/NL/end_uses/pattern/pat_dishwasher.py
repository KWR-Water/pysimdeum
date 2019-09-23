import pandas as pd
from matplotlib import pyplot as plt

def dishwasher_daily_pattern(x=None, resolution='1s'):

    # todo: last hour of day is not talking into account in the pattern

    if x is None:
        x = '70 49 33 69 30 19 9 37 80 52 52 45 53 78 34 44 38 101 489 390 170 185 240 574 70'
    data = list(map(float, x.split(' ')))
    index = pd.timedelta_range(start='00:00:00', freq='1H', periods=len(data))
    s = pd.Series(data=data, index=index)
    s = s.resample(resolution).mean().interpolate(method='linear') # todo interpolate with cubic splines does not work
    s = s[s.index.days == s.index[0].days]


    return s

def dishwasher_enduse_pattern(resolution='1s', periods=7200):

    value = 1/6

    index = pd.timedelta_range(start='00:00:00', freq=resolution, periods=periods)
    s = pd.Series(0, index=index)

    s.iloc[0:24] = value
    s.iloc[1860:1884] = value
    s.iloc[3660:3684] = value
    s.iloc[5460:5472] = value

    # s.index = s.index - s.index[0]

    return s

if __name__ == '__main__':

    pass

    # x = '70 49 33 69 30 19 9 37 80 52 52 45 53 78 34 44 38 101 489 390 170 185 240 574'
    # data = list(map(float, x.split(' ')))
    # index = pd.DatetimeIndex(start='2018/1/1', freq='1H', periods=24)
    # s1 = pd.Series(data=data, index=index)
    #
    # s2 = make_daily_pattern(x=x)
    #
    # fig = plt.figure(1)
    # ax = fig.add_subplot(111)
    #
    # s1.plot(ax=ax, marker='o', linestyle='None')
    # s2.plot(ax=ax)
    # plt.show()

