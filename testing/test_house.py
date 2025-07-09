from pysimdeum.core.house import Property
from pysimdeum.core.statistics import Statistics
from statistics import mean

def test_usersminimal1():
    number_of_users = []
    for x in range(100):
        stats = Statistics()
        prop = Property(statistics=stats)
        house = prop.built_house()
        house.populate_house()
        house.furnish_house()
        for user in house.users:
            user.compute_presence(statistics=stats)
        number_of_users.append(len(house.users))
    
    assert 0 not in number_of_users

def test_average_users():
    number_of_users = []
    for x in range(200):
        stats = Statistics()
        prop = Property(statistics=stats)
        house = prop.built_house()
        house.populate_house()
        house.furnish_house()
        for user in house.users:
            user.compute_presence(statistics=stats)
        number_of_users.append(len(house.users))
    
    assert mean(number_of_users) > 2.1
    assert mean(number_of_users) < 2.5

def test_save_and_load_house():
    stats = Statistics()
    prop = Property(statistics=stats)
    house = prop.built_house()
    house.populate_house()
    house.furnish_house()
    for user in house.users:
        user.compute_presence(statistics=stats)
    house.save_house('unittest')

    prop2 = Property(statistics=stats)
    house2 = prop2.built_house(housefile='unittest.house')

    assert house.id == house2.id


