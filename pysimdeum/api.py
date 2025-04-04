from pysimdeum.core.statistics import Statistics
from pysimdeum.core.house import Property, HousePattern, House


def built_house(house_type: str = "", country: str = None) -> House:

    country = country or 'NL'
    stats = Statistics(country=country)
    prop = Property(statistics=stats)
    house = prop.built_house(house_type=house_type)
    house.populate_house()
    house.furnish_house()
    for user in house.users:
        user.compute_presence(statistics=stats)
    house.simulate(num_patterns=1, simulate_discharge=False)

    return house
