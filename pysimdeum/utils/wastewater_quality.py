import pandas as pd
import numpy as np
import os
import toml
from pysimdeum.data import DATA_DIR
from pysimdeum.utils.probability import truncated_normal_dis_sampling


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
    

def discharge_postprocessing(ds, process_type, nutrient_data=None):
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

def assign_discharge_nutrients(ds, country):
    """Calculates nutrient concentrations based on simulated discharge flow data.

    Calls the discharge_postprocessing function to extract discharge data and metadata from the dataset,
    and calculate the nutrient concentrations for each event.

    Args:
        ds (xarray.Dataset): The dataset containing discharge data and discharge events metadata.
        country (str): NL or UK. The country for which the nutrient concentrations are calculated.

    Returns:
        pd.DataFrame: The updated DataFrame containing the discharge data and the nutrient concentrations.
    """
    toml_file_path = os.path.join(DATA_DIR, country, 'ww_nutrients.toml')
    nutrient_data = toml.load(toml_file_path)
    
    # Call the helper funcion
    df, ref_start, ref_end = discharge_postprocessing(ds, 'nutrients', nutrient_data)

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

def hh_discharge_nutrients(ds, country='NL', time_agg='h'):
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
    df, ref_start, ref_end = assign_discharge_nutrients(ds, country)

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

    df, ref_start, ref_end = discharge_postprocessing(ds, 'temperature')

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
