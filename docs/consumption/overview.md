# Consumption overview

## Overview

`pysimdeum` allows for the simulation of water usage at the end-use level with a time resolution of 1 second. Water usage is simulated per user per end use.
It is envoked by using:

```python
house.simulate(duration='1 day', num_patterns=1)
```

`pysimdeum` will simulate both the total water usage as well as the hot water part of that consumption, again per user per end-use.

## Methodology


## Object structure

The `consumption` object is stored as a `xarray.DataArray` in a similar fashion as the `discharge` object. The `xarray.DataArray` allows for easy access
to specific enduses, users or moments in time and allows for aggregation, summing, averaging etc.

The `consumption` array has five dimensions:

- Time
- User
- Enduse
- Patterns
- Flowtype

Here Time, represents time (default in seconds), User represents users (depending on number of occupants of the house) or `household` (some water usage is attributed to the household instead of a specific user), Enduse represents the different possible enduses like `bath`, `shower`, `kitchentap` etc, Patterns represents different simulations with the same settings and flotype can have two values: `totalflow` and `hotflow`, where totalflow is the total water usage while hotflow is that part of the water usage that was heated.

To-do:
Explanation of concept and structure of `consumption` object

- Object structure
- Enduse penentration

