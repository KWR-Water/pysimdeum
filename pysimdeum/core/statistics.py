import os
import importlib
import toml
from dataclasses import dataclass, field

try:
    from pysimdeum.data import DATA_DIR
except:
    from ..data import DATA_DIR

# try:
#     from pysimdeum.data.NL.end_uses.pattern.pat_dishwasher import dishwasher_daily_pattern, \
#         dishwasher_enduse_pattern
#     from pysimdeum.data.NL.end_uses.pattern.pat_ktap import ktap_daily_pattern
#     from pysimdeum.data.NL.end_uses.pattern.pat_washing_machine import washingmachine_daily_pattern, \
#         washingmachine_enduse_pattern
# except:
#     from ..data.NL.end_uses.pattern.pat_dishwasher import dishwasher_daily_pattern, dishwasher_enduse_pattern
#     from ..data.NL.end_uses.pattern.pat_ktap import ktap_daily_pattern
#     from ..data.NL.end_uses.pattern.pat_washing_machine import washingmachine_daily_pattern, washingmachine_enduse_pattern

# from ..data.NL.Amsterdam.end_uses.pattern.pat_dishwasher import dishwasher_daily_pattern, dishwasher_enduse_pattern
# from ..data.NL.Amsterdam.end_uses.pattern.pat_ktap import ktap_daily_pattern
# from ..data.NL.Amsterdam.end_uses.pattern.pat_washing_machine import washingmachine_daily_pattern, washingmachine_enduse_pattern


@dataclass
class Statistics:
    """Statistics dataclass that contains all the relevant statistical information for pysimdeum."""

    country:       str = 'NL'
    city:          str = 'All'

    statisticsdir: str = os.path.join(DATA_DIR, 'NL', 'All')

    household:       dict = field(default_factory=dict)
    diurnal_pattern: dict = field(default_factory=dict)
    end_uses:        dict = field(default_factory=dict)

    def __post_init__(self):
        self.statisticsdir = os.path.join(DATA_DIR, self.country, self.city)

        module_name_pat_dishwasher      = '.pat_dishwasher'
        module_name_pat_ktap            = '.pat_ktap'
        module_name_pat_washing_machine = '.pat_washing_machine'

        try:
            if len(self.city) > 0:
                package_name = f'pysimdeum.data.{self.country}.{self.city}.end_uses.pattern'
            else:
                package_name = f'pysimdeum.data.{self.country}.end_uses.pattern'

            obj_dishwasher      = importlib.import_module(f'{module_name_pat_dishwasher}',      package=package_name)
            obj_ktap            = importlib.import_module(f'{module_name_pat_ktap}',            package=package_name)
            obj_washing_machine = importlib.import_module(f'{module_name_pat_washing_machine}', package=package_name)
        except ModuleNotFoundError as err:
            if len(self.city) > 0:
                package_name = f'pysimdeum.pysimdeum.data.{self.country}.{self.city}.end_uses.pattern'
            else:
                package_name = f'pysimdeum.pysimdeum.data.{self.country}.end_uses.pattern'

            obj_dishwasher      = importlib.import_module(f'{module_name_pat_dishwasher}',      package=package_name)
            obj_ktap            = importlib.import_module(f'{module_name_pat_ktap}',            package=package_name)
            obj_washing_machine = importlib.import_module(f'{module_name_pat_washing_machine}', package=package_name)

        # Load household statistics
        household_file = os.path.join(self.statisticsdir, 'household_statistics.toml')
        self.household = toml.load(open(household_file, 'r'))

        # Load diurnal pattern statistics
        diurnal_pattern_file = os.path.join(self.statisticsdir, 'diurnal_patterns.toml')
        self.diurnal_pattern = toml.load(open(diurnal_pattern_file, 'r'))

        # load end-uses:
        self.end_uses = dict()
        path2end_use  = os.path.join(self.statisticsdir, 'end_uses')

        bathtub_file         = os.path.join(path2end_use, 'Bathtub.toml')
        brtap_file           = os.path.join(path2end_use, 'BathroomTap.toml')
        dishwasher_file      = os.path.join(path2end_use, 'Dishwasher.toml')
        kitchen_tap_file     = os.path.join(path2end_use, 'KitchenTap.toml')
        outside_tap_file     = os.path.join(path2end_use, 'OutsideTap.toml')
        shower_file          = os.path.join(path2end_use, 'Shower.toml')
        washing_machine_file = os.path.join(path2end_use, 'WashingMachine.toml')
        wc_file              = os.path.join(path2end_use, 'Wc.toml')

        self.end_uses['Wc']             = toml.load(open(wc_file, 'r'))
        self.end_uses['Bathtub']        = toml.load(open(bathtub_file, 'r'))
        self.end_uses['BathroomTap']    = toml.load(open(brtap_file, 'r'))
        self.end_uses['Dishwasher']     = toml.load(open(dishwasher_file, 'r'))
        self.end_uses['KitchenTap']     = toml.load(open(kitchen_tap_file, 'r'))
        self.end_uses['OutsideTap']     = toml.load(open(outside_tap_file, 'r'))
        self.end_uses['Shower']         = toml.load(open(shower_file, 'r'))
        self.end_uses['WashingMachine'] = toml.load(open(washing_machine_file, 'r'))

        # Pattern
        self.end_uses['Dishwasher']['daily_pattern']      = obj_dishwasher.dishwasher_daily_pattern()
        self.end_uses['Dishwasher']['enduse_pattern']     = obj_dishwasher.dishwasher_enduse_pattern()

        self.end_uses['KitchenTap']['daily_pattern']      = obj_ktap.ktap_daily_pattern()

        self.end_uses['WashingMachine']['daily_pattern']  = obj_washing_machine.washingmachine_daily_pattern()
        self.end_uses['WashingMachine']['enduse_pattern'] = obj_washing_machine.washingmachine_enduse_pattern()


def main():
    print(DATA_DIR)
    stats = Statistics()


if __name__ == '__main__':
    main()
