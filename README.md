<!--- the "--8<--" html comments define what part of the README to add to the index page of the documentation -->
<!--- --8<-- [start:docs] -->
# PYSIMDEUM

`pysimdeum` is a Python package for modelling and simulating residential stochastic water demand and discharge at the end-use level.

Main functionalities:

-	Build and populate houses with users and water end-use devices according to region (e.g. country, city, state) specific statistics
-	Simulate water usage and demand stochastically based on the statistics 
-	The results are stored as `xarray.DataArray`, so all the simulation information can be accessed and aggregated afterwards (e.g., specific end-uses, sums over water usage of users, rolling means over time, ...)
-   Serialisation: `pysimdeum`  supports different output formats (e.g., csv, excel, netcdf, ...)
-	Plotting results using matplotlib
<!--- --8<-- [end:docs] -->

For more detailed instructions, see our [documentation](https://pysimdeum.readthedocs.io/en/latest/).

Output is based on statistics about household sizes and water use of the Netherlands. These can be changed either within the code or by creating the correct toml files. An overview of worldwide differences is available in:

Mazzoni, F., Alvisi, S., Blokker, E. J. M., Buchberger, S. G., Castelletti, A., Cominola, A., Gross, M. P., Jacobs, H. E., Mayer, P., Steffelbauer, D. B., Stewart, R. A., Stillwell, A. S., Tzatchkov, V., Yamanaka, V. H. A. and Franchini, M. (2022). "Investigating the characteristics of residential end uses of water: a worldwide review." Water Research, art. no. 119500, https://www.sciencedirect.com/science/article/abs/pii/S0043135422014452
<!--- --8<-- [end:docs] -->

## Installation

`pysimdeum`  uses features only available in a newer Python version, which is why Python >= 3.8 is needed along with several Python package dependencies.

### As a user

`pysimdeum`  is available on PyPI and can be easily installed together with its dependencies using `pip`:

<!--- --8<-- [start:docs-install-PyPI] -->
```bash
pip install pysimdeum
```
<!--- --8<-- [end:docs-install-PyPI] -->

Alternatively, you can install `pysimdeum`  from its repository:


<!--- --8<-- [start:docs-install-repo] -->
```bash
pip install git+https://github.com/KWR-Water/pysimdeum.git
```
<!--- --8<-- [end:docs-install-repo] -->


### As a developer

<!--- --8<-- [start:docs-install-dev] -->
```bash
git clone git@github.com:KWR-Water/pysimdeum.git
cd pysimdeum
mamba create -n pysimdeum python=3.11 pip -c conda-forge
mamba activate pysimdeum
pip install -r requirements.txt .

```
<!--- --8<-- [end:docs-install-dev] -->

## Basic Usage

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
<div style="display: flex; justify-content: center;">
    <figure style="text-align: center;">
        <img src="/images/consumption_totalflow.png", width="60%", style="background-color:white; margin:auto", alt="Consumption total flow">
    </figure>
</div>


<div style="display: flex; justify-content: center;">
    <figure style="text-align: center;">
        <img src="/images/consumption_totalflow_rollingav.png", width="60%", style="background-color:white; margin:auto", alt="Consumption total flow, 1-hour rolling average">
    </figure>
</div>
   
Or produce plots for a specific enduse such as `KitchenTap`

```python
# Plot total consumption of KitchenTap enduse
consumption.sum(["user"]).sel(enduse="KitchenTap").sel(flowtypes="totalflow").plot()
```

<div style="display: flex; justify-content: center;">
    <figure style="text-align: center;">
        <img src="/images/consumption_ktap_totalflow.png", width="60%", style="background-color:white; margin:auto", alt="KitchenTap total consumption">
    </figure>
</div>

## License

`pysimdeum` is available under a [EUPL-1.2 license](https://github.com/KWR-Water/pysimdeum/blob/master/LICENSE).

## Contributing

If you want to contribute, please check out our [Code of Conduct](https://github.com/KWR-Water/pysimdeum/blob/master/CODE_OF_CONDUCT.md) and our [Contribution Guide](https://github.com/KWR-Water/pysimdeum/blob/master/CONTRIBUTING.md). Looking forward to your pull request or issue!

## Citing

If you publish work based on `pysimdeum` , we appreciate a citation of the following reference:
 
 - Steffelbauer, D.B., Hillebrand B., Blokker, E.J.M., 2022. pySIMDEUM: An open-source stochastic water demand end-use model in Python. Proceedings of the 2nd joint Water Distribution System Analysis and Computing and Control in the Water Industry (WDSA/CCWI2022) conference, Valencia (Spain), 18-22 July 2022.
