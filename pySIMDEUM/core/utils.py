import pandas as pd
import uuid
import numpy as np
from dataclasses import dataclass


def chooser(data: pd.Series | pd.DataFrame, myproperty: str=''):
    if not myproperty:
        data = pd.Series(data)
    else:
        # if property is nested
        types = data.keys()
        data = pd.Series(index=types,
                         data=[data[x][myproperty] for x in types])
    data = data[data > 0]
    data /= (data.sum())
    u = np.random.uniform()
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


def normalize(pdf):
    """Normalize probability density function (pdf).

    Args:
        pdf:

    Returns:

    """
    pdf = pdf / np.sum(pdf)
    return pdf


def to_timedelta(value):
    if isinstance(value, str):
        value = pd.Timedelta(value)
    elif isinstance(value, (int, float)):
        value = pd.Timedelta(seconds=value)
    elif isinstance(value, pd.Timedelta):
        pass
    else:
        raise Exception('Value is of unknoen type:', type(value))
    return value

@dataclass
class Base:

    id: str = str(uuid.uuid4())
