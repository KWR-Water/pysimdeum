# Discharge overview

## Overview

`pysimdeum` allows for the simulation of water discharge at the end-use level. The discharge simulation relies on the simulation of water consumption at the end-use level. On a basic level, discharge simulations work on the principle of conservation of volume, with the exception for consumption events that result in use of water, such as drinking water from a kitchen tap.

By default, discharge simulations are not simulated, but can be enabled by the `simulate_discharge=True` argument when simulating a house: 

```python
house.simulate(duration='1 day', num_patterns=1, simulate_discharge=True)
```

Discharge of water typically occurs after the consumption event begins. For simple enduses such as a `BathroomTap` this discharge begins when consumption is initiated. Other appliances such as a `Bathtub` have a usage time resulting in a delay before a discharge event begins following a consumption event. More complex enduses such as the `WashingMachine` and `Dishwasher` have cycles of discharge events that follow their respective consumption cycles. The `Wc` is an exception where the discharge event must occur immediately before a consumption event.

## Methodology

Discharge calculations in `pysimdeum` follow a simple method of calculating the volume of water consumed over a consumption event of an enduse, and discharging this at a sampled discharge flow rate.  To provide some stochastic behaviour, low and high ranges of discharge flow rates inform the bounds of a uniform distribution from which a discharge flow rate for a specific enduse discharge event is sampled. Details for each enduse are described in the sections [Common Methods]() and [Enduse specifics]().

## Object structure

The `discharge` object follows an almost identical structure to the `consumption` object. Results are stored as a `xarray.DataArray` so that simulation information can be accessed and aggregared afterwards (e.g. specific enduses, sum over water discharge of users, rolling means over time etc.).

The `discharge` array has four dimensions:
- Time
- User
- Enduse
- Patterns