from pysimdeum.tools.plot import plot_water_use_distribution
from pysimdeum.core.house import Property
from pysimdeum.core.statistics import Statistics

def test_plot_water_use_distribution():
    # test if this function still runs

    stats = Statistics()
    prop = Property(statistics=stats)
    house = prop.built_house()
    house.populate_house()
    house.simulate()
    testax = plot_water_use_distribution(house)
    
    assert testax is not None

    house2 = prop.built_house()
    house2.populate_house()
    house2.simulate()
    testax2 = plot_water_use_distribution([house, house2])

    assert testax2 is not None


