import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.dates import DateFormatter


import pySIMDEUM

# Built a house (one-person household)
house = pySIMDEUM.built_house(house_type='one_person')
print(house)

# Show the inhabitants of a house
print("List of Users:")
print(house.users)

# Show water end-use devices present in the house
print("List of Devices:")
print(house.appliances) 

# Simulate water consumption for house (xarray.DataArray)
consumption = house.simulate(num_patterns=100)

# Build statistics from consumption
tot_cons = consumption.sum(['enduse', 'user']).mean([ 'patterns'])
print(tot_cons)

# Plot total consumption
tot_cons.plot()
tot_cons.rolling(time=3600, center=True).mean().plot()
plt.show()

fig, ax = plt.subplots()
ax.set_ylim((0, None))
ax.set_xlim((pd.to_datetime('2022-07-18 00:00'), pd.to_datetime('2022-07-19 00:00')))
date_form = DateFormatter("%H:%M")
ax.xaxis.set_major_formatter(date_form)

plt.show()


# fig, ax = plt.subplots()

# ax.set_ylim((0, None))
# ax.set_xlim((pd.to_datetime('2022-07-17 00:00'), pd.to_datetime('2022-07-18 00:00')))
# date_form = DateFormatter("%H:%M")
# ax.xaxis.set_major_formatter(date_form)

# plt.show()