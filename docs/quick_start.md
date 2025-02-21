# Quick Start

Generate one house with a single occupant and simulate consumption and discharge events at enduse level for single day, using the following steps.

Currently, there is no `cli` available so you must run `pysimdeum` via a `.py` script or `.ipynb` Jupyter notebook.

To use `pysimdeum`, you first have to import it in your script:

```python
import pysimdeum
```

In `pysimdeum`, everything is about the `House`. If you want to build a specific House, e.g., a one-erson household, you can use the `house_type` keyword. Type the following:

```python
# Build a one-person household
house = pysimdeum.built_house(house_type='one_person')
```

The house is automatically populated by a person, which follows certain statistics, and "furnished" with water end-use devices or appliances (e.g., toilet, bathtub, ...). You can check which appliances are available, and who are the possible users, by using the `appliances` or `users` property of the House:

```
print(house.users)
print(house.appliances)
```

To simulate the water consumption of a house, you can use the House's `simulate` method:

```python
# Simulate water consumption for house
consumption = house.simulate(num_patterns=1)
```

`pysimdeum` also allows you to simulate discharge flows that are linked to your consumption flows.

```python
# Simulate water consumption and discharge for house
consumption, discharge = house.simulate(num_patterns=1, simulate_discharge=True)
```

The consumption (and discharge) simulation result is an `xarray.DataArray` - basically a labelled `numpy.ndarray` with four dimensions / axes (i.e. `time`, `user`, `enduse`, `patterns`)

You can easily create statistics over the `consumption` and `discharge` objects, for example, to compute the total consumption (sum of consumption of all users and enduses), you can build the sum over the `user` and `enduse` axes (the total consumption). Within `consumption`, there are two `flowtypes` defined. `totalflow` and `hotflow`. `totalflow` reflects the total water use while `hotflow` reflects the water that has been heated up.

```python
# Build statistics from consumption
tot_cons = consumption.sum(['enduse', 'user']).sel(flowtypes='totalflow').mean(['patterns'])
```

If you want to plot the results and additionally depict some rolling averages (e.g. hourly means = 3600 seconds), you can do this in the following way:

```python
# Plot total consumption
tot_cons.plot()
tot_cons.rolling(time=3600, center=True).mean().plot()
plt.show()
```

<figure>
<img src="/images/consumption_totalflow.png", width="100%", style="background-color:white;", alt="Consumption total flow">
<figcaption>Plot of total flow consumption for a one-person household.</figcaption>
</figure>

<figure>
<img src="/images/consumption_totalflow_rollingav.png", width="100%", style="background-color:white;", alt="Consumption total flow, 1-hour rolling average">
<figcaption>Plot of 1-hour rolling average total flow consumption for a one-person household.</figcaption>
</figure>

Or produce plots for a specific enduse such as `KitchenTap`

```python
# Plot total consumption of KitchenTap enduse
consumption.sum(["user"]).sel(enduse="KitchenTap").sel(flowtypes="totalflow").plot()
```

<figure>
<img src="/images/consumption_ktap_totalflow.png", width="100%", style="background-color:white;", alt="KitchenTap total consumption">
<figcaption>Plot of total consumption of the KitchenTap appliance in a one-person household</figcaption>
</figure>