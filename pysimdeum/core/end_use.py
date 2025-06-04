import copy
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from pysimdeum.utils.misc import is_weekend_day
from pysimdeum.utils.probability import chooser, duration_decorator, normalize, to_timedelta
from pysimdeum.utils.patterns import handle_spillover_consumption, handle_discharge_spillover, sample_start_time, offset_simultaneous_discharge
from pysimdeum.core.statistics import Statistics
from pysimdeum.utils.patterns import accumulate_sparse_consumption


#TODO: Specific EndUse __post_init__ calls can be replaced by directly using the class name instead of setting the name attributes

@dataclass
class EndUse:
    """Base class for end-uses."""
    
    statistics: Statistics = field(repr=False)  # ... statistic object associated with end-use
    name: str = "EndUse"  # ... name of the end-use
    cold_water_temp = 10
    hot_water_temp = 60
    discharge_events = []

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
    
    def calc_prob_user(self, day_num, user, include_weekend):
        """Calculates the probability of a user being present on a given day.

        Args:
            day_num: The day number (0 for the first day).
            user: user.
            include_weekend: Boolean indicating whether to include weekend days.

        Returns:
            A pandas Series with the probability of each user being present.
        """
        if (is_weekend_day(day_num) and include_weekend):
            prob_user = user.weekend_presence.values
        else:
            prob_user = user.week_presence.values

        return prob_user

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
    
    def temperature(self):
        """Placeholder for specific temperature function defined in specific EndUse"""

        raise NotImplementedError('temperature function is not implemented yet!')

    def fct_duration_intensity_temperature(self):
        """Computing duration and intensity for enduse and retrieve temperature for enduse"""

        duration = self.fct_duration()
        intensity = self.fct_intensity()
        temperature = self.temperature()

        return duration, intensity, temperature

@dataclass
class Bathtub(EndUse):
    """Class for Bathtub end-use."""
    #discharge_events: list = field(default_factory=list)

    def __post_init__(self):
        """Initialisation function of Bathtub end-use class.

        Args:
            name: End-use name as string.
            **kwargs: keyword arguments for super classes.
        """
        self.name = "Bathtub"
        self.wastewater_type = "greywater"
        #self.discharge_events = []

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
    
    def temperature(self):
        """Obtain the temperature of a bath

        Returns:
            temperature of bath water
        
        """
        # independent of subtype
        return self.statistics['temperature']

    def calculate_discharge(self, discharge, end, duration, intensity, temperature_fraction, j, ind_enduse, pattern_num):
        remaining_water = intensity * duration

        # Sample a usage_delay from a uniform distribution
        usage_delay_stats = self.statistics['usage_delay']
        usage_delay = np.random.uniform(usage_delay_stats['low'], usage_delay_stats['high']) * 60

        start = int(end + usage_delay)

        # Sample a value from the discharge_intensity distribution
        discharge_intensity_stats = self.statistics['discharge_intensity']
        dist = getattr(np.random, discharge_intensity_stats['distribution'].lower())
        low = discharge_intensity_stats['low']
        high = discharge_intensity_stats['high']
        discharge_flow_rate = dist(low=low, high=high)

        self.discharge_events.append({
            'enduse': self.name,
            'usage': self.name, # no bath subtypes
            'start': start,
            'end': int(start + (remaining_water / discharge_flow_rate)),
            'discharge_temperature': self.statistics['discharge_temperature'],
        })

        while remaining_water > 0:
            discharge_duration = remaining_water / discharge_flow_rate
            end = int(start + discharge_duration)
            discharge[start:end, j, ind_enduse, pattern_num, 0] = discharge_flow_rate
            remaining_water -= discharge_flow_rate * discharge_duration
            start = end

        return discharge


    def simulate(self, consumption, discharge=None, users=None, ind_enduse=None, pattern_num=1, day_num=0, total_days=1, simulate_discharge=False, spillover=False, include_weekend=False):

        prob_usage = self.usage_probability().values

        previous_events = []

        for j, user in enumerate(users):
            freq = self.fct_frequency(age=user.age)
            prob_user = self.calc_prob_user(day_num, user, include_weekend)

            for i in range(freq):

                duration, intensity, temperature = self.fct_duration_intensity_temperature()
                temperature = self.statistics['temperature']
                prob_joint = normalize(prob_user * prob_usage)

                start, end = sample_start_time(prob_joint, day_num, duration, previous_events)
                previous_events.append((start, end))

                consumption = accumulate_sparse_consumption(consumption, ind_enduse, pattern_num, j, intensity, start, end, 0)
                temperature_fraction = (temperature - self.cold_water_temp)/(self.hot_water_temp - self.cold_water_temp)
                consumption = accumulate_sparse_consumption(consumption, ind_enduse, pattern_num, j, intensity*temperature_fraction, start, end, 1)

                if simulate_discharge:
                    if discharge is None:
                        raise ValueError("Discharge array is None. It must be initialized before being passed to the simulate function.")
                    discharge = self.calculate_discharge(discharge, end, duration, intensity, temperature_fraction, j, ind_enduse, pattern_num)

        return consumption, (discharge if simulate_discharge else None)

    


@dataclass
class BathroomTap(EndUse):
    #discharge_events: list = field(default_factory=list)
    
    def __post_init__(self):
        self.name = "BathroomTap"
        self.wastewater_type = "greywater"
        #self.discharge_events = []

    def fct_frequency(self):

        f_stats = self.statistics['frequency']
        distribution = getattr(np.random, f_stats['distribution'].lower())
        average = f_stats['average']
        return distribution(average)

    def fct_duration_intensity_temperature(self):

        self.subtype = chooser(self.statistics['subtype'], 'penetration')

        d_stats = self.statistics['subtype'][self.subtype]['duration']
        i_stats = self.statistics['subtype'][self.subtype]['intensity']

        dist = duration_decorator(getattr(np.random, d_stats['distribution'].lower()))
        mean = to_timedelta(np.log(to_timedelta(d_stats['average']).total_seconds()) - 0.5)
        duration = dist(mean=mean).total_seconds()

        dist = getattr(np.random, i_stats['distribution'].lower())
        low = i_stats['low']
        high = i_stats['high']

        intensity = dist(low=low, high=high)
        temperature = self.statistics['subtype'][self.subtype]['temperature']
        return duration, intensity, temperature
    
    def calculate_discharge(self, discharge, start, duration, intensity, temperature_fraction, j, ind_enduse, pattern_num, spillover=False):
        remaining_water = intensity * duration
        start = int(start)

        # Sample a value from the discharge_intensity distribution
        discharge_intensity_stats = self.statistics['subtype'][self.subtype]['discharge_intensity']
        dist = getattr(np.random, discharge_intensity_stats['distribution'].lower())
        low = discharge_intensity_stats['low']
        high = discharge_intensity_stats['high']
        discharge_flow_rate = dist(low=low, high=high)

        # limit discharge_flow_rate to the intensity of the tap if there is not enough water to discharge
        if discharge_flow_rate > intensity:
            discharge_flow_rate = intensity

        start = offset_simultaneous_discharge(discharge, start, j, ind_enduse, pattern_num, spillover=spillover)
      
        self.discharge_events.append({
            'enduse': self.name,
            'usage': self.subtype, # subtypes are inherited from chooser(toml)
            'start': start,
            'end': int(start + (remaining_water / discharge_flow_rate)),
            'discharge_temperature': self.statistics['subtype'][self.subtype]['discharge_temperature'],
        })

        while remaining_water > 0:
            discharge_duration = remaining_water / discharge_flow_rate
            end = int(start + discharge_duration)            
            discharge[start:end, j, ind_enduse, pattern_num, 0] = discharge_flow_rate
            remaining_water -= discharge_flow_rate * discharge_duration
            start = end

        return discharge


    def simulate(self, consumption, discharge, users=None, ind_enduse=None, pattern_num=1, day_num=0, total_days=1, simulate_discharge=False, spillover=False, include_weekend=False):
        prob_usage = self.usage_probability().values
        
        previous_events = []

        for j, user in enumerate(users):
            freq = self.fct_frequency()
            prob_user = self.calc_prob_user(day_num, user, include_weekend)

            for i in range(freq):

                duration, intensity, temperature = self.fct_duration_intensity_temperature()

                prob_joint = normalize(prob_user * prob_usage)

                start, end = sample_start_time(prob_joint, day_num, duration, previous_events)
                previous_events.append((start, end))

                consumption = accumulate_sparse_consumption(consumption, ind_enduse, pattern_num, j, intensity, start, end, 0)
                temperature_fraction = (temperature - self.cold_water_temp)/(self.hot_water_temp - self.cold_water_temp)
                consumption = accumulate_sparse_consumption(consumption, ind_enduse, pattern_num, j, intensity*temperature_fraction, start, end, 1)

                if simulate_discharge:
                    if discharge is None:
                        raise ValueError("Discharge array is None. It must be initialized before being passed to the simulate function.")
                    discharge = self.calculate_discharge(discharge, start, duration, intensity, temperature_fraction, j, ind_enduse, pattern_num, spillover=spillover)

        return consumption, (discharge if simulate_discharge else None)

@dataclass
class Dishwasher(EndUse):
    #discharge_events: list = field(default_factory=list)

    def __post_init__(self):
        self.name = "Dishwasher"
        self.wastewater_type = "blackwater"
        #self.discharge_events = []

    def fct_frequency(self, numusers=None):

        f_stats = self.statistics['frequency']
        distribution = getattr(np.random, f_stats['distribution'].lower())

        df = pd.Series(f_stats['average'])
        average = df[str(numusers)]  * numusers
        return distribution(average)

    def fct_duration_pattern(self, start=None):
        pattern = self.statistics['enduse_pattern']
        return pattern
    
    def calculate_discharge(self, discharge, start, j, ind_enduse, pattern_num, day_num, end_of_day, total_days, spillover=False):
        discharge_pattern = self.statistics['discharge_pattern']
        
        cycle_times = []

        for time in discharge_pattern[discharge_pattern > 0].index:
            discharge_time  = start + int(time.total_seconds())
            if discharge_time > end_of_day and spillover:
                discharge = handle_discharge_spillover(discharge, discharge_pattern, time, discharge_time, j, ind_enduse, pattern_num, end_of_day, total_days)
            elif ((day_num + 1) == total_days) and (discharge_time > end_of_day):
                pass
            else:
                discharge[discharge_time, j, ind_enduse, pattern_num, 1] = discharge_pattern[time]

                if not cycle_times or discharge_time - cycle_times[-1][1] > 1:
                    cycle_times.append([discharge_time, discharge_time])
                else:
                    cycle_times[-1][1] = discharge_time

        discharge_temperature = self.statistics['discharge_temperature']

        if isinstance(discharge_temperature, (int, float)):
            discharge_temperatures = [discharge_temperature] * len(cycle_times)
        elif isinstance(discharge_temperature, dict):
            dist = getattr(np.random, discharge_temperature['distribution'].lower())
            low = discharge_temperature['low']
            high = discharge_temperature['high']
            discharge_temperatures = dist(low=low, high=high, size=len(cycle_times)).tolist()
        else:
            raise ValueError("Discharge temperature type not implemented.")
        
        self.discharge_events.append({
            'enduse': self.name,
            'usage': self.name, # no subtypes currently
            'start': [cycle[0] for cycle in cycle_times],
            'end': [cycle[1] for cycle in cycle_times],
            'discharge_temperature': discharge_temperatures,
        })

        return discharge

    def simulate(self, consumption, discharge=None, users=None, ind_enduse=None, pattern_num=1, day_num=0, total_days=1, simulate_discharge=False, spillover=False, include_weekend=False):

        if (is_weekend_day(day_num) and include_weekend):
            prob_usage = copy.deepcopy(self.statistics['daily_pattern_weekend'].values)
        else:
            prob_usage = copy.deepcopy(self.statistics['daily_pattern'].values)

        freq = self.fct_frequency(numusers=len(users))

        for j, user in enumerate(users):
            if j == 0:
                if (is_weekend_day(day_num) and include_weekend):
                    prob_user = copy.deepcopy(user.weekend_presence)
                else:
                    prob_user = copy.deepcopy(user.week_presence)
            else:
                if (is_weekend_day(day_num) and include_weekend):
                    prob_user += user.weekend_presence
                else:
                    prob_user += user.week_presence

        prob_user = normalize(prob_user.values)
        j = len(users)

        prob_joint = normalize(prob_user * prob_usage)

        pattern = self.fct_duration_pattern().values
        duration = len(pattern)

        previous_events = []

        for i in range(freq):
            start, end = sample_start_time(prob_joint, day_num, duration, previous_events)

            # add event times to list of previous events
            previous_events.append((start, end))

            end_of_day = 24 * 60 * 60 * (day_num + 1)
            if end > end_of_day and spillover:
                consumption = handle_spillover_consumption(consumption, pattern, start, end, j, ind_enduse, pattern_num, end_of_day, self.name, total_days)
            elif ((day_num + 1) == total_days) and (end > end_of_day):
                difference = end_of_day - start
                consumption = accumulate_sparse_consumption(consumption, ind_enduse, pattern_num, j, pattern[:difference], start, end_of_day, 0)
            else:
                difference = end - start
                consumption = accumulate_sparse_consumption(consumption, ind_enduse, pattern_num, j, pattern[:difference], start, end, 0)

            if simulate_discharge:
                if discharge is None:
                    raise ValueError("Discharge array is None. It must be initialized before being passed to the simulate function.")
                discharge = self.calculate_discharge(discharge, start, j, ind_enduse, pattern_num, day_num, end_of_day, total_days, spillover=spillover)

        return consumption, (discharge if simulate_discharge else None)

@dataclass
class KitchenTap(EndUse):
    #discharge_events: list = field(default_factory=list)

    def __post_init__(self):
        self.name = "KitchenTap"
        self.wastewater_type = "blackwater"
        #self.discharge_events = []

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

    def fct_duration_intensity_temperature(self):

        self.subtype = chooser(self.statistics['subtype'], 'penetration')

        d_stats = self.statistics['subtype'][self.subtype]['duration']
        i_stats = self.statistics['subtype'][self.subtype]['intensity']

        dist = getattr(np.random, d_stats['distribution'].lower())
        mean = np.log(pd.Timedelta(d_stats['average']).total_seconds()) - 0.5

        duration = int(pd.Timedelta(seconds=dist(mean=mean)).total_seconds())

        dist = getattr(np.random, i_stats['distribution'].lower())
        low = i_stats['low']
        high = i_stats['high']

        intensity = dist(low=low, high=high)
        temperature = self.statistics['subtype'][self.subtype]['temperature']

        return duration, intensity, temperature
    
    def calculate_discharge(self, discharge, start, duration, intensity, temperature_fraction, j, ind_enduse, pattern_num, usage, spillover=False):
        remaining_water = intensity * duration
        start = int(start)

        # Sample a value from the discharge_intensity distribution
        discharge_intensity_stats = self.statistics['subtype'][self.subtype]['discharge_intensity']
        dist = getattr(np.random, discharge_intensity_stats['distribution'].lower())
        low = discharge_intensity_stats['low']
        high = discharge_intensity_stats['high']
        discharge_flow_rate = 0
        while discharge_flow_rate == 0: #ensure the discharge is not zero
            discharge_flow_rate = dist(low=low, high=high)

        # limit discharge_flow_rate to the intensity of the tap if there is not enough water to discharge
        if discharge_flow_rate > intensity:
            discharge_flow_rate = intensity

        # Check if the tap is turned off before the end of the duration, if so, update the start time
        start = offset_simultaneous_discharge(discharge, start, j, ind_enduse, pattern_num, spillover=spillover)

        self.discharge_events.append({
            'enduse': self.name,
            'usage': usage, # subtypes are from chooser(toml)
            'start': start,
            'end': int(start + (remaining_water / discharge_flow_rate)),
            'discharge_temperature': self.statistics['subtype'][self.subtype]['discharge_temperature'],
        })

        while remaining_water > 0:
            discharge_duration = remaining_water / discharge_flow_rate
            end = int(start + discharge_duration)
            # check if subtype = consumption (drinking), if so the discharge flow rate is set to 0
            if self.subtype == 'consumption':
                discharge[start:end, j, ind_enduse, pattern_num, 1] = 0
            else:
                discharge[start:end, j, ind_enduse, pattern_num, 1] = discharge_flow_rate         
            remaining_water -= discharge_flow_rate * discharge_duration
            start = end

        return discharge

    def simulate(self, consumption, discharge=None, users=None, ind_enduse=None, pattern_num=1, day_num=0, total_days=1, simulate_discharge=False, spillover=False, include_weekend=False):

        if (is_weekend_day(day_num) and include_weekend):
            prob_usage = copy.deepcopy(self.statistics['daily_pattern_weekend'].values)
        else:
            prob_usage = copy.deepcopy(self.statistics['daily_pattern'].values)

        freq = self.fct_frequency(numusers=len(users))

        for j, user in enumerate(users):
            if j == 0:
                if (is_weekend_day(day_num) and include_weekend):
                    prob_user = copy.deepcopy(user.weekend_presence)
                else:
                    prob_user = copy.deepcopy(user.week_presence)
            else:
                if (is_weekend_day(day_num) and include_weekend):
                    prob_user += user.weekend_presence
                else:
                    prob_user += user.week_presence

        prob_user = normalize(prob_user).values

        j = len(users)

        freq = self.fct_frequency(numusers=len(users))

        previous_events = []

        for i in range(freq):

            duration, intensity, temperature = self.fct_duration_intensity_temperature()

            # assign usage type (based on subtype)
            usage = self.subtype
            
            prob_joint = normalize(prob_user * prob_usage)  # ToDo: Check if joint probability can be computed outside of for loop for all functions
            
            start, end = sample_start_time(prob_joint, day_num, duration, previous_events)
            previous_events.append((start, end))

            consumption = accumulate_sparse_consumption(consumption, ind_enduse, pattern_num, j, intensity, start, end, 0)
            temperature_fraction = (temperature - self.cold_water_temp)/(self.hot_water_temp - self.cold_water_temp)
            consumption = accumulate_sparse_consumption(consumption, ind_enduse, pattern_num, j, intensity*temperature_fraction, start, end, 1)

            if simulate_discharge:
                if discharge is None:
                    raise ValueError("Discharge array is None. It must be initialized before being passed to the simulate function.")
                discharge = self.calculate_discharge(discharge, start, duration, intensity, temperature_fraction, j, ind_enduse, pattern_num, usage, spillover=spillover)

        return consumption, (discharge if simulate_discharge else None)

@dataclass
class OutsideTap(EndUse):

    def __post_init__(self):
        self.name = "OutsideTap"

    def fct_frequency(self):

        f_stats = self.statistics['frequency']
        distribution = getattr(np.random, f_stats['distribution'].lower())
        average = f_stats['average']
        return distribution(average)

    def fct_duration_intensity_temperature(self):

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
        temperature = self.statistics['subtype'][subtype]['temperature']

        return duration, intensity, temperature

    def simulate(self, consumption, discharge=None, users=None, ind_enduse=None, pattern_num=1, day_num=0, total_days=1, simulate_discharge=False, spillover=False, include_weekend=False):

        prob_usage = self.usage_probability().values

        freq = 0
        for j, user in enumerate(users):
            if j == 0:
                if (is_weekend_day(day_num) and include_weekend):
                    prob_user = copy.deepcopy(user.weekend_presence)
                else:
                    prob_user = copy.deepcopy(user.week_presence)
            else:
                if (is_weekend_day(day_num) and include_weekend):
                    prob_user += user.week_presence
                else:
                    prob_user += user.weekend_presence
            freq += self.fct_frequency()

        prob_user = normalize(prob_user).values

        j = len(users)

        previous_events = []

        for i in range(freq):

            duration, intensity, temperature = self.fct_duration_intensity_temperature()

            prob_joint = normalize(prob_user * prob_usage)
            
            start, end = sample_start_time(prob_joint, day_num, duration, previous_events)
            previous_events.append((start, end))

            consumption = accumulate_sparse_consumption(consumption, ind_enduse, pattern_num, j, intensity, start, end, 0)
            temperature_fraction = (temperature - self.cold_water_temp)/(self.hot_water_temp - self.cold_water_temp)
            consumption = accumulate_sparse_consumption(consumption, ind_enduse, pattern_num, j, intensity*temperature_fraction, start, end, 1)

        return consumption, (discharge if simulate_discharge else None)

@dataclass
class Shower(EndUse):
    #discharge_events: list = field(default_factory=list)

    def __post_init__(self):
        self.name = "Shower"
        self.wastewater_type = "greywater"
        #self.discharge_events = []

    def fct_frequency(self, age=None):

        f_stats = self.statistics['frequency']
        distribution = getattr(np.random, f_stats['distribution'].lower())
        n = f_stats['n']
        p = f_stats['p'][age]

        return distribution(n, p)

    def fct_duration_intensity_temperature(self, age=None):

        d_stats = self.statistics['duration']
        distribution = getattr(np.random, d_stats['distribution'].lower())
        df = to_timedelta(d_stats['df'][age])

        df = int(df.total_seconds() / 60)
        duration = round(distribution(df))
        duration = int(pd.Timedelta(minutes=duration).total_seconds())

        intensity = self.statistics['subtype'][self.name]['intensity']
        temperature = self.statistics['temperature']

        return duration, intensity, temperature
    
    def calculate_discharge(self, discharge, start, duration, intensity, temperature_fraction, j, ind_enduse, pattern_num, spillover=False):
        remaining_water = intensity * duration

        start = int(start)

        # Sample a value from the discharge_intensity distribution
        discharge_intensity_stats = self.statistics['subtype'][self.name]['discharge_intensity']
        dist = getattr(np.random, discharge_intensity_stats['distribution'].lower())
        low = discharge_intensity_stats['low']
        high = discharge_intensity_stats['high']
        discharge_flow_rate = dist(low=low, high=high)

        # limit discharge_flow_rate to the intensity of the tap if there is not enough water to discharge
        if discharge_flow_rate > intensity:
            discharge_flow_rate = intensity

        start = offset_simultaneous_discharge(discharge, start, j, ind_enduse, pattern_num, spillover=spillover)

        self.discharge_events.append({
            'enduse': "Shower",
            'usage': "Shower", # subtypes are class inheritance names
            'start': start,
            'end': int(start + (remaining_water / discharge_flow_rate)),
            'discharge_temperature': self.statistics['discharge_temperature'],
        })

        while remaining_water > 0:
            discharge_duration = remaining_water / discharge_flow_rate
            end = int(start + discharge_duration)
            discharge[start:end, j, ind_enduse, pattern_num, 0] = discharge_flow_rate
            remaining_water -= discharge_flow_rate * discharge_duration
            start = end

        return discharge

    def simulate(self, consumption, discharge=None, users=None, ind_enduse=None, pattern_num=1, day_num=0, total_days=1, simulate_discharge=False, spillover=False, include_weekend=False):

        prob_usage = self.usage_probability().values

        previous_events = []

        for j, user in enumerate(users):
            freq = self.fct_frequency(age=user.age)
            prob_user = self.calc_prob_user(day_num, user, include_weekend)

            for i in range(freq):
                duration, intensity, temperature = self.fct_duration_intensity_temperature(age=user.age)

                prob_joint = normalize(prob_user * prob_usage)
                start, end = sample_start_time(prob_joint, day_num, duration, previous_events)
                previous_events.append((start, end))

                consumption = accumulate_sparse_consumption(consumption, ind_enduse, pattern_num, j, intensity, start, end, 0)
                temperature_fraction = (temperature - self.cold_water_temp)/(self.hot_water_temp - self.cold_water_temp)
                consumption = accumulate_sparse_consumption(consumption, ind_enduse, pattern_num, j, intensity*temperature_fraction, start, end, 1)

                if simulate_discharge:
                    if discharge is None:
                        raise ValueError("Discharge array is None. It must be initialized before being passed to the simulate function.")
                    discharge = self.calculate_discharge(discharge, start, duration, intensity, temperature_fraction, j, ind_enduse, pattern_num, spillover=spillover)

        return consumption, (discharge if simulate_discharge else None)


class NormalShower(Shower):

    def __post_init__(self):
        self.name = "NormalShower"
        self.wastewater_type = "greywater"

class FancyShower(Shower):

    def __post_init__(self):
        self.name = "FancyShower"
        self.wastewater_type = "greywater"
    

class WashingMachine(EndUse):
    #discharge_events: list = field(default_factory=list)

    def __post_init__(self):
        self.name = "WashingMachine"
        self.wastewater_type = "blackwater"
        #self.discharge_events = []

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
    
    def calculate_discharge(self, discharge, start, j, ind_enduse, pattern_num, day_num, end_of_day, total_days, spillover=False):
        discharge_pattern = self.statistics['discharge_pattern']

        cycle_times = []

        for time in discharge_pattern[discharge_pattern > 0].index:
            discharge_time  = start + int(time.total_seconds())
            if discharge_time > end_of_day and spillover:
                discharge = handle_discharge_spillover(discharge, discharge_pattern, time, discharge_time, j, ind_enduse, pattern_num, end_of_day, total_days)
            elif ((day_num + 1) == total_days) and (discharge_time > end_of_day):
                pass
            else:
                discharge[discharge_time, j, ind_enduse, pattern_num, 1] = discharge_pattern[time]

            if not cycle_times or discharge_time - cycle_times[-1][1] > 1:
                    cycle_times.append([discharge_time, discharge_time])
            else:
                    cycle_times[-1][1] = discharge_time

        discharge_temperature = self.statistics['discharge_temperature']

        if isinstance(discharge_temperature, (int, float)):
            discharge_temperatures = [discharge_temperature] * len(cycle_times)
        elif isinstance(discharge_temperature, dict):
            dist = getattr(np.random, discharge_temperature['distribution'].lower())
            low = discharge_temperature['low']
            high = discharge_temperature['high']
            discharge_temperatures = dist(low=low, high=high, size=len(cycle_times)).tolist()
        else:
            raise ValueError("Discharge temperature type not implemented.")
        
        self.discharge_events.append({
            'enduse': "WashingMachine",
            'usage': "WashingMachine", # no subtypes currently
            'start': [cycle[0] for cycle in cycle_times],
            'end': [cycle[1] for cycle in cycle_times],
            'discharge_temperature': discharge_temperatures,
        })

        return discharge

    def simulate(self, consumption, discharge=None, users=None, ind_enduse=None, pattern_num=1, day_num=0, total_days=1, simulate_discharge=False, spillover=False, include_weekend=False):

        if (is_weekend_day(day_num) and include_weekend):
            prob_usage = copy.deepcopy(self.statistics['daily_pattern_weekend'].values)
        else:
            prob_usage = copy.deepcopy(self.statistics['daily_pattern'].values)

        # for j, user in enumerate(users):
        freq = self.fct_frequency(numusers=len(users))

        for j, user in enumerate(users):
            if j == 0:
                if (is_weekend_day(day_num) and include_weekend):
                    prob_user = copy.deepcopy(user.weekend_presence)
                else:
                    prob_user = copy.deepcopy(user.week_presence)
            else:
                if (is_weekend_day(day_num) and include_weekend):
                    prob_user += user.week_presence
                else:
                    prob_user += user.weekend_presence

        prob_user = normalize(prob_user).values
        j = len(users)

        prob_joint = normalize(prob_user * prob_usage)

        pattern = self.fct_duration_pattern()
        duration = len(pattern)

        previous_events = []

        for i in range(freq):
            start, end = sample_start_time(prob_joint, day_num, duration, previous_events)
            
            # add event times to list of previous events
            previous_events.append((start, end))

            end_of_day = 24 * 60 * 60 * (day_num + 1)
            if end > end_of_day and spillover:
                consumption = handle_spillover_consumption(consumption, pattern, start, end, j, ind_enduse, pattern_num, end_of_day, "WashingMachine", total_days)
            elif ((day_num + 1) == total_days) and (end > end_of_day):
                difference = end_of_day - start
                consumption = accumulate_sparse_consumption(consumption, ind_enduse, pattern_num, j, pattern[:difference], start, end_of_day, 0)
            else:
                difference = end - start
                consumption = accumulate_sparse_consumption(consumption, ind_enduse, pattern_num, j, pattern[:difference], start, end, 0)

            if simulate_discharge:
                if discharge is None:
                    raise ValueError("Discharge array is None. It must be initialized before being passed to the simulate function.")
                discharge = self.calculate_discharge(discharge, start, j, ind_enduse, pattern_num, day_num, end_of_day, total_days, spillover=spillover)

        return consumption, (discharge if simulate_discharge else None)

@dataclass
class Wc(EndUse):
    #discharge_events: list = field(default_factory=list)

    def __post_init__(self):
        self.name = "Wc"
        self.wastewater_type = "blackwater"
        self.discharge_events = []
    

    def fct_frequency(self, age=None, gender=None):
        f_stats = self.statistics['frequency']
        distribution = getattr(np.random, f_stats['distribution'].lower())

        average = f_stats['average'][age][gender]

        return distribution(average)

    def fct_duration_intensity_temperature(self):

        flush_interuption = self.statistics['subtype'][self.name]['flush_interuption']
        prob_flush_interuption = self.statistics['prob_flush_interuption']

        intensity = self.statistics['intensity']
        temperature = self.statistics['temperature']
        average = to_timedelta(self.statistics['subtype'][self.name]['duration'])

        # dist = duration_decorator(getattr(np.random, d_stats['distribution'].lower()))

        # add water savings option
        if flush_interuption:
            v = np.random.random() * 100
            if v < prob_flush_interuption:
                average /= 2.0

        duration = int(average.total_seconds())

        return duration, intensity, temperature


    def calculate_discharge(self, discharge, start, duration, intensity, temperature_fraction, j, ind_enduse, pattern_num, usage):
        incoming_water = intensity * duration
        end = int(start)

        # Sample a value from the discharge_intensity distribution
        discharge_flow_rate = self.statistics['discharge_intensity']

        self.discharge_events.append({
            'enduse': "Wc",
            'usage': usage,
            'start': int(end - (incoming_water / discharge_flow_rate)),
            'end': end,
            'discharge_temperature': self.statistics['discharge_temperature'],
        })

        while incoming_water > 0:
            discharge_duration = incoming_water / discharge_flow_rate
            start = int(end - discharge_duration)
            discharge[start:end, j, ind_enduse, pattern_num, 1] = discharge_flow_rate
            incoming_water -= discharge_flow_rate * discharge_duration
            end = start

        return discharge


    def simulate(self, consumption, discharge=None, users=None, ind_enduse=None, pattern_num=1, day_num=0, total_days=1, simulate_discharge=False, spillover=False, include_weekend=False):

        prob_usage = self.usage_probability().values

        previous_events = []

        for j, user in enumerate(users):
            freq = self.fct_frequency(age=user.age, gender=user.gender)
            prob_user = self.calc_prob_user(day_num, user, include_weekend)

            for i in range(freq):

                duration, intensity, temperature = self.fct_duration_intensity_temperature()

                # assign usage type (urine or faeces)
                usage = "urine" if np.random.random() * 100 < self.statistics['prob_urine'] else "faeces"
                #print(prob_user)
                prob_joint = normalize(prob_user * prob_usage)
                start, end = sample_start_time(prob_joint, day_num, duration, previous_events)
                previous_events.append((start, end))

                consumption = accumulate_sparse_consumption(consumption, ind_enduse, pattern_num, j, intensity, start, end, 0)
                temperature_fraction = (temperature - self.cold_water_temp)/(self.hot_water_temp - self.cold_water_temp)
                consumption = accumulate_sparse_consumption(consumption, ind_enduse, pattern_num, j, intensity*temperature_fraction, start, end, 1)

                if simulate_discharge:
                    if discharge is None:
                        raise ValueError("Discharge array is None. It must be initialized before being passed to the simulate function.")
                    discharge = self.calculate_discharge(discharge, start, duration, intensity, temperature_fraction, j, ind_enduse, pattern_num, usage)

        return consumption, (discharge if simulate_discharge else None)

@dataclass
class WcNormal(Wc):

    def __post_init__(self):
        self.name = 'WcNormal'
        self.wastewater_type = "blackwater"

@dataclass
class WcNormalSave(Wc):

    def __post_init__(self):
        self.name = "WcNormalSave"
        self.wastewater_type = "blackwater"

@dataclass
class WcNew(Wc):

    def __post_init__(self):
        self.name = "WcNew"
        self.wastewater_type = "blackwater"

@dataclass
class WcNewSave(Wc):

    def __post_init__(self):
        self.name = "WcNewSave"
        self.wastewater_type = "blackwater"
