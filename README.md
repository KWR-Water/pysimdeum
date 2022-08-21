######### Begin old text

# pysimdeum
Repository to share demand generator Python software with Mirjam Blokker and KWR

Uses Python 3.x

Used Python packages:

* `numpy`
* `pandas`
* `matplotlib`
* `scipy`
* `xarray`
* `traits` (for strict type definitions of classes, could be replaced by Python's type annotations)
* `toml`


It is recommended to install Python Anaconda distribution from https://www.anaconda.com/distribution/

All packages can be installed either with `conda install <packagename>` or `pip install <packagename>` in a terminal. 
(Actually, `toml` is the only package that has to be installed with `pip`)

The Python script `sim_water_use.py` shows how the pysimdeum can be used.
######### End old text


# PYSIMDEUM
pysimdeum is a Python package for modelling and simulating residential stochastic water demand at the end-use level.

Main functionalities:

-	Build and populate houses with users and water end-use devices according to country specific statistics
-	Simulate water usage stochastically based on the statistics 
-	The results are stored as `xarray.DataArray`, so all the simulation information can be accessed and aggregated afterwards (e.g., specific end-uses, sums over water usage of users, rolling means over time, ...)
-   Serialization: pysimdeum supports different output formats (e.g., csv, excel, netcdf, ...)
-	Plotting results using matplotlib

A detailed documentation is available under https://pysimdeum.readthedocs.io.

---
**Warning!**

Be warned, that pysimdeum is still changing a lot. Until it's marked as 1.0.0, you should assume that it is unstable and act accordingly. We are trying to avoid breaking changes but they can and will occur!

---

## Installation

pysimdeum uses features only available in a newer Python version, which is why Python >= 3.8 is needed along with several Python package dependencies.

pysimdeum is available on PyPI and can be easily installed together with its dependencies using `pip`:

```bash
pip install pysimdeum
```

Alternatively, you can install pysimdeum from its repository:


```bash
pip install git+https://github.com/KWR-Water/pysimdeum.git
```

### Dependencies
pysimdeum requires the following Python packages:

- matplotlib
- numpy
- pandas
- toml
- xarray
- scipy

## Basic Usage

To use pysimdeum, you first have to import it in your script:

```python
import pysimdeum
```

In pysimdeum, everything is about the `House`. If you want to start with a new, empty House, type the following:

```python
house = pySIMDEUM.built_house(house_type='one_person')
```

If you want to build a specific House, e.g., a one-person household, you can use the `house_type` keyword:

```python
house = pySIMDEUM.built_house(house_type='one_person')
```
The house is automatically populated by people, which follow certain statistics, and "furnished" with water end-use devices or appliances (e.g., toilet, bathtub, ...). You can check, which appliances are available by using the `appliances` or `users` property of the House:

```python
print(house.users)
print(house.appliances)
```

To simulate the water consumption of a house, you can use the House\`s `simulate` method:

```python
consumption = house.simulate(num_patterns=100)
```


If you want to create a basic Network plot, you can use its `plot` method:

```python
network.plot()
```

## License

OOPNET is available under a [EUPL-1.2 license](https://github.com/KWR-Water/pysimdeum/blob/main/LICENSE).

## Contributing
If you want to contribute, please check out our [Code of Conduct](https://github.com/KWR-Water/pysimdeum/blob/main/CODE_OF_CONDUCT.md) and our [Contribution Guide](https://github.com/KWR-Water/pysimdeum/blob/main/CONTRIBUTING.md). Looking forward to your pull request or issue!

## Citing
If you publish work based on OOPNET, we appreciate a citation of the following reference:
 
 - Steffelbauer, D., Fuchs-Hanusch, D., 2015. OOPNET: an object-oriented EPANET in Python. Procedia Eng. 119, 710e718. https://doi.org/10.1016/j.proeng.2015.08.924.