import copy
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from pysimdeum.core.utils import chooser, duration_decorator, normalize, to_timedelta
from pysimdeum.core.statistics import Statistics	


#TODO: Specific EndUse __post_init__ calls can be replaced by directly using the class name instead of setting the name attributes

@dataclass
class EndUse:
    """Base class for end-uses."""
    
    statistics: Statistics = field(repr=False)  # ... statistic object associated with end-use
    name: str = "EndUse"  # ... name of the end-use

    def init_consumption(self, users: list=None, time_resolution: str='1s') -> pd.DataFrame:
        """Initialization of a pandas dataframe to store the  consumptions.

        Args:
            users:  list with users
            time_resolution:  string with desired time resolution as python pandas `DateOffset` object
            (https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#dateoffset-objects)

        Returns:
            consumption as pandas `DataFrame` filled with zeros
        """

        if users:
            # produce datetime index
            index = pd.TimedeltaIndex(start='00:00:00', end='24:00:00', freq=time_resolution, closed='left')

            # name columns by users
            columns = ['user_' + str(x+1) for x, user in enumerate(users)]

            # initialise consumption dataframe with timedelta index and user columnnames, name it according to end-use
            # device and fill it with zeros.
            consumption = pd.DataFrame(data=0, index=index, columns=columns)
            consumption.name = self.name
        else:
            # raise an error if no users are defined.
            raise Exception('No Users are defined!')

        return consumption

    @staticmethod
    def usage_probability(time_resolution: str='1s') -> pd.Series:
        """Produces uninformed prior.

        For more specific usage probabilities (washing machine, kitchen tap, dishwasher) overload this function by
        loading a usage pattern into it.
        """
        # produce datetime index
        index = pd.timedelta_range(start='00:00:00', end='24:00:00', freq=time_resolution, closed='left')

        prob = pd.Series(data=1, index=index)  # ... uniform probability over time and cast it into pandas series.
        prob /= prob.sum()  # ... normalization of the probabilities

        return prob

    def fct_frequency(self):
        """Placeholder for specific frequency probability function defined in specific EndUse"""

        raise NotImplementedError('Frequency function is not implemented yet!')

    def fct_duration(self):
        """Placeholder for specific duration probability function defined in specific EndUse"""

        raise NotImplementedError('Duration function is not implemented yet!')

    def fct_intensity(self):
        """Placeholder for specific intensity probability function defined in specific EndUse"""

        raise NotImplementedError('Intensity function is not implemented yet!')

    def fct_duration_intensity(self):
        """Computing duration and intensity for enduse"""

        duration = self.fct_duration()
        intensity = self.fct_intensity()

        return duration, intensity

@dataclass
class Bathtub(EndUse):
    """Class for Bathtub end-use."""


    def __post_init__(self):
        """Initialisation function of Bathtub end-use class.

        Args:
            name: End-use name as string.
            **kwargs: keyword arguments for super classes.
        """
        self.name = "Bathtub"

    def fct_frequency(self, age=None):
        """Random function computing the frequency of use for the Bathtub end-use class.

        Args:
            age: age of the user in years.

        Returns:
            distribution function from `numpy.random` to compute frequency of use.

        """
        f_stats = self.statistics['frequency']
        distribution = getattr(np.random, f_stats['distribution'].lower())
        average = f_stats['average'][age]

        return distribution(average)

    def fct_duration(self):
        """Function to compute the duration of Bathtub end-use.

        Comment: The duration is fixed to 10 minutes in this case.

        Returns:
            duration (fixed value as integer)

        """
        # fixed duration
        return int(to_timedelta(self.statistics['duration']).total_seconds())

    def fct_intensity(self):
        """Compute the intensity of Bathtub end-use.

        Returns:
            intensity (fixed value as float)

        """
        # fixed intensity
        return self.statistics['intensity']

    def simulate(self, consumption, users=None, ind_enduse=None, pattern_num=1, day_num=0):

        prob_usage = self.usage_probability().values

        for j, user in enumerate(users):
            freq = self.fct_frequency(age=user.age)
            prob_user = user.presence.values

            for i in range(freq):

                duration, intensity = self.fct_duration_intensity()
                prob_joint = normalize(prob_user * prob_usage)

                u = np.random.uniform()
                start = np.argmin(np.abs(np.cumsum(prob_joint) - u)) + int(pd.to_timedelta('1 day').total_seconds())*day_num
                end = start + duration

                consumption[start:end, j, ind_enduse, pattern_num] = intensity

        return consumption


@dataclass
class BathroomTap(EndUse):
    
    def __post_init__(self):
        self.name = "BathroomTap"

    def fct_frequency(self):

        f_stats = self.statistics['frequency']
        distribution = getattr(np.random, f_stats['distribution'].lower())
        average = f_stats['average']
        return distribution(average)

    def fct_duration_intensity(self):

        subtype = chooser(self.statistics['subtype'], 'penetration')

        d_stats = self.statistics['subtype'][subtype]['duration']
        i_stats = self.statistics['subtype'][subtype]['intensity']

        dist = duration_decorator(getattr(np.random, d_stats['distribution'].lower()))
        mean = to_timedelta(np.log(to_timedelta(d_stats['average']).total_seconds()) - 0.5)
        duration = dist(mean=mean).total_seconds()

        dist = getattr(np.random, i_stats['distribution'].lower())
        low = i_stats['low']
        high = i_stats['high']

        intensity = dist(low=low, high=high)

        return duration, intensity

    def simulate(self, consumption, users=None, ind_enduse=None, pattern_num=1, day_num=0):

        prob_usage = self.usage_probability().values

        for j, user in enumerate(users):
            freq = self.fct_frequency()
            prob_user = user.presence.values

            for i in range(freq):

                duration, intensity = self.fct_duration_intensity()

                prob_joint = normalize(prob_user * prob_usage)

                u = np.random.uniform()
                start = np.argmin(np.abs(np.cumsum(prob_joint) - u)) + int(pd.to_timedelta('1 day').total_seconds())*day_num
                end = int(start + duration)
                consumption[start:end, j, ind_enduse, pattern_num] = intensity

        return consumption

@dataclass
class Dishwasher(EndUse):

    def __post_init__(self):
        self.name = "Dishwasher"

    def fct_frequency(self, numusers=None):

        f_stats = self.statistics['frequency']
        distribution = getattr(np.random, f_stats['distribution'].lower())

        df = pd.Series(f_stats['average'])
        average = df[str(numusers)]  * numusers
        return distribution(average)

    def fct_duration_pattern(self, start=None):
        pattern = self.statistics['enduse_pattern']
        return pattern

    def simulate(self, consumption, users=None, ind_enduse=None, pattern_num=1, day_num=0):

        prob_usage = copy.deepcopy(self.statistics['daily_pattern'].values)
        freq = self.fct_frequency(numusers=len(users))

        for j, user in enumerate(users):
            if j == 0:
                prob_user = copy.deepcopy(user.presence)
            else:
                prob_user += user.presence

        prob_user = normalize(prob_user.values)
        j = len(users)

        prob_joint = normalize(prob_user * prob_usage)

        pattern = self.fct_duration_pattern().values
        duration = len(pattern)

        for i in range(freq):

            u = np.random.random()
            start = np.argmin(np.abs(np.cumsum(prob_joint) - u)) + int(pd.to_timedelta('1 day').total_seconds())*day_num
            end = start + duration

            if end > (24 * 60 * 60):  #ToDo: Find better way to simulate dishwashers that are turned on in the night
                end = 24 * 60 * 60
            difference = end - start
            consumption[start:end, j, ind_enduse, pattern_num] = pattern[:difference]

        return consumption

@dataclass
class KitchenTap(EndUse):

    def __post_init__(self):
        self.name = "KitchenTap"

    def fct_frequency(self, numusers=None):

        f_stats = self.statistics['frequency']
        distribution = getattr(np.random, f_stats['distribution'].lower())

        df = pd.Series(f_stats['average'])
        average = df[str(numusers)]

        df = pd.Series(f_stats['sigma'])
        sigma = df[str(numusers)]

        # Todo: find out which implementation is right? Mirjam (implemented here) or Wikipedia

        # Implementation according to Wikipedia
        # p = (sigma ** 2 - average) / (sigma ** 2)
        # r = (average ** 2) / (sigma ** 2 - average)

        # implementation according to Mirjam
        p = average / sigma ** 2
        r = p * average / (1 - p)

        return distribution(r, p)

    def fct_duration_intensity(self):

        subtype = chooser(self.statistics['subtype'], 'penetration')

        d_stats = self.statistics['subtype'][subtype]['duration']
        i_stats = self.statistics['subtype'][subtype]['intensity']

        dist = getattr(np.random, d_stats['distribution'].lower())
        mean = np.log(pd.Timedelta(d_stats['average']).total_seconds()) - 0.5

        duration = int(pd.Timedelta(seconds=dist(mean=mean)).total_seconds())

        dist = getattr(np.random, i_stats['distribution'].lower())
        low = i_stats['low']
        high = i_stats['high']

        intensity = dist(low=low, high=high)

        return duration, intensity

    def simulate(self, consumption, users=None, ind_enduse=None, pattern_num=1, day_num=0):

        prob_usage = copy.deepcopy(self.statistics['daily_pattern'].values)

        for j, user in enumerate(users):
            if j == 0:  # ToDo: Add function that computes usage probability for all users
                prob_user = copy.deepcopy(user.presence)
            else:
                prob_user += user.presence

        prob_user = normalize(prob_user).values

        j = len(users)

        freq = self.fct_frequency(numusers=len(users))

        for i in range(freq):

            duration, intensity = self.fct_duration_intensity()
            u = np.random.uniform()
            prob_joint = normalize(prob_user * prob_usage)  # ToDo: Check if joint probability can be computed outside of for loop for all functions
            start = np.argmin(np.abs(np.cumsum(prob_joint) - u)) + int(pd.to_timedelta('1 day').total_seconds())*day_num
            end = start + duration
            consumption[start:end, j, ind_enduse, pattern_num] = intensity

        return consumption

@dataclass
class OutsideTap(EndUse):

    def __post_init__(self):
        self.name = "OutsideTap"

    def fct_frequency(self):

        f_stats = self.statistics['frequency']
        distribution = getattr(np.random, f_stats['distribution'].lower())
        average = f_stats['average']
        return distribution(average)

    def fct_duration_intensity(self):

        subtype = chooser(self.statistics['subtype'], 'penetration')

        d_stats = self.statistics['subtype'][subtype]['duration']
        i_stats = self.statistics['subtype'][subtype]['intensity']

        dist = getattr(np.random, d_stats['distribution'].lower())
        mean = np.log(pd.Timedelta(d_stats['average']).total_seconds()) - 0.5

        duration = int(pd.Timedelta(seconds=dist(mean=mean)).total_seconds())

        dist = getattr(np.random, i_stats['distribution'].lower())
        low = i_stats['low']
        high = i_stats['high']

        intensity = dist(low=low, high=high)

        return duration, intensity

    def simulate(self, consumption, users=None, ind_enduse=None, pattern_num=1, day_num=0):

        prob_usage = self.usage_probability().values

        freq = 0
        for j, user in enumerate(users):
            if j == 0:
                prob_user = copy.deepcopy(user.presence)
            else:
                prob_user += user.presence
            freq += self.fct_frequency()

        prob_user = normalize(prob_user).values

        j = len(users)

        for i in range(freq):

            duration, intensity = self.fct_duration_intensity()

            prob_joint = normalize(prob_user * prob_usage)
            u = np.random.uniform()
            start = np.argmin(np.abs(np.cumsum(prob_joint) - u)) + int(pd.to_timedelta('1 day').total_seconds())*day_num
            end = start + duration

            consumption[start:end, j, ind_enduse, pattern_num] = intensity

        return consumption

@dataclass
class Shower(EndUse):

    def __post_init__(self):
        self.name = "Shower"

    def fct_frequency(self, age=None):

        f_stats = self.statistics['frequency']
        distribution = getattr(np.random, f_stats['distribution'].lower())
        n = f_stats['n']
        p = f_stats['p'][age]

        return distribution(n, p)

    def fct_duration_intensity(self, age=None):

        d_stats = self.statistics['duration']
        distribution = getattr(np.random, d_stats['distribution'].lower())
        df = to_timedelta(d_stats['df'][age])

        df = int(df.total_seconds() / 60)
        duration = round(distribution(df))
        duration = int(pd.Timedelta(minutes=duration).total_seconds())

        intensity = self.statistics['subtype'][self.name]['intensity']

        return duration, intensity

    def simulate(self, consumption, users=None, ind_enduse=None, pattern_num=1, day_num=0):

        prob_usage = self.usage_probability().values

        for j, user in enumerate(users):
            freq = self.fct_frequency(age=user.age)
            prob_user = user.presence.values

            for i in range(freq):
                duration, intensity = self.fct_duration_intensity(age=user.age)

                prob_joint = normalize(prob_user * prob_usage)
                u = np.random.uniform()
                start = np.argmin(np.abs(np.cumsum(prob_joint) - u)) + int(pd.to_timedelta('1 day').total_seconds())*day_num
                end = start + duration
                consumption[start:end, j, ind_enduse, pattern_num] = intensity

        return consumption


class NormalShower(Shower):

    def __post_init__(self):
        self.name = "NormalShower"

class FancyShower(Shower):

    def __post_init__(self):
        self.name = "FancyShower"
    

class WashingMachine(EndUse):

    def __post_init__(self):
        self.name = "WashingMachine"

    def fct_frequency(self, numusers=None):

        f_stats = self.statistics['frequency']
        distribution = getattr(np.random, f_stats['distribution'].lower())

        df = pd.Series(f_stats['average'])
        average = df[str(numusers)] * numusers
        return distribution(average)

    def fct_duration_pattern(self, start=None):
        pattern = self.statistics['enduse_pattern']
        # duration = pattern.index[-1] - pattern.index[0]
        return pattern

    def simulate(self, consumption, users=None, ind_enduse=None, pattern_num=1, day_num=0):

        prob_usage = copy.deepcopy(self.statistics['daily_pattern'].values)

        # for j, user in enumerate(users):
        freq = self.fct_frequency(numusers=len(users))

        for j, user in enumerate(users):
            if j == 0:
                prob_user = copy.deepcopy(user.presence)
            else:
                prob_user += user.presence

        prob_user = normalize(prob_user).values
        j = len(users)

        prob_joint = normalize(prob_user * prob_usage)

        pattern = self.fct_duration_pattern()
        duration = len(pattern)

        for i in range(freq):

            u = np.random.random()
            start = np.argmin(np.abs(np.cumsum(prob_joint) - u)) + int(pd.to_timedelta('1 day').total_seconds())*day_num
            end = start + duration

            if end > (24 * 60 * 60):
                end = 24 * 60 * 60
            difference = end - start
            consumption[start:end, j, ind_enduse, pattern_num] = pattern[:difference]

        return consumption

@dataclass
class Wc(EndUse):

    def __post_init__(self):
        self.name = "Wc"
    

    def fct_frequency(self, age=None, gender=None):
        f_stats = self.statistics['frequency']
        distribution = getattr(np.random, f_stats['distribution'].lower())

        average = f_stats['average'][age][gender]

        return distribution(average)

    def fct_duration_intensity(self):

        flush_interuption = self.statistics['subtype'][self.name]['flush_interuption']
        prob_flush_interuption = self.statistics['prob_flush_interuption']

        intensity = self.statistics['intensity']

        average = to_timedelta(self.statistics['subtype'][self.name]['duration'])

        # dist = duration_decorator(getattr(np.random, d_stats['distribution'].lower()))

        # add water savings option
        if flush_interuption:
            v = np.random.random() * 100
            if v < prob_flush_interuption:
                average /= 2.0

        duration = int(average.total_seconds())

        return duration, intensity


    def simulate(self, consumption, users=None, ind_enduse=None, pattern_num=1, day_num=0):

        prob_usage = self.usage_probability().values

        for j, user in enumerate(users):
            freq = self.fct_frequency(age=user.age, gender=user.gender)
            prob_user = user.presence.values

            for i in range(freq):

                duration, intensity = self.fct_duration_intensity()

                prob_joint = normalize(prob_user * prob_usage)
                u = np.random.uniform()
                start = np.argmin(np.abs(np.cumsum(prob_joint) - u)) + int(pd.to_timedelta('1 day').total_seconds())*day_num
                end = start + duration
                consumption[start:end, j, ind_enduse, pattern_num] = intensity

        return consumption

@dataclass
class WcNormal(Wc):

    def __post_init__(self):
        self.name = 'WcNormal'

@dataclass
class WcNormalSave(Wc):

    def __post_init__(self):
        self.name = "WcNormalSave"

@dataclass
class WcNew(Wc):

    def __post_init__(self):
        self.name = "WcNew"

@dataclass
class WcNewSave(Wc):

    def __post_init__(self):
        self.name = "WcNewSave"
