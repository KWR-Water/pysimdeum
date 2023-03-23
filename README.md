# PYSIMDEUM

`pysimdeum` is a Python package for modelling and simulating residential stochastic water demand at the end-use level.

Main functionalities:

-	Build and populate houses with users and water end-use devices according to country specific statistics
-	Simulate water usage stochastically based on the statistics 
-	The results are stored as `xarray.DataArray`, so all the simulation information can be accessed and aggregated afterwards (e.g., specific end-uses, sums over water usage of users, rolling means over time, ...)
-   Serialization: `pysimdeum`  supports different output formats (e.g., csv, excel, netcdf, ...)
-	Plotting results using matplotlib

A detailed documentation will be soon available under https://pysimdeum.readthedocs.io.

Output is based on statistics about household sizes and water use of the Netherlands. These can be changed either within the code or by creating the correct toml files. An overview of worldwide differences is available in:

Mazzoni, F., Alvisi, S., Blokker, E. J. M., Buchberger, S. G., Castelletti, A., Cominola, A., Gross, M. P., Jacobs, H. E., Mayer, P., Steffelbauer, D. B., Stewart, R. A., Stillwell, A. S., Tzatchkov, V., Yamanaka, V. H. A. and Franchini, M. (2022). "Investigating the characteristics of residential end uses of water: a worldwide review." Water Research, art. no. 119500, doi:https://doi.org/10.1016/j.watres.2022.119500.https://www.sciencedirect.com/science/article/pii/S0043135422014452 https://livelink.kwrwater.nl/livelink/livelink.exe/Open/69638292

---
**Warning!**

Be warned, that `pysimdeum`  is still changing a lot. Until it's marked as 1.0.0, you should assume that it is unstable and act accordingly. We are trying to avoid breaking changes but they can and will occur!

---

## Installation

`pysimdeum`  uses features only available in a newer Python version, which is why Python >= 3.8 is needed along with several Python package dependencies.

`pysimdeum`  is available on PyPI and can be easily installed together with its dependencies using `pip`:

```bash
pip install pysimdeum
```

Alternatively, you can install `pysimdeum`  from its repository:


```bash
pip install git+https://github.com/KWR-Water/pysimdeum.git
```

### Dependencies

`pysimdeum`  requires the following Python packages:

- matplotlib
- numpy
- pandas
- toml
- xarray
- scipy

## Basic Usage

To use `pysimdeum` , you first have to import it in your script:

```python
import pysimdeum
```

In `pysimdeum` , everything is about the `House`. If you want to start with a new, empty House, type the following:

```python
house = pySIMDEUM.built_house(house_type='one_person')
```

If you want to build a specific House, e.g., a one-person household, you can use the `house_type` keyword:

```python
# Built a house (one-person household)
house = pySIMDEUM.built_house(house_type='one_person')
```
The house is automatically populated by people, which follow certain statistics, and "furnished" with water end-use devices or appliances (e.g., toilet, bathtub, ...). You can check, which appliances are available by using the `appliances` or `users` property of the House:

```python
# Show users and water end-use devices present in the house
print(house.users)
print(house.appliances)
```

To simulate the water consumption of a house, you can use the House\`s `simulate` method:

```python
# Simulate water consumption for house (xarray.DataArray)
consumption = house.simulate(num_patterns=100)
```

The simulation result is an `xarray.DataArray` --- basically a labelled `numpy.ndarray` with four dimensions / axes (i.e., time, user, enduse, patterns).

You can easily create statistics over the consumption object, for example, to compute the  average total consumption (sum of consumption of all users and enduses as an average over the patterns), you can build the sum over the `user` and `enduse` axes (the total consumption), and then build the mean over the `patterns` axes 

```python
# Build statistics from consumption
tot_cons = consumption.sum(['enduse', 'user']).mean([ 'patterns'])
```

If you want to plot the results pand additionally depict some rolling averages (e.g., hourly means = 3600 seconds), you can this in the following way

```python
# Plot total consumption
tot_cons.plot()
tot_cons.rolling(time=3600, center=True).mean().plot()
plt.show()
```

## License

`pysimdeum` is available under a [EUPL-1.2 license](https://github.com/KWR-Water/pysimdeum/blob/master/LICENSE).

## Contributing

If you want to contribute, please check out our [Code of Conduct](https://github.com/KWR-Water/pysimdeum/blob/master/CODE_OF_CONDUCT.md) and our [Contribution Guide](https://github.com/KWR-Water/pysimdeum/blob/master/CONTRIBUTING.md). Looking forward to your pull request or issue!

## Citing

If you publish work based on `pysimdeum` , we appreciate a citation of the following reference:
 
 - Steffelbauer, D.B., Hillebrand B., Blokker, E.J.M., 2022. pySIMDEUM: An open-source stochastic water demand end-use model in Python. Proceedings of the 2nd joint Water Distribution System Analysis and Computing and Control in the Water Industry (WDSA/CCWI2022) conference, Valencia (Spain), 18-22 July 2022.
