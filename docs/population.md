# Population object

The `Population` module in pySIMDEUM is designed to model population distribution and household occupancies within subcatchments and boundaries. It provides tools to simulate multiple houses in a region, aggregate their wastewater profiles, and prepare data for further analysis or integration with external systems like Infoworks ICM.

This module includes the `Population` and `DataPrep` classes, which work together to preprocess input datasets, assign household types, and aggregate wastewater profiles at the subcatchment level.

## Overview

In most cases, it is expected the user would want to simulate multiple houses at once to represent a population of houses in a region. There are a few methods which allow pySIMDEUM users to achieve this; these are covered by example notebook [7. Advanced simulation: Population fitting and subcatchment aggregation](../examples/7_advanced_simulation_population_fitting_and_subcatchment_aggregation.ipynb). The notebook shows the methods of:

* Manual scripting approach
* `build_multi_hh()` api method
* `Population` class method

If the user wants to take a simple approach then one of the first two methods are suitable. The `Population` class is the more advanced method which provides additional features such as using granual census population count for boundaries within your study area to fit household occupancies to provided house location data.

This method is supported by the `DataPrep` class `spatial_config` which together help prepare the various input files needed for this method into a standardised format that works with the `Population` method.

Data files needed and their expected columns are:

* Census boundaries file (e.g. `.geojson`)
    * census boundary ids
    * geometry
* Census population count (with ids matching boundaries file)
    * census boundary ids
    * population count
* House location points (unique ids)
    * ids
    * building type (assuming file includes mix of resi and non-resi)
* Subcatchment boundaries (e.g. `.geojson`)
    * ids
    * geometry

The `DataPrep` class and `spatial_config.toml` essentially help map column ids from your raw dataset to the expected inputs for the `Population` method. We can read in the config file to just understand the different sections. The first section `dataset` is the file path to each of your respective files.

## Data Preparation (`DataPrep` class)

The DataPrep class is responsible for preprocessing input datasets based on a TOML configuration file. It standardises input data into a format compatible with the Population class.

### Key Features:
* Configuration-based preprocessing:
    * Reads a TOML configuration file to map raw dataset columns to expected column names.
* Dataset loading:
    * Supports geospatial datasets (e.g., .geojson) and tabular datasets (e.g., .csv).
* Geospatial operations:
    * Reprojects datasets to the appropriate coordinate reference system (e.g., EPSG:27700 for the UK).
* Preprocessed datasets:
    * Outputs datasets for subcatchments, boundaries, population counts, and house locations.

### Requirements:
* A valid TOML configuration file (`spatial_config.toml`) with the following sections:
    * datasets: Paths to input files.
    * columns: Column mappings for each dataset.

## Population Modeling (`Population` class)

The `Population` class models household occupancies and aggregates wastewater profiles for subcatchments. It uses spatial data to assign household types and simulate multiple houses.

### Key Features:
* Spatial clipping:
    * Clips boundaries and houses to subcatchments to ensure only relevant data is processed.
* Household assignment:
    * Assigns occupancy types (e.g., one_person, two_person, family) to houses based on census population counts and household probabilities.
* Simulation preparation:
    * Prepares household data for simulation using the `build_multi_hh()` API method.
* Subcatchment aggregation:
    * Aggregates household wastewater profiles to subcatchment levels, including total flow and nutrient concentrations.

### Key Methods:
* `spatial_clipping_and_pop_count()`:
    * Clips boundaries and houses to subcatchments and calculates household and population totals for each boundary.
* `fit_hh_population()`:
    * Optimises household probabilities and calculates household counts for each boundary.
* `assign_occupancy_types()`:
    * Assigns occupancy types to houses based on optimised probabilities.
* `clip_houses_to_subs()`:
    * Clips houses to subcatchments for further processing.
* `calculate_subcatchment_profiles()`:
    * Aggregates household profiles for each subcatchment.
    * Outputs a dictionary with subcatchment IDs as keys and aggregated profiles as values.
* `calculate_subcatchment_ww_nutrient_profiles()`:
    * Aggregates wastewater flow and nutrient concentrations for each subcatchment.
    * Outputs a dictionary with:
        * `daily_flow`: Total daily flow for each subcatchment.
        * `hourly_average`: Average hourly flow for each subcatchment.
        * `ww_profile`: A DataFrame with aggregated flow and nutrient concentrations.

### Requirements
The `Population` module requires the following input datasets:
* Subcatchments:
    * Geospatial file with subcatchment geometries and unique IDs.
* Boundaries:
    * Geospatial file with boundary geometries and unique IDs.
* Population counts:
    * Tabular file with population counts for each boundary.
* House locations:
    * Geospatial file with house geometries and attributes.

### Outputs
The `Population` objects holds standard `House` objects and their associated `consumption` and `discharge` objects that can be accessed as normal. In addition, the subcatchment aggregation allows for the following unique objects to be included (which are ultimately used for export to Infoworks ICM):

* Subcatchment wastewater profiles
    * The `Population` class outputs aggregated profiles for each subcatchment, including:
        * Daily flow
            * Total daily wastewater flow for each subcatchment.
        * Hourly average
            * Average hourly flow for each subcatchment.
        * Wastewater profile
            * A DataFrame with aggregated flow and nutrient concentrations for each timestamp