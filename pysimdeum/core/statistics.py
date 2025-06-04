import os
import toml
from dataclasses import dataclass, field
from pysimdeum.utils.patterns import complex_daily_pattern, complex_enduse_pattern, complex_discharge_pattern
from pysimdeum.data import DATA_DIR
import pickle

@dataclass
class Statistics:
    """Statistics dataclass that contains all the relevant statistical information for pysimdeum."""

    country: str = 'NL'   
    household: dict = field(default_factory=dict)
    diurnal_pattern: dict = field(default_factory=dict)
    end_uses: dict = field(default_factory=dict)
    statisticsdir: str = ""  # TODO: Find good solution for this dirty statistics file workaround

    def __post_init__(self):
        
        # Check if pointing to a custom statistics directory or a country in the repository
        if os.path.isdir(self.country):
            self.statisticsdir = self.country
            self.country = None #No country is set as its a custom directory
        else:
            self.statisticsdir = os.path.join(DATA_DIR, self.country)

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
        self.end_uses['Dishwasher'] = self._convert_to_dict(toml.load(open(dishwasher_file, 'r')))
        self.end_uses['KitchenTap'] = toml.load(open(kitchen_tap_file, 'r'))
        self.end_uses['OutsideTap'] = toml.load(open(outside_tap_file, 'r'))
        self.end_uses['Shower'] = toml.load(open(shower_file, 'r'))
        self.end_uses['WashingMachine'] = self._convert_to_dict(toml.load(open(washing_machine_file, 'r')))

        # Pattern
        self._initialize_patterns()

    def _initialize_patterns(self):
        self.end_uses['WashingMachine']['daily_pattern'] = complex_daily_pattern(self.end_uses['WashingMachine'])
        self.end_uses['WashingMachine']['daily_pattern_weekend'] = complex_daily_pattern(self.end_uses['WashingMachine'], weekend=True)
        self.end_uses['WashingMachine']['enduse_pattern'] = complex_enduse_pattern(self.end_uses['WashingMachine'])
        self.end_uses['WashingMachine']['discharge_pattern'] = complex_discharge_pattern(self.end_uses['WashingMachine'], self.end_uses['WashingMachine']['enduse_pattern'])
        self.end_uses['Dishwasher']['daily_pattern'] = complex_daily_pattern(self.end_uses['Dishwasher'])
        self.end_uses['Dishwasher']['daily_pattern_weekend'] = complex_daily_pattern(self.end_uses['Dishwasher'], weekend=True)
        self.end_uses['Dishwasher']['enduse_pattern'] = complex_enduse_pattern(self.end_uses['Dishwasher'])
        self.end_uses['Dishwasher']['discharge_pattern'] = complex_discharge_pattern(self.end_uses['Dishwasher'], self.end_uses['Dishwasher']['enduse_pattern'])
        self.end_uses['KitchenTap']['daily_pattern'] = complex_daily_pattern(self.end_uses['KitchenTap'], freq='15Min')
        self.end_uses['KitchenTap']['daily_pattern_weekend'] = complex_daily_pattern(self.end_uses['KitchenTap'], freq='15Min', weekend=True)

    def _convert_to_dict(self, data):
        if isinstance(data, dict):
            return {k: self._convert_to_dict(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._convert_to_dict(v) for v in data]
        else:
            return data
    
def main():
    print(DATA_DIR)
    stats = Statistics()

if __name__ == '__main__':
    main()