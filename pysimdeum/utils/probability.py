import pandas as pd
import numpy as np
from typing import Union
from scipy.stats import truncnorm
from scipy.optimize import minimize

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


def optimise_probabilities(starting_probs, total_population, total_households, household_sizes):
    """
    Optimises household probabilities to match the total population while staying close to starting probabilities.

    Args:
        starting_probs (list): Initial probabilities for each household category (e.g., census averages).
        total_population (int): Total population within the boundary area.
        total_households (int): Total number of households within the boundary area.
        household_sizes (list): Average household sizes for each category.

    Returns:
        np.ndarray: Optimized probabilities for each household category.
    """
    # Define the objective function (minimize the difference from starting probabilities)
    def objective(probs):
        return np.sum((probs - starting_probs) ** 2)

    # Define the equality constraint: resulting population must match total_population
    def population_constraint(probs):
        return np.dot(probs * total_households, household_sizes) - total_population

    # Define the equality constraint: probabilities must sum to 1
    def sum_constraint(probs):
        return np.sum(probs) - 1

    # Bounds: probabilities must be non-negative
    bounds = [(0, 1) for _ in starting_probs]

    # Initial guess (starting probabilities)
    initial_guess = starting_probs

    # Define constraints
    constraints = [
        {"type": "eq", "fun": population_constraint},
        {"type": "eq", "fun": sum_constraint},
    ]

    # Perform optimization
    result = minimize(
        objective,
        initial_guess,
        bounds=bounds,
        constraints=constraints,
        method="SLSQP"  # Sequential Least Squares Programming
    )

    # Check if optimization was successful
    if not result.success:
        raise ValueError(f"Optimisation failed: {result.message}")

    return result.x