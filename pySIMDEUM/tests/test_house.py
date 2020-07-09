from pySIMDEUM.house import Property
from pySIMDEUM.statistics import Statistics
from statistics import mean

def test_usersminimal1():
    number_of_users = []
    for x in range(100):
        stats = Statistics()
        prop = Property(statistics=stats)
        house = prop.built_house()
        house.populate_house()
        number_of_users.append(len(house.users))
    
    assert 0 not in number_of_users

def test_average_users():
    number_of_users = []
    for x in range(200):
        stats = Statistics()
        prop = Property(statistics=stats)
        house = prop.built_house()
        house.populate_house()
        number_of_users.append(len(house.users))
    
    assert mean(number_of_users) > 2.1
    assert mean(number_of_users) < 2.5

