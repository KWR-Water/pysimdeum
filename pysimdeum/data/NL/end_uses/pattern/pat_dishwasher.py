import pandas as pd
from matplotlib import pyplot as plt

def dishwasher_daily_pattern(x=None, resolution='1s'):

    # todo: last hour of day is not talking into account in the pattern

    if x is None:
        x = '70 49 33 69 30 19 9 37 80 52 52 45 53 78 34 44 38 101 489 390 170 185 240 574 70'
    data = list(map(float, x.split(' ')))
    index = pd.timedelta_range(start='00:00:00', freq='1h', periods=len(data))
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


def dishwasher_discharge_pattern(enduse_pattern, discharge_time=8, resolution='1s', periods=7200):
    index = pd.timedelta_range(start='00:00:00', freq=resolution, periods=periods)
    discharge_pattern = pd.Series(0, index=index)

    # Identify the start and end of each phase_on section
    phase_on_sections = []
    in_phase = False
    for i in range(len(enduse_pattern)):
        if enduse_pattern.iloc[i] > 0 and not in_phase:
            start = enduse_pattern.index[i]
            in_phase = True
        elif enduse_pattern.iloc[i] == 0 and in_phase:
            end = enduse_pattern.index[i-1]
            phase_on_sections.append((start, end))
            in_phase = False
    if in_phase:
        end = enduse_pattern.index[-1]
        phase_on_sections.append((start, end))

    # Calculate the total water consumed for each phase_on section and distribute it as discharge
    for i in range(1, len(phase_on_sections)):
        prev_end = phase_on_sections[i-1][1]
        next_start = phase_on_sections[i][0]
        discharge_end = next_start - pd.Timedelta(seconds=10) # 10 second gap between discharge and next phase_on
        discharge_start = discharge_end - pd.Timedelta(seconds=discharge_time) 

        # Calculate the total water consumed for the phase_on section
        total_water_consumed = enduse_pattern[phase_on_sections[i-1][0]:phase_on_sections[i-1][1]].sum()

        # Calculate the flow rate based on the total water consumed and discharge time
        discharge_rate = total_water_consumed / discharge_time

        # Assign the calculated flow rate to the discharge pattern
        discharge_pattern.loc[discharge_start:discharge_end - pd.Timedelta(seconds=1)] = discharge_rate

    # Account for the final phase_on section (the above just looks at gaps between phase_on sections)
    if len(phase_on_sections) > 0:
        last_start, last_end = phase_on_sections[-1]
        total_water_consumed = enduse_pattern[last_start:last_end].sum()
        flow_rate = total_water_consumed / discharge_time

        # Calculate the time from last_end to the end of the periods time
        remaining_time = periods - int(last_end.total_seconds())
        discharge_start = last_end + pd.Timedelta(seconds=remaining_time // 3) # leave 2/3 of the time for a 'dry' cycle
        discharge_end = discharge_start + pd.Timedelta(seconds=discharge_time)
        discharge_pattern.loc[discharge_start:discharge_end - pd.Timedelta(seconds=1)] = flow_rate

    return discharge_pattern


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

