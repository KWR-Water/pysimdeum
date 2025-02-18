import os
import toml
from dataclasses import dataclass, field
from pysimdeum.data.NL.end_uses.pattern.pat_ktap import ktap_daily_pattern
from pysimdeum.core.utils import complex_daily_pattern, complex_enduse_pattern, complex_discharge_pattern
from pysimdeum.data import DATA_DIR

@dataclass
class Statistics:
    """Statistics dataclass that contains all the relevant statistical information for pysimdeum."""

    country: str = 'NL'   
    household: dict = field(default_factory=dict)
    diurnal_pattern: dict = field(default_factory=dict)
    end_uses: dict = field(default_factory=dict)
    statisticsdir: str = os.path.join(DATA_DIR, 'NL')  # TODO: Find good solution for this dirty statistics file workaround

    def __post_init__(self, country='NL'):
        self.country = country

        # Load household statistics
        household_file = os.path.join(self.statisticsdir, 'household_statistics.toml')
        self.household = toml.load(open(household_file, 'r'))

        # Load diurnal pattern statistics
        diurnal_pattern_file = os.path.join(self.statisticsdir, 'diurnal_patterns.toml')
        self.diurnal_pattern = toml.load(open(diurnal_pattern_file, 'r'))

        # load end-uses:
        self.end_uses = dict()
        path2end_use = os.path.join(self.statisticsdir, 'end_uses')

        bathtub_file = os.path.join(path2end_use, 'Bathtub.toml')
        brtap_file = os.path.join(path2end_use, 'BathroomTap.toml')
        dishwasher_file = os.path.join(path2end_use, 'Dishwasher.toml')
        kitchen_tap_file = os.path.join(path2end_use, 'KitchenTap.toml')
        outside_tap_file = os.path.join(path2end_use, 'OutsideTap.toml')
        shower_file = os.path.join(path2end_use, 'Shower.toml')
        washing_machine_file = os.path.join(path2end_use, 'WashingMachine.toml')
        wc_file = os.path.join(path2end_use, 'Wc.toml')

        self.end_uses['Wc'] = toml.load(open(wc_file, 'r'))
        self.end_uses['Bathtub'] = toml.load(open(bathtub_file, 'r'))
        self.end_uses['BathroomTap'] = toml.load(open(brtap_file, 'r'))
        self.end_uses['Dishwasher'] = toml.load(open(dishwasher_file, 'r'))
        self.end_uses['KitchenTap'] = toml.load(open(kitchen_tap_file, 'r'))
        self.end_uses['OutsideTap'] = toml.load(open(outside_tap_file, 'r'))
        self.end_uses['Shower'] = toml.load(open(shower_file, 'r'))
        self.end_uses['WashingMachine'] = toml.load(open(washing_machine_file, 'r'))

        # Pattern
        self._initialize_patterns()

    def _initialize_patterns(self):
        self.end_uses['WashingMachine']['daily_pattern'] = complex_daily_pattern(self.end_uses['WashingMachine'])
        self.end_uses['WashingMachine']['enduse_pattern'] = complex_enduse_pattern(self.end_uses['WashingMachine'])
        self.end_uses['WashingMachine']['discharge_pattern'] = complex_discharge_pattern(self.end_uses['WashingMachine'], self.end_uses['WashingMachine']['enduse_pattern'])
        self.end_uses['Dishwasher']['daily_pattern'] = complex_daily_pattern(self.end_uses['Dishwasher'])
        self.end_uses['Dishwasher']['enduse_pattern'] = complex_enduse_pattern(self.end_uses['Dishwasher'])
        self.end_uses['Dishwasher']['discharge_pattern'] = complex_discharge_pattern(self.end_uses['Dishwasher'], self.end_uses['Dishwasher']['enduse_pattern'])
        self.end_uses['KitchenTap']['daily_pattern'] = ktap_daily_pattern()

    def __getstate__(self):
        state = self.__dict__.copy()
        # Remove the unpickleable entries
        for end_use in self.end_uses.values():
            end_use.pop('daily_pattern', None)
            end_use.pop('enduse_pattern', None)
            end_use.pop('discharge_pattern', None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        # Reinitialize the unpickleable entries
        self._initialize_patterns()


def main():

    print(DATA_DIR)

    stats = Statistics()


if __name__ == '__main__':

    main()