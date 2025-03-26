import pandas as pd
import uuid
import numpy as np
from dataclasses import dataclass
from scipy.stats import truncnorm
from typing import Union
import toml
import xarray as xr
import os
from pysimdeum.data import DATA_DIR


def chooser(data: Union[pd.Series, pd.DataFrame], myproperty: str=''):
    """Function to choose elements from a pd.Series randomly, which consists of keys representing the elements and probabilities as values [-> Statistics object].

    Args:
        data (pd.Series | pd.DataFrame): input data to chose from which can be either a pandas.Series or a pandas.DataFrame
        myproperty (str, optional): If the data is in form of a pandas.DataFrame then the myproperty property defines the column to chose from
    Returns:
        _type_: randomly chosen element from pandas.Series or pandas.DataFrame
    """

    if not myproperty:
        data = pd.Series(data)
    else:
        # if property is nested
        types = data.keys()
        data = pd.Series(index=types,
                         data=[data[x][myproperty] for x in types])

    # take only probabilities which are greater than 0
    data = data[data > 0]

    # normalize probabilities to 0
    data /= (data.sum())

    # choose a random number between 0 and 1 from a uniform distribution
    u = np.random.uniform()

    # choose an element from the Series or DataFrame respectively randomly.
    choose = data[u < data.cumsum()].index[0]

    return choose


def duration_decorator(func):
    """Decorator function for duration.

    This decorator transforms duration from timedelta to total seconds, then performs the function on the
    seconds (e.g. fct_duration for generating durations from a probability distribution), afterwards  it transforms
    the output back to a pd.Timedelta object."""

    def wrapper(*args, **kwargs):

        args = map(lambda x: (pd.Timedelta(x)).total_seconds(), args)
        kwargs = {k: pd.Timedelta(v).total_seconds() for k, v in kwargs.items()}
        # kwargs = map(lambda x: (pd.Timedelta(x)).total_seconds(), kwargs)
        result = func(*args, **kwargs)
        result = to_timedelta(round(result))
        return result

    return wrapper


def normalize(pdf: Union[np.ndarray, pd.Series]) -> Union[np.ndarray, pd.Series]:
    """Normalize probability density function (pdf).

    Args:
        pdf (np.ndarray | pd.Series): probability density as numpy array or pandas.Series 

    Returns:
        np.ndarray | pd.Series: normalized probability density
    """
    pdf = pdf / np.sum(pdf)
    return pdf


def to_timedelta(time: Union[str, float, pd.Timedelta]) -> pd.Timedelta:
    """Transform a time in format string or float to a pandas.Timedelta object. 

    The function raises an exception if the format is not a string, float or pandas.Timedelta object

    Args:
        time (str | float | pd.Timedelta): time in the format string, float or already pandas.Timedelta

    Raises:
        Exception: _description_

    Returns:
        pd.Timedelta: _description_
    """

    if isinstance(time, str):
        value = pd.Timedelta(time)

    elif isinstance(time, (int, float)):
        value = pd.Timedelta(seconds=time)

    elif isinstance(time, pd.Timedelta):
        value = time

    else:
        raise Exception('Value is of unknown type:', type(value), '. It should be of type str, float, or pandas.Timedelta')

    return value


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
        u = np.random.random()
        start = np.argmin(np.abs(np.cumsum(prob_joint) - u)) + int(pd.to_timedelta('1 day').total_seconds()) * day_num
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

def offset_simultaneous_discharge(discharge, start, j, ind_enduse, pattern_num):
    """Checks if the tap is turned off before the end of the duration. If so, updates the start time to the next zero value in the discharge array.

    This function shifts the discharge start time to the next available zero value in the discharge array.

    Args:
        discharge (numpy.ndarray): The array representing the discharge data.
        start (int): The start time of the discharge event in seconds from the beginning of the day.
        j (int): The index of the user.
        ind_enduse (int): The index of the end-use appliance.
        pattern_num (int): The pattern number.

    Returns:
        numpy.ndarray: The updated start index or original array if no zero is found
    """

    if discharge[start, j, ind_enduse, pattern_num, 0] > 0:
        next_zero_timestamp = start + 1
        while next_zero_timestamp < len(discharge) and discharge[next_zero_timestamp, j, ind_enduse, pattern_num, 0] > 0: 
            next_zero_timestamp += 1

        if next_zero_timestamp < len(discharge):
            return next_zero_timestamp # return update start time
        else:
            return discharge

    return start #return original start


def complex_daily_pattern(config, resolution='1s'):
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
    x = config['daily_pattern_input']['x']
    data = list(map(float, x.split(' ')))
    index = pd.timedelta_range(start='00:00:00', freq='1h', periods=25)
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
    s = pd.Series(0, index=index)

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


def xarray_to_metadata_df(ds, array, metadata):
    """Extract from xarray.Dataset to a pd.DataFrame and enrich with event metadata.

    Adds 'usage' and 'event_label' columns to the DataFrame based on the metadata.

    Args:
        ds (xarray.Dataset): The dataset containing the data and metadata.
        array (str): Name of the array in the dataset to be converted to a DataFrame.
        metadata (str): Name of the metadata array in the dataset.

    Returns:
        pd.DataFrame: The enriched DataFrame containing the data and metadata.
    """
    df_ = ds[array].to_dataframe(name='flow').reset_index()
    ref_start = df_['time'].min()
    ref_end = df_['time'].max()
    
    df = df_[df_['flow'] != 0].copy()
    df['usage'] = None
    df['event_label'] = None
    df['discharge_temperature'] = None

    events = ds[metadata].values

    for event in events:
        start_times = [ref_start + pd.Timedelta(seconds=start) for start in np.atleast_1d(event['start'])]
        end_times = [ref_start + pd.Timedelta(seconds=end) for end in np.atleast_1d(event['end'])]
        usage = event['usage'].lower()
        enduse = event['enduse']
        discharge_temperatures = np.atleast_1d(event['discharge_temperature'])

        for start, end, discharge_temperature in zip(start_times, end_times, discharge_temperatures):
            condition = ((df['time'] >= start)
                        & (df['time'] < end)
                        & (df['enduse'] == enduse)
                        & (df['flow'] != 0)
                        )
            
            if isinstance(discharge_temperature, (list, np.ndarray)):
                df.loc[condition, 'discharge_temperature'] = discharge_temperature[:len(df[condition])]
            else:
                df.loc[condition, 'discharge_temperature'] = discharge_temperature

            df.loc[condition, 'usage'] = usage
            df.loc[condition, 'event_label'] = f"{usage}_{start.timestamp()}_{end.timestamp()}"

    return df, ref_start, ref_end
    

def truncated_normal_dis_sampling(mean_value):
    """Samples a value from a truncated normal distribution based on the given mean value.

    Distribution is truncated at 0 to prevent negative values.

    Args:
        mean_value (float): Mean value for the truncated normal distribution.

    Returns:
        float: Sampled value from the truncated normal distribution. If input value is 0, returns 0.
    """
    if mean_value == 0: # if input stat is 0, then should always sample 0
        return 0
    std_dev = mean_value * 0.3 # 30% of meean value is just an educated guess based on data types
    lower_bound = 0
    upper_bound = np.inf
    a, b = (lower_bound - mean_value) / std_dev, (upper_bound - mean_value) / std_dev
    # sample from truncated normal distribution
    sample = truncnorm.rvs(a, b, loc=mean_value, scale=std_dev)

    return sample

def discharge_postprocessing(ds, process_type):
    """
    Helper function to perform post-processing on discharge data. 
    Called by assign_discharge_nutrients and assign_discharge_temperature.

    Args:
        ds (xarray.Dataset): The dataset containing discharge data and discharge events metadata.
        process_type (str): The type of post-processing to perform.
        calculation (function): The function to calculate nutrient concentrations.

    Returns:
        pd.DataFrame: The updated DataFrame containing the discharge data and the nutrient concentrations.
    """

    df, ref_start, ref_end = xarray_to_metadata_df(ds, 'discharge', 'discharge_events')

    toml_file_path = os.path.join(DATA_DIR, 'NL', 'ww_nutrients.toml')
    nutrient_data = toml.load(toml_file_path)

    nutrients = ['n', 'p', 'cod', 'bod5', 'ss', 'amm']
    for nutrient in nutrients:
        df[nutrient] = 0.0

    # group by event_label
    grouped = df.groupby('event_label')

    results = []

    for event_label, event_data in grouped:
        if pd.isna(event_label):
            continue

        # Compute total flow for the event
        total_flow = event_data['flow'].sum()

        if process_type == 'nutrients':
            enduse = event_data['enduse'].iloc[0]
            usage = event_data['usage'].iloc[0]

            # Calculate nutrient concentrations for the event
            nutrient_values = {}
            for nutrient in nutrients:
                mean_value = nutrient_data[enduse][usage][nutrient]
                nutrient_per_use = truncated_normal_dis_sampling(mean_value)
                nutrient_concentration = nutrient_per_use / total_flow if total_flow > 0 else 0
                nutrient_values[nutrient] = nutrient_concentration

            # Assign nutrient concentrations to the event
            for nutrient, value in nutrient_values.items():
                event_data[nutrient] = value

        elif process_type == 'temperature':
            if total_flow > 0:
                temperature_sum = (event_data['discharge_temperature'] * event_data['flow']).sum()
                avg_temperature = temperature_sum / total_flow
            else:
                avg_temperature = 0.0 # No flo

            event_data['discharge_temperature'] = avg_temperature

        results.append(event_data)

    # Combine results back into a single DataFrame
    df = pd.concat(results)

    return df, ref_start, ref_end

def assign_discharge_nutrients(ds):
    """Calculates nutrient concentrations based on simulated discharge flow data.

    Calls the discharge_postprocessing function to extract discharge data and metadata from the dataset,
    and calculate the nutrient concentrations for each event.

    Args:
        ds (xarray.Dataset): The dataset containing discharge data and discharge events metadata.

    Returns:
        pd.DataFrame: The updated DataFrame containing the discharge data and the nutrient concentrations.
    """
    # Call the helper funcion
    df, ref_start, ref_end = discharge_postprocessing(ds, 'nutrients')

    return df, ref_start, ref_end

def discharge_time_agg(df, time_agg='h'):
    """
    Helper function to aggregate the data by time based on the specified time aggregation level.

    Args:
        ds (xarray.Dataset): The dataset containing discharge data and discharge event metadata.
        process_type (str): The type of post-processing to perform.
        time_agg (str, optional): The time aggregation level. Options are:
            - 's': Aggregate by seconds.
            - 'm': Aggregate by minutes.
            - '15min': Aggregate by 15-minute intervals.
            - '30min': Aggregate by 30-minute intervals.
            - 'h': Aggregate by hours (default).
        process_calculation (function): The function to calculate nutrient concentrations or temperature.

    Raises:
        ValueError: If the input DataFrame does not contain the required columns ('time', 'flow', and nutrient types).
        ValueError: If an invalid `time_agg` value is provided.

    Returns:
        pd.DataFrame: A DataFrame containing the aggregated data with the following columns:
            - 'time': The aggregated time intervals.
            - 'flow': The total flow for each time interval.
            - 'value_columns': Nutrient concentrations or temperature values.
    """
    # Round time to the specified aggregation level
    if time_agg == 's':
        df['agg_time'] = df['time']
        freq = 'S'
    elif time_agg == 'm':
        df['agg_time'] = df['time'].dt.floor('min')  # Round to the nearest minute
        freq = 'min'
    elif time_agg == '15min':
        df['agg_time'] = df['time'].dt.floor('15T')  # Round to the nearest 15 minutes
        freq = '15T'
    elif time_agg == '30min':
        df['agg_time'] = df['time'].dt.floor('30T')  # Round to the nearest 30 minutes
        freq = '30T'
    elif time_agg == 'h':
        df['agg_time'] = df['time'].dt.floor('h')  # Round to the nearest hour
        freq = 'H'
    else:
        raise ValueError("Invalid time_agg value. Use 's' for seconds, 'm' for minutes, '15min' for 15mins, '30min' for 30mins, or 'h' for hours.")

    # Group by date and the aggregated time
    df['date'] = df['time'].dt.date
    grouped = df.groupby(['date', 'agg_time'])

    return df, grouped, freq

def hh_discharge_nutrients(ds, time_agg='h'):
    """
    Aggregates discharge data and calculates nutrient concentrations over specified time intervals.

    This function processes discharge data from an xarray.Dataset, calculates nutrient concentrations
    based on flow and event metadata, and aggregates the data over user-specified time intervals.
    Missing timestamps (zero discharge flows) within the specified range are filled with zeros.

    Args:
        ds (xarray.Dataset): The dataset containing discharge data and discharge event metadata.
        time_agg (str, optional): The time aggregation level. Options are:
            - 's': Aggregate by seconds.
            - 'm': Aggregate by minutes.
            - '15min': Aggregate by 15-minute intervals.
            - '30min': Aggregate by 30-minute intervals.
            - 'h': Aggregate by hours (default).

    Raises:
        ValueError: If the input DataFrame does not contain the required columns ('time', 'flow', and nutrient types).
        ValueError: If an invalid `time_agg` value is provided.

    Returns:
        pd.DataFrame: A DataFrame containing the aggregated data with the following columns:
            - 'time': The aggregated time intervals.
            - 'flow': The total flow for each time interval.
            - Nutrient columns (e.g., 'n', 'p', 'cod', 'bod5', 'ss', 'amm'): Nutrient concentrations.
    """
    df, ref_start, ref_end = assign_discharge_nutrients(ds)

    nutrients = ['n', 'p', 'cod', 'bod5', 'ss', 'amm']

    # Check if the DataFrame has the required columns
    if not all(col in df.columns for col in ['time', 'flow'] + nutrients):
        raise ValueError("Input DataFrame must contain columns for time, flow, and all nutrient types.")

    # time aggregation helper function
    df, grouped, freq = discharge_time_agg(df, time_agg)

    # Group by time and calculate total flow
    flow = grouped['flow'].sum()

    # Calculate weighted averages for each nutrient
    weighted_nutrients = {
        nutrient: grouped.apply(lambda g: (g[nutrient] * g['flow']).sum() / g['flow'].sum())
        for nutrient in nutrients
    }

    # Combine results into a single DataFrame
    hh_nutrients = pd.DataFrame(weighted_nutrients)
    hh_nutrients['flow'] = flow

    hh_nutrients = hh_nutrients.reset_index()[['agg_time','flow'] + nutrients].rename(columns={'agg_time': 'time'})

    # Generate a complete range of timestamps between ref_start and ref_end
    full_time_index = pd.date_range(start=ref_start, end=ref_end, freq=freq)
    hh_nutrients = hh_nutrients.set_index('time').reindex(full_time_index, fill_value=0).rename_axis('time').reset_index()

    return hh_nutrients

def assign_discharge_temperature(ds):
    """
    Calculates discharge temperatures based on simulated discharge flow data.

    Calls the discharge_postprocessing function to extract discharge data and metadata from the dataset,
    and calculate the average discharge temperature for each event. Assigns the calculated temperatures to the
    corresponding timestamps in the DataFrame

    Args:
        ds (xarray.Dataset): The dataset containing discharge data and discharge events metadata.

    Returns:
        pd.DataFrame: The updated DataFrame containing the discharge data and the temperatures.

    """

    df, ref_start, ref_end = discharge_postprocessing(ds, 'temperature')

    return df, ref_start, ref_end

def hh_discharge_temperature(ds, time_agg='h'):
    """
    Aggregates discharge data and calculates discharge temperatures over specified time intervals.

    This function processes discharge data from an xarray.Dataset, calculates discharge temperatures
    based on flow and event metadata, and aggregates the data over user-specified time intervals.
    Missing timestamps (zero discharge flows) within the specified range are filled with zeros.

    Args:
        ds (xarray.Dataset): The dataset containing discharge data and discharge event metadata.
        time_agg (str, optional): The time aggregation level. Options are:
            - 's': Aggregate by seconds.
            - 'm': Aggregate by minutes.
            - '15min': Aggregate by 15-minute intervals.
            - '30min': Aggregate by 30-minute intervals.
            - 'h': Aggregate by hours (default).

    Raises:
        ValueError: If the input DataFrame does not contain the required columns ('time', 'flow', and 'discharge_temperature').
        ValueError: If an invalid `time_agg` value is provided.

    Returns:
        pd.DataFrame: A DataFrame containing the aggregated data with the following columns:
            - 'time': The aggregated time intervals.
            - 'flow': The total flow for each time interval.
            - 'discharge_temperature': The average discharge temperature for each time interval.
    """

    df, ref_start, ref_end = assign_discharge_temperature(ds)

    # Check if the DataFrame has the required columns
    if not all(col in df.columns for col in ['time', 'flow', 'discharge_temperature']):
        raise ValueError("Input DataFrame must contain columns for time, flow, and discharge_temperature.")

    # time aggregation helper function
    df, grouped, freq = discharge_time_agg(df, time_agg)

    # Group by time and calculate total flow
    flow = grouped['flow'].sum()    

    # Weighted average discharge temperature
    weighted_temperature = grouped.apply(lambda g: (g['flow'] * g['discharge_temperature']).sum() / g['flow'].sum() if g['flow'].sum() > 0 else None)

    # Combine results
    hh_temp = pd.DataFrame({'flow': flow, 'discharge_temperature': weighted_temperature}).reset_index()

    # Ensure full time range
    full_time_index = pd.date_range(start=ref_start, end=ref_end, freq=freq)
    hh_temp = hh_temp.set_index('agg_time').reindex(full_time_index, fill_value=0).rename_axis('time').reset_index()

    return hh_temp

@dataclass
class Base:
    """Base class of pysimdeum for generating objects. 
    
    The only argument of this parent class is an id which can either be set or will be set to a unique identifier
    """

    id: str = str(uuid.uuid4())
