import pySIMDEUM
import matplotlib.pyplot as plt

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
