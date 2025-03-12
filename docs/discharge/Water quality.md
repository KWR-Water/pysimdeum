# Water Quality

## Overview

`pysimdeum` treats water quality calculations as a post-processing step after simulation. Simulated wastewater profiles in the form of a `discharge` object are the assumed input for both nutrient and temperature calculations.

!!! info 
    Note that water quality calculations are applied outside the simulation stage and will not be generated when simulating discharge patterns.

## Nutrient Concentrations

### Methodology

The nutrient concentration calculations in `pysimdeum` are performed using a series of steps that process simulated discharge profiles and enrich it with nutrient concentrations based on input statistics from a [wastewater nutrient config](schema.md). These calculations inclusde steps to manipulate data from `xarray.Dataset` and `xarray.DataArray` objects, converting them to `pandas.DataFrame` objects for easier manipulation and calculation.

1. **Data extraction and enrichment**
    - Discharge data is extracted from `discharge` object (`xarray.Dataset`) and converted to a `pandas.DataFrame`. This DataFrame is then enriched with metadata, including `usage` and `event_label` columns, based on the discharge event metadata provided in the dataset.

1. **Nutrient sampling**
    - Nutrient concentrations (g/use) are sampled from a truncated normal distribution. The mean values for the distribution are read from a TOML config file, which contains statistics for enduse and usage type level, i.e. difference nutrient concentrations for `urine` and `faeces` use of a `Wc` enduse.

1. **Nutrient concentration** 
    - The nutrient concentration for each discharge event is calculated by dividing the sampled nutrient value by the total flow for the discharge event, resulting in a concentration in grams per liter (g/L).

## Temperature

tbc