from pySIMDEUM.pySIMDEUM.statistics import Statistics
from pySIMDEUM.pySIMDEUM.house import Property
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('darkgrid')

# Simulation for single houses:

# Build house, populate and furnish it, then compute user presence:
stats = Statistics()
prop = Property(statistics=stats)
house = prop.built_house()
house.populate_house()
house.furnish_house()
for user in house.users:
    user.compute_presence(statistics=stats)
print(house)

# Simulate one day of water use in the house, the result is an xarray dataarray with dimensions time, user and end-user
# resample it to 15 minutes and plot it for each user and end-use device:
cons = house.simulate()

data = cons.resample(time='1Min').mean(dim='time')  # ... resample time from 1 second to 1 minute
used_devices = data.enduse[data.sum(dim='user').sum('time') != 0]  # ... find only used end-use devices
data = data.sel(enduse=used_devices)
users = list(data.user.values)  # ... extract list with all users
for user in users:  # ... iterate over users
    fig, ax = plt.subplots()  # ... generate figure
    df = data.sel(user=user).to_dataframe(user)[user].unstack()  # ... select user and cast to pandas dataframe
    df.plot(ax=ax, legend=False)  # ... plot dataframe

    # title, legend settings and labels
    ax.set_title(user)
    patches, labels = ax.get_legend_handles_labels()
    ax.legend(patches, labels, loc='upper center',
              ncol=3, fancybox=False, frameon=False, fontsize=8, bbox_to_anchor=(0.5, -.05))
    plt.xlabel('')
    plt.show()  # ... display figure


# Simulate same house for 1 week (difference between weekday and weekend is not yet automatically implemented, but can
# be done quite easily)
start = pd.datetime.now().date()  # ... set simulation starttime to today
end = start + pd.to_timedelta('1 W')  # ... endtime is 1 week in the future
dates = pd.date_range(start, end, freq='1d', closed='left')  # ... generate dates to simulate

result = xr.concat(list(map(house.simulate, dates)), 'time')  # ... simulate with map function (point for parallel computing with m,ultiprocessing!)
cons = result.sum('user').sum('enduse').to_dataframe('total consumption')  # ... sum over users and enduses and cast to pandas DataFrame
cons = cons.resample('15 Min').mean()  # ... resample from 1 second to 15 minutes
cons.plot()  # ... plot the data
plt.ylim((0, None))  # ... y axis should start at 0
plt.ylabel(r'$Q \quad (\frac{L}{s})$', fontsize=14)  # ... y-axis label with latex code
plt.show()  # ... show plot


# Simulations for multiple houses:
def simulate_house():
    prop = Property(statistics=stats)
    house = prop.built_house()
    house.populate_house()
    house.furnish_house()
    for user in house.users:
        user.compute_presence(statistics=stats)
    house.simulate()
    return house

def simulate(x):

    house = simulate_house()
    cons = house.consumption
    data = cons.sum('user').sum('enduse').to_pandas()
    data.name = house._id
    return data

number_of_houses = 20

results = list(map(simulate, range(number_of_houses)))
results = pd.concat(results, axis=1)
total = results.sum(axis=1)

total.plot(alpha=0.3)
total.rolling('2H').mean().plot(color='k')
plt.ylim((0, None))
plt.show()





