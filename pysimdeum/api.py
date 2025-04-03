from pysimdeum.core.statistics import Statistics
from pysimdeum.core.house import Property, HousePattern, House


def built_house(house_type: str = "", duration: str = '1 day', country: str = None, simulate_discharge=False, spillover=False) -> House:

    country = country or 'NL'
    stats = Statistics(country=country)
    prop = Property(statistics=stats)
    house = prop.built_house(house_type=house_type)
    house.populate_house()
    house.furnish_house()
    for user in house.users:
        user.compute_presence(statistics=stats)
    house.simulate(duration=duration, num_patterns=1, simulate_discharge=simulate_discharge, spillover=spillover)

    return house


def build_multi_hh(household_data: dict, duration: str = '1 day', country: str = None, simulate_discharge=False, spillover=False) -> dict:

    houses = {}

    for household_id, house_type in household_data.items():
        # generate and simulate the hh
        house_instance = built_house(house_type=house_type, duration=duration, country=country, simulate_discharge=simulate_discharge, spillover=spillover)
        # store the resulting House instance in the houses dictionary
        houses[household_id] = house_instance

    return houses