from traits.api import HasStrictTraits, Either, Instance, Str, Any
import copy
import pandas as pd
import numpy as np
from utils import chooser, duration_decorator, normalize, to_timedelta


class EndUse(HasStrictTraits):
    """Base class for end-uses.

    """

    name = Str  # ... name of the end-use
    statistics = Any  # ... statistic object associated with end-use

    def __init__(self, name: str = 'EndUse', statistics=None):
        """Initialisation funciton of end-use class.

        Args:
            name: name of the specific end-use as string
            statistics: statistics object associated with end-use
        """
        super(EndUse, self).__init__()
        self.name = name
        self.statistics = statistics

    def init_consumption(self, users=None, time_resolution='1s'):
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
    def usage_probability(time_resolution='1s'):
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


class Bathtub(EndUse):
    """Class for Bathtub end-use."""


    def __init__(self, name='Bathtub', **kwargs):
        """Initialisation function of Bathtub end-use class.

        Args:
            name: End-use name as string.
            **kwargs: keyword arguments for super classes.
        """
        super(Bathtub, self).__init__(**kwargs)
        self.name = name

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

    def simulate(self, consumption, users=None, ind_enduse=None):

        prob_usage = self.usage_probability().values

        for j, user in enumerate(users):
            freq = self.fct_frequency(age=user.age)
            prob_user = user.presence.values

            for i in range(freq):

                duration, intensity = self.fct_duration_intensity()
                prob_joint = normalize(prob_user * prob_usage)

                u = np.random.uniform()
                start = np.argmin(np.abs(np.cumsum(prob_joint) - u))
                end = start + duration

                consumption[start:end, j, ind_enduse] = intensity

                # block uses of current user for other enduses (this is possible because Python takes the object
                # itself and not a copy of the presence attribute) So no user can use two endtypes at the same time
                prob_user[start:end] = 0
                prob_user = normalize(prob_user)

                # block for other users (only possible because of fixed duration time)
                prob_usage[start-duration:end] = 0
                prob_usage = normalize(prob_usage)

        return consumption


class BathroomTap(EndUse):
    
    def __init__(self, name='BathroomTap', **kwargs):
        super(BathroomTap, self).__init__(**kwargs)
        self.name = name

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

    def simulate(self, consumption, users=None, ind_enduse=None):

        prob_usage = self.usage_probability().values

        for j, user in enumerate(users):
            freq = self.fct_frequency()
            prob_user = user.presence.values

            for i in range(freq):
                check = False

                duration, intensity = self.fct_duration_intensity()

                prob_joint = normalize(prob_user * prob_usage)

                # get rid of overlaps
                for tries in range(10):
                    u = np.random.uniform()
                    start = np.argmin(np.abs(np.cumsum(prob_joint) - u))
                    end = int(start + duration)
                    if np.sum(consumption[start:end, j, ind_enduse]) == 0:
                        check = True
                        break

                if check:
                    prob_user[start:end] = 0
                    prob_user = normalize(prob_user)

                    prob_usage[start:end] = 0
                    prob_usage = normalize(prob_usage)

                    consumption[start:end, j, ind_enduse] = intensity

        return consumption


class Dishwasher(EndUse):

    def __init__(self, name='Dishwasher', **kwargs):
        super(Dishwasher, self).__init__(**kwargs)
        self.name = name

    def fct_frequency(self, numusers=None):

        f_stats = self.statistics['frequency']
        distribution = getattr(np.random, f_stats['distribution'].lower())

        df = pd.Series(f_stats['average'])
        average = df[str(numusers)]  * numusers
        return distribution(average)

    def fct_duration_pattern(self, start=None):
        pattern = self.statistics['enduse_pattern']
        # duration = pattern.index[-1] - pattern.index[0]
        return pattern

    def simulate(self, consumption, users=None, ind_enduse=None):

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
            start = np.argmin(np.abs(np.cumsum(prob_joint) - u))
            end = start + duration

            if end > (24 * 60 * 60):
                end = 24 * 60 * 60
            difference = end - start
            consumption[start:end, j, ind_enduse] = pattern[:difference]

            prob_user[start:end] = 0
            prob_user = normalize(prob_user)

            prob_usage[start - duration:end] = 0
            prob_usage = normalize(prob_usage)

        return consumption


class KitchenTap(EndUse):

    def __init__(self, name='KitchenTap', **kwargs):
        super(KitchenTap, self).__init__(**kwargs)
        self.name = name

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

    def simulate(self, consumption, users=None, ind_enduse=None):

        prob_usage = copy.deepcopy(self.statistics['daily_pattern'].values)

        for j, user in enumerate(users):
            if j == 0:
                prob_user = copy.deepcopy(user.presence)
            else:
                prob_user += user.presence

        prob_user = normalize(prob_user).values

        j = len(users)

        freq = self.fct_frequency(numusers=len(users))

        for i in range(freq):

            duration, intensity = self.fct_duration_intensity()

            prob_joint = normalize(prob_user * prob_usage)

            for tries in range(10):
                u = np.random.uniform()
                start = np.argmin(np.abs(np.cumsum(prob_joint) - u))
                end = start + duration

                if np.sum(consumption[start:end, j, ind_enduse]) == 0:
                    check = True
                    break

            if check:
                prob_user[start:end] = 0
                prob_user = normalize(prob_user)

                prob_usage[start:end] = 0
                prob_usage = normalize(prob_usage)

                consumption[start:end, j, ind_enduse] = intensity

        return consumption


class OutsideTap(EndUse):

    def __init__(self, name='OutsideTap', **kwargs):
        super(OutsideTap, self).__init__(**kwargs)
        self.name = name

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

    def simulate(self, consumption, users=None, ind_enduse=None):

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

            for tries in range(10):
                u = np.random.uniform()
                start = np.argmin(np.abs(np.cumsum(prob_joint) - u))
                end = start + duration

                if np.sum(consumption[start:end, j, ind_enduse]) == 0:
                    check = True
                    break
                else:
                    print('consumption overlap')

            if check:
                prob_user[start:end] = 0
                prob_user = normalize(prob_user)

                prob_usage[start:end] = 0
                prob_usage = normalize(prob_usage)

                consumption[start:end, j, ind_enduse] = intensity

        return consumption


class Shower(EndUse):

    def __init__(self, name='Shower',**kwargs):
        super(Shower, self).__init__(**kwargs)
        self.name = name

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

    def simulate(self, consumption, users=None, ind_enduse=None):

        prob_usage = self.usage_probability().values

        for j, user in enumerate(users):
            freq = self.fct_frequency(age=user.age)
            prob_user = user.presence.values

            for i in range(freq):
                check = False

                duration, intensity = self.fct_duration_intensity(age=user.age)

                prob_joint = normalize(prob_user * prob_usage)

                # get rid of overlaps
                for tries in range(10):
                    u = np.random.uniform()
                    start = np.argmin(np.abs(np.cumsum(prob_joint) - u))
                    end = start + duration

                    if np.sum(consumption[start:end, j, ind_enduse]) == 0:
                        check = True
                        break
                    else:
                        print('consumption overlap')
                if check:
                    prob_user[start:end] = 0
                    prob_user = normalize(prob_user)

                    prob_usage[start:end] = 0
                    prob_usage = normalize(prob_usage)

                    consumption[start:end, j, ind_enduse] = intensity

        return consumption


class NormalShower(Shower):

    def __init__(self, name='NormalShower', **kwargs):
        super(NormalShower, self).__init__(**kwargs)
        self.name = name


class FancyShower(Shower):

    def __init__(self, name='FancyShower', **kwargs):
        super(FancyShower, self).__init__(**kwargs)
        self.name = name


class WashingMachine(EndUse):

    def __init__(self, name='WashingMachine', **kwargs):
        super(WashingMachine, self).__init__(**kwargs)
        self.name = name

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

    def simulate(self, consumption, users=None, ind_enduse=None):

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
            start = np.argmin(np.abs(np.cumsum(prob_joint) - u))
            end = start + duration

            if end > (24 * 60 * 60):
                end = 24 * 60 * 60
            difference = end - start
            consumption[start:end, j, ind_enduse] = pattern[:difference]

            prob_user[start:end] = 0
            prob_user = normalize(prob_user)

            prob_usage[start - duration:end] = 0
            prob_usage = normalize(prob_usage)

        return consumption


class Wc(EndUse):

    def __init__(self, name='Wc', **kwargs):
        super(Wc, self).__init__(**kwargs)
        self.name = name

    def fct_frequency(self, age=None, gender=None):
        f_stats = self.statistics['frequency']
        distribution = getattr(np.random, f_stats['distribution'].lower())

        average = f_stats['average'][age][gender]

        return distribution(average)

    def fct_duration_intensity(self):

        flush_interuption = self.statistics['subtype'][self.name]['flush_interuption']
        prob_flush_interuption = self.statistics['prob_flush_interuption']

        intensity = self.statistics['intensity']

        average = self.statistics['subtype'][self.name]['duration']

        # dist = duration_decorator(getattr(np.random, d_stats['distribution'].lower()))

        average = to_timedelta(np.log(to_timedelta(average).total_seconds()) - 0.5)

        # add water savings option
        if flush_interuption:
            v = np.random.random() * 100
            if v < prob_flush_interuption:
                average /= 2.0

        duration = int(average.total_seconds())

        return duration, intensity


    def simulate(self, consumption, users=None, ind_enduse=None):

        prob_usage = self.usage_probability().values

        for j, user in enumerate(users):
            freq = self.fct_frequency(age=user.age, gender=user.gender)
            prob_user = user.presence.values

            for i in range(freq):
                check = False

                duration, intensity = self.fct_duration_intensity()

                prob_joint = normalize(prob_user * prob_usage)

                # get rid of overlaps
                for tries in range(10):
                    u = np.random.uniform()
                    start = np.argmin(np.abs(np.cumsum(prob_joint) - u))
                    end = start + duration

                    if np.sum(consumption[start:end, j, ind_enduse]) == 0:
                        check = True
                        break
                    else:
                        print('consumption overlap')
                # print(start, end)
                # print(consumption.time)
                if check:
                    prob_user[start:end] = 0
                    prob_user = normalize(prob_user)

                    prob_usage[start:end] = 0
                    prob_usage = normalize(prob_usage)

                    consumption[start:end, j, ind_enduse] = intensity

        return consumption

class WcNormal(Wc):

    def __init__(self, name='WcNormal', **kwargs):
        super(WcNormal, self).__init__(**kwargs)
        self.name = name


class WcNormalSave(Wc):

    def __init__(self, name='WcNormalSave', **kwargs):
        super(WcNormalSave, self).__init__(**kwargs)
        self.name = name


class WcNew(Wc):

    def __init__(self, name='WcNew', **kwargs):
        super(WcNew, self).__init__(**kwargs)
        self.name = name


class WcNewSave(Wc):

    def __init__(self, name='WcNewSave', **kwargs):
        super(WcNewSave, self).__init__(**kwargs)
        self.name = name
