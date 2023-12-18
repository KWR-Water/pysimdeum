import copy
import numpy as np
import scipy.stats as sstats
import pandas as pd
from pysimdeum.core.utils import Base
from dataclasses import dataclass, field
from typing import Any, Callable, Literal
from pysimdeum.core.statistics import Statistics


@dataclass
class Presence:
    """Class representing the presence and the water use activity of users in a house."""

    weekday: bool
    user: Any
    stats: Statistics

    up: pd.Timedelta = field(init=False)
    go: pd.Timedelta = field(init=False)
    home: pd.Timedelta = field(init=False)
    sleep: pd.Timedelta = field(init=False)

    _prob_getting_up: Any = field(init=False, repr=False)
    _prob_leaving_house: Any = field(init=False, repr=False)
    _prob_being_away: Any = field(init=False, repr=False)
    _prob_sleep: Any = field(init=False, repr=False)

    def __post_init__(self) -> None:

        if self.weekday:
            diurnal = copy.deepcopy(self.stats.diurnal_pattern[self.user.age])
        else:
            diurnal = copy.deepcopy(self.stats.diurnal_pattern['weekend'])

        for key, val in diurnal.items():
            dist = val['dist']
            del val['dist']
            # dist = getattr(pm, dist)
            dist = getattr(sstats, dist)
            newval = dict()
            translate = {'mu': 'loc',
                         'sd': 'scale'}

            for x, y in val.items():
                newval[translate[x]] = round(pd.Timedelta(y).total_seconds() / 60)

            # setattr(self, '_prob_' + key, dist.dist(**newval))
            setattr(self, '_prob_' + key, dist(**newval))

        self.up = self.sample_single_property('_prob_getting_up')

        self.sleep = self.up - self.sample_single_property('_prob_sleep') + pd.Timedelta(days=1)

        self.go = self.sample_single_property('_prob_leaving_house')

        if self.go < self.up:
            self.go = self.up + pd.Timedelta(minutes=30)

        self.home = self.go + self.sample_single_property('_prob_being_away')

        if self.home < self.go:
            self.home = self.go  # actually no leave

        if self.sleep < self.home:
            self.home = self.sleep - pd.Timedelta(minutes=30)

    def print(self) -> None:
        """Method to print the main properties of the user's presence"""

        print('up:', self.up)
        print('go:', self.go)
        print('home:', self.home)
        print('sleep:', self.sleep)

    def sample_single_property(self, prop: str) -> pd.Timedelta:
        """Function to draw random time values from the single time properties (e.g., getting up, leave house, ...) of the users"""

        prob_fct = getattr(self, prop)
        x = prob_fct.rvs()
        x = int(np.round(x))
        x = pd.Timedelta(minutes=x)
        return x

    @staticmethod
    def timestamp2str(x: pd.Timedelta) -> str:
        """Transform a Python Pandas Timedelta object to a string in the format HH:MM"""
        
        return str(x.components.hours).zfill(2) + ':' + str(x.components.minutes).zfill(2) # + ':' + str(
        # x.components.seconds).zfill(2)

    def timeindexer(self, l, value, a, b):

        if a < b:
            l[a:b] = value
        else:
            l[a:len(l)] = value
            l[0:b] = value
        return l

    def pdf(self, peak=0.65, normal=0.335, away=0.0, night=0.015):
        index = pd.timedelta_range(start='00:00:00', end='24:00:00', freq='1Min')
        pdf = pd.Series(index=index, dtype='float64')

        up = int((self.up.total_seconds()) / 60) % 1440
        up_p30 = int((up + 30)) % 1440

        go = int(self.go.total_seconds() / 60) % 1440
        go_m30 = int(go - 30) % 1440

        home = int(self.home.total_seconds() / 60) % 1440
        home_p30 = int(home + 30) % 1440

        sleep = int(self.sleep.total_seconds() / 60) % 1440
        sleep_m30 = int(sleep - 30) % 1440

        pdf = self.timeindexer(pdf, 'normal', up_p30, go_m30)
        pdf = self.timeindexer(pdf, 'normal', home_p30, sleep_m30)
        pdf = self.timeindexer(pdf, 'peak', up, up_p30)
        pdf = self.timeindexer(pdf, 'peak', go_m30, go)
        pdf = self.timeindexer(pdf, 'peak', home, home_p30)
        pdf = self.timeindexer(pdf, 'peak', sleep_m30, sleep)
        pdf = self.timeindexer(pdf, 'night', sleep, up)
        pdf = self.timeindexer(pdf, 'away', go, home)

        cnts = pdf.value_counts(normalize=True)
        try:
            cnts = cnts.drop('away')
        except:
            pass
        cnts /= cnts.sum()
        try:
            pdf[pdf == 'peak'] = peak / cnts['peak']
        except:
            pass
        try:
            pdf[pdf == 'normal'] = normal / cnts['normal']
        except:
            pass
        try:
            pdf[pdf == 'night'] = night / cnts['night']
        except:
            pass
        try:
            pdf[pdf == 'away'] = 0.0
        except:
            pass


        pdf = pdf.astype('float').resample('1S').fillna('ffill')[:-1]

        pdf /= np.sum(pdf)  # normalize

        # transform timedeltas to strings for indexing later on
        return pdf

# removed reference to house. house user belongs to house and not also vice versa


@dataclass
class User(Base):

    gender: Literal['male', 'female'] = None
    age: Literal['child', 'teen', 'adult', 'home_ad', 'work_ad', 'senior'] = None  #TODO: Detangle home and work adult from adult
    job: bool = True

    presence: Presence = field(init=False, repr=False)

    def __post_init__(self):

        if self.age == 'adult':
            if self.job:
                self.age = 'work_ad'
            else:
                self.age = 'home_ad'


    def compute_presence(self, weekday=True, statistics=None, peak=0.65, normal=0.335, away=0.0, night=0.015):

        presence = Presence(user=self, weekday=weekday, stats=statistics)
        pdf = presence.pdf(peak=peak, normal=normal, away=away, night=night)
        self.presence = pdf

        return self.presence
