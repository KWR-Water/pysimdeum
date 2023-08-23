try:
    from pysimdeum.core.statistics import Statistics
    from pysimdeum.core.house import Property, HousePattern, House
except:
    from .core.statistics import Statistics
    from .core.house import Property, HousePattern, House


def built_house(country:    str = "",
                city:       str = "",
                house_type: str = "") -> House:

    stats = Statistics(country=country, city=city)
    prop = Property(statistics=stats)
    house = prop.built_house(house_type=house_type)
    house.populate_house()
    house.furnish_house()
    for user in house.users:
        user.compute_presence(statistics=stats)
    house.simulate(num_patterns=100)

    return house
