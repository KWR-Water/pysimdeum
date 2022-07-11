from pySIMDEUM.core.statistics import Statistics
from pySIMDEUM.core.house import Property, HousePattern


def built_house(x):
    stats = Statistics()
    prop = Property(statistics=stats)
    house = prop.built_house()
    house.populate_house()
    house.furnish_house()
    for user in house.users:
        user.compute_presence(statistics=stats)
    house.simulate(num_patterns=100)

    return house