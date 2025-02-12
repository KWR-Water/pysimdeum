import pandas as pd
import uuid
import numpy as np
from dataclasses import dataclass
from typing import Union


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
            return start, end

def handle_spillover_consumption(consumption, pattern, start, end, j, ind_enduse, pattern_num, end_of_day, name):
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

    Returns:
        numpy.ndarray: The updated consumption array with the spillover consumption handled.
    """
    print("An event for ", name, " use has spilled over to the next day. Adjusting spillover times...")
    # Part that fits within the current day
    difference = end_of_day - start
    consumption[start:end_of_day, j, ind_enduse, pattern_num, 0] = pattern[:difference]
    consumption[start:end_of_day, j, ind_enduse, pattern_num, 1] = 0

    # Part that spills over into the next day
    spillover_start = 0
    spillover_end = end - end_of_day
    consumption[spillover_start:spillover_start + spillover_end, j, ind_enduse, pattern_num, 0] = pattern[difference:difference + spillover_end]
    consumption[spillover_start:spillover_start + spillover_end, j, ind_enduse, pattern_num, 1] = 0
    print("Spillover adjustment complete.")

    return consumption


def handle_discharge_spillover(discharge, discharge_pattern, time, discharge_time, j, ind_enduse, pattern_num, end_of_day):
    """Handles the spillover of discharge times that occur beyond the end of the current day, making an assumption that appliance had the same usage event beginning the previous day.

    This function shifts the discharge time to the start of the day.

    Args:
        discharge (numpy.ndarray): The array representing the discharge data.
        discharge_pattern (pandas.Series): The pattern of discharge to be applied.
        time (int): The time in seconds from the start of the appliance pattern
        discharge_time (int): The discharge time in seconds from the beginning of the day.
        j (int): The index of the user.
        ind_enduse (int): The index of the end-use appliance.
        pattern_num (int): The pattern number.
        end_of_day (int): The end time of the current day in seconds from the beginning of the day.

    Returns:
        numpy.ndarray: The updated discharge array with the spillover discharge handled.
    """
    spillover_time = discharge_time - end_of_day
    discharge[spillover_time, j, ind_enduse, pattern_num, 0] = discharge_pattern[time]

    return discharge


@dataclass
class Base:
    """Base class of pysimdeum for generating objects. 
    
    The only argument of this parent class is an id which can either be set or will be set to a unique identifier
    """

    id: str = str(uuid.uuid4())
