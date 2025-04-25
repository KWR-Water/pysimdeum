import numpy as np
import pandas as pd
from pysimdeum.utils.probability import normalize


def sample_start_time(prob_joint, day_num, duration, previous_events):
    """
    Samples a valid start time for an event, ensuring no overlap with previous events
    and no start within duration before the last sampled start time.

    Args:
        prob_joint (numpy.ndarray): The joint probability distribution.
        day_num (int): The current day number in the simulation.
        duration (int): The duration of the event.
        previous_events (list): List of tuples containing start and end times of previous events.

    Returns:
        int: The sampled start time.
        int: The calculated end time.
    """
    while True:
        start_index = np.random.choice(len(prob_joint), p=prob_joint)
        start = start_index + int(pd.to_timedelta('1 day').total_seconds()) * day_num
        end = start + duration

        # Check for overlapping events or events within duration before the last sample start
        if not any((start < event_end and start >= event_start) or (start < event_start and start >= event_start - int(duration)) for event_start, event_end in previous_events):
            return int(start), int(end)


def handle_spillover_consumption(consumption, pattern, start, end, j, ind_enduse, pattern_num, end_of_day, name, total_days):
    """Handles the spillover of consumption events that extend beyond the end of the current day.

    Splits the consumption event into two parts: the part that fits within the current days and the part that spills over into the next day. The spillover part is moved to the start of the day, making an assumption that appliance had the same usage event beginning the previous day.

    Args:
        consumption (numpy.ndarray): The array representing the consumption data.
        pattern (numpy.ndarray): The pattern of consumption to be applied.
        start (int): The start time of the consumption event in seconds from the beginning of the day.
        end (int): The end time of the consumption event in seconds from the beginning of the day.
        j (int): The index of the user.
        ind_enduse (int): The index of the end-use appliance.
        pattern_num (int): The pattern number.
        end_of_day (int): The end time of the current day in seconds from the beginning of the day.
        name(str): The name of the appliance.
        total_days (int): The total number of days in the simulation.

    Returns:
        numpy.ndarray: The updated consumption array with the spillover consumption handled.
    """
    print("A usage event for ", name, " use has spilled over to the next day. Adjusting spillover times...")
    # Part that fits within the current day
    difference = end_of_day - start
    consumption[start:end_of_day, j, ind_enduse, pattern_num, 0] = pattern[:difference]
    consumption[start:end_of_day, j, ind_enduse, pattern_num, 1] = 0

    # Part that spills over into the next day
    spillover_start = 0
    spillover_end = end - end_of_day

    # Calculate the day index for the spillover
    current_day = start // (24 * 60 * 60)
    next_day = (current_day + 1) % total_days # if next day exceeds total number of days in the sim, wraps around to the beginning (day 0)

    if next_day == 0:
        consumption[spillover_start:spillover_start + spillover_end, j, ind_enduse, pattern_num, 0] = pattern[difference:difference + spillover_end]
        consumption[spillover_start:spillover_start + spillover_end, j, ind_enduse, pattern_num, 1] = 0
    else:
        # Continue to the next day
        spillover_start = next_day * 24 * 60 * 60
        spillover_end = spillover_start + spillover_end
        consumption[spillover_start:spillover_end, j, ind_enduse, pattern_num, 0] = pattern[difference:difference + (spillover_end - spillover_start)]
        consumption[spillover_start:spillover_end, j, ind_enduse, pattern_num, 1] = 0

    print("Spillover consumption adjustment complete.")

    return consumption


def handle_discharge_spillover(discharge, discharge_pattern, time, discharge_time, j, ind_enduse, pattern_num, end_of_day, total_days):
    """Handles the spillover of discharge times that occur beyond the end of the current day, making an assumption that appliance had the same usage event beginning the previous day.

    This function shifts the discharge time to the start of the day.

    Args:
        discharge (numpy.ndarray): The array representing the discharge data.
        discharge_pattern (pandas.Series): The pattern of discharge to be applied.
        time (int): The time in seconds from the start of the appliance pattern
        discharge_time (int): The discharge time in seconds from the beginning of the simulation.
        j (int): The index of the user.
        ind_enduse (int): The index of the end-use appliance.
        pattern_num (int): The pattern number.
        end_of_day (int): The end time of the current day in seconds from the beginning of the day.
        total_days (int): The total number of days in the simulation.

    Returns:
        numpy.ndarray: The updated discharge array with the spillover discharge handled.
    """
    if discharge_time >= (total_days * 24 * 60 * 60):
        spillover_time = discharge_time - end_of_day
        discharge[spillover_time, j, ind_enduse, pattern_num, 1] = discharge_pattern[time]
    else:
        # Continue to the next day
        discharge[discharge_time, j, ind_enduse, pattern_num, 1] = discharge_pattern[time]

    return discharge

def offset_simultaneous_discharge(discharge, start, j, ind_enduse, pattern_num, spillover=False):
    """Checks if the enduse is turned off before the end of the duration. If so, updates the start time to the next zero value in the discharge array.

    This function shifts the discharge start time to the next available zero value in the discharge array.

    Args:
        discharge (numpy.ndarray): The array representing the discharge data.
        start (int): The start time of the discharge event in seconds from the beginning of the day.
        j (int): The index of the user.
        ind_enduse (int): The index of the end-use appliance.
        pattern_num (int): The pattern number.
        spillover (bool): Flag indicating whether to handle spillover.

    Returns:
        numpy.ndarray: The updated start index or original array if no zero is found
    """

    if discharge[start, j, ind_enduse, pattern_num, 0] > 0:
        next_zero_timestamp = start + 1
        while next_zero_timestamp < len(discharge) and discharge[next_zero_timestamp, j, ind_enduse, pattern_num, 0] > 0: 
            next_zero_timestamp += 1

        if next_zero_timestamp < len(discharge):
            return next_zero_timestamp # return update start time
        elif spillover:
            next_zero_timestamp = 0
            while next_zero_timestamp < start and discharge[next_zero_timestamp, j, ind_enduse, pattern_num, 0] > 0:
                next_zero_timestamp += 1

            if next_zero_timestamp < start:
                return next_zero_timestamp
            else:
                print("No zero value found in the discharge array.")
        else:
            return len(discharge) - 1
    else:
        return start #return original start


def complex_daily_pattern(config, resolution='1s', freq='1h'):
    """Generates a daily pattern for water usage based on the provided configuration.

    This function reads the daily pattern data from the provided configuration,
    resamples it to the specified resolution, and interpolates the values to create
    a smooth daily pattern.

    Args:
        config (dict): Configuration dictionary containing the daily pattern data.
        resolution (str, optional): The time resolution for resampling the data. Defaults to '1s'.

    Returns:
        pd.Series: A pandas Series representing the daily pattern, resampled and interpolated
        to the specified resolution.
    """
    if freq not in ['1h', '15Min']:
        raise ValueError("The 'freq' parameter must be either '1h' or '15Min'.")
    
    x = config['daily_pattern_input']['x']
    data = list(map(float, x.split(' ')))
    if freq == '1h':
        index = pd.timedelta_range(start='00:00:00', freq='1h', periods=25)
    elif freq == '15Min':
        index = pd.timedelta_range(start='00:00:00', freq='15Min', end='24:00:00')
    s = pd.Series(data=data, index=index)
    s = s.resample(resolution).mean().interpolate(method='linear')
    s = s[s.index.days == s.index[0].days]
    return s


def complex_enduse_pattern(config, resolution='1s'):
    """Generates the end-use pattern for an appliance with consumption cycles based on the provided configuration.

    This function reads the intensity, runtime, and cycle times from the provided configuration,
    creates a time series for the specified resolution, and assigns the intensity to the specified
    cycle times.

    Args:
        resolution (str, optional): The time resolution for the time series. Defaults to '1s'.

    Returns:
        pd.Series: A pandas Series representing the end-use pattern for the appliance,
        with the specified intensity assigned to the specified cycle times.
    """
    intensity = config['enduse_pattern_input']['intensity']
    runtime = config['enduse_pattern_input']['runtime']
    cycle_times = config['enduse_pattern_input']['cycle_times']

    index = pd.timedelta_range(start='00:00:00', freq=resolution, periods=runtime)
    s = pd.Series(0.0, index=index)

    for cycle in cycle_times:
        start = cycle['start']
        end = cycle['end']
        s.iloc[start:end] = intensity

    return s


def complex_discharge_pattern(config, enduse_pattern, resolution='1s'):
    """Generates the discharge pattern for an appliance with discharge cycles based on the provided configuration and end-use pattern.

    This function reads the discharge time and runtime from the provided configuration,
    identifies the start and end of each phase_on section in the end-use pattern, calculates
    the total water consumed for each section, and distributes it as discharge over the specified
    resolution.

    Args:
        config (dict): Configuration dictionary containing the discharge pattern and end-use pattern data.
        enduse_pattern (pd.Series): A pandas Series representing the end-use pattern for the appliance.
        resolution (str, optional): The time resolution for the discharge pattern. Defaults to '1s'.

    Returns:
        pd.Series: A pandas Series representing the discharge pattern for the appliance,
        with the calculated discharge rates assigned to the specified cycle times.
    """
    discharge_time = config['discharge_pattern_input']['discharge_time']
    runtime = config['enduse_pattern_input']['runtime']

    index = pd.timedelta_range(start='00:00:00', freq=resolution, periods=runtime)
    discharge_pattern = pd.Series(0.0, index=index)

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
        next_start = phase_on_sections[i][0]
        discharge_end = next_start - pd.Timedelta(seconds=10) # 10 second gap between discharge and next phase_on
        discharge_start = discharge_end - pd.Timedelta(seconds=discharge_time) 

        # Calculate the total water consumed for the phase_on section
        total_water_consumed = enduse_pattern[phase_on_sections[i-1][0]:phase_on_sections[i-1][1]].sum()

        # Calculate the flow rate based on the total water consumed and discharge time
        discharge_rate = total_water_consumed / discharge_time

        # Assign the calculated flow rate to the discharge pattern
        discharge_pattern.loc[discharge_start:discharge_end - pd.Timedelta(seconds=1)] = discharge_rate # restrict range to not be inclusive of final timstamp as this would result in extra discharge

    # Account for the final phase_on section (the above just looks at gaps between phase_on sections)
    if len(phase_on_sections) > 0:
        last_start, last_end = phase_on_sections[-1]
        total_water_consumed = enduse_pattern[last_start:last_end].sum()
        flow_rate = total_water_consumed / discharge_time

        # Calculate the time from last_end to the end of the periods time
        remaining_time = runtime - int(last_end.total_seconds())
        discharge_start = last_end + pd.Timedelta(seconds=remaining_time // 3) # leave 2/3 of the time for a 'spin' or 'drain' cycle
        discharge_end = discharge_start + pd.Timedelta(seconds=discharge_time)
        discharge_pattern.loc[discharge_start:discharge_end - pd.Timedelta(seconds=1)] = flow_rate # restrict range to not be inclusive of final timstamp as this would result in extra discharge

    return discharge_pattern
