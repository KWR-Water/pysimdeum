import pandas as pd
import geopandas as gpd
import numpy as np
import os
from shapely.ops import unary_union
from pysimdeum.data import DATA_DIR
from pysimdeum.utils.probability import optimise_probabilities
from pysimdeum.utils.misc import fix_invalid_geometries
import pysimdeum.utils.wastewater_quality as wq
from pysimdeum.api import build_multi_hh
import toml


class DataPrep:
    """
    A class to preprocess input datasets based on a TOML configuration file.

    This class reads datasets from specified file paths provided in a config file,
    renames columns based on the configuration, and prepares them for use in the Population class.
    """

    def __init__(
            self,
            config_path: str = None,
            country: str = 'NL'
        ):
        """
        Initialises the DataPrep class by determining the configuration file location.

        Args:
            config_path (str): Path to the configuration file (TOML format). If None, the country folder is used.
            country (str): Country name (e.g., 'NL', 'UK') to locate the configuration file in the default data directory.
        """
        if config_path and os.path.isfile(config_path):
            self.config_file = config_path
        elif os.path.isdir(country):
            self.config_file = os.path.join(country, 'spatial_config.toml')
            self.country = None
        else:
            self.config_file = os.path.join(DATA_DIR, country, 'spatial_config.toml')
            self.country = country

        # validate that the configuration file exists
        if not os.path.isfile(self.config_file):
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")

        # Load the configuration
        self.config = toml.load(self.config_file)
        
        #self.datasets = {}
        self.load_datasets()

    def _load_and_preprocess(self, dataset_key: str, is_geospatial: bool = False):
        """
        Helper method to load and preprocess a dataset.

        Args:
            dataset_key (str): The key in the configuration file for the dataset (e.g., 'subcatchments').
            is_geospatial (bool): Whether the dataset is a geospatial file (True for GeoDataFrame).

        Returns:
            pd.DataFrame or gpd.GeoDataFrame: The preprocessed dataset.
        """
        # Get the dataset path and column mappings from the configuration
        dataset_path = self.config['datasets'][dataset_key]
        column_mapping = self.config['columns'][dataset_key]
        column_mapping = {v: k for k, v in column_mapping.items()} # reverse mapping

        # Load the dataset
        if is_geospatial:
            dataset = gpd.read_file(dataset_path)
            if self.country == 'UK':
                dataset = dataset.to_crs(epsg=27700)
        else:
            dataset = pd.read_csv(dataset_path)

        # Rename and select only the columns of interest
        dataset = dataset.rename(columns=column_mapping)[list(column_mapping.values())]

        return dataset

    def load_datasets(self):
        """
        Loads and preprocesses datasets based on the configuration file.

        Returns:
            dict: A dictionary containing preprocessed datasets.
        """
        self.datasets = {
            'subcatchments': self._load_and_preprocess('subcatchments', is_geospatial=True),
            'boundaries': self._load_and_preprocess('boundaries', is_geospatial=True),
            'boundaries_pop': self._load_and_preprocess('boundaries_pop', is_geospatial=False),
            'houses': self._load_and_preprocess('houses', is_geospatial=True),
        }


class Population:
    """
    Model population distribution and households occupancies within subcatchments and boundaries,
    to inform simulation of multiple houses.

    This class performs spatial operations, assigns household types, and prepares data
    for simulation of multiple houses in a region. It uses spatial data to clip boundaries
    and houses, fit household probabilities, and assign occupancy types. The class returns
    a series of pysimdeum.House instances.

    Attributes:
        subcatchments (gpd.GeoDataFrame): GeoDataFrame containing subcatchment geometries.
        boundaries (gpd.GeoDataFrame): GeoDataFrame containing boundary geometries.
        boundaries_pop (pd.DataFrame): DataFrame containing population data for boundaries.
        houses (gpd.GeoDataFrame): GeoDataFrame containing house geometries and attributes.
        boundary_counts (pd.DataFrame): DataFrame containing household and population totals for each boundary.
        results (dict): Dictionary containing household counts and probabilities for each boundary.
        houses_instances (list): List of pysimdeum.House instances prepared for simulation.
        sample (bool): Whether to sample a subset of houses or proces the entire dataset.
    """

    def __init__(
            self,
            datasets: dict,
            sample: bool = False,
            duration: str = '1 day',
            country: str = None,
            simulate_discharge: bool = False,
            spillover: bool = False
        ):
        """
        Initialises the Population class with preprocessed datasets.

        Args:
            datasets (dict): A dictionary containing preprocessed datasets:
                - 'subcatchments': GeoDataFrame of subcatchments.
                - 'boundaries': GeoDataFrame of boundaries.
                - 'boundaries_pop': DataFrame of population data for boundaries.
                - 'houses': GeoDataFrame of houses.
        """
        
        self.subcatchments = fix_invalid_geometries(datasets['subcatchments'])
        self.boundaries = datasets['boundaries']
        self.boundaries_pop = datasets['boundaries_pop']
        self.houses = datasets['houses']
        self.sample = sample

        self._prepare_data()

        self.houses_instances = build_multi_hh(self.household_data, duration=duration, country=country, simulate_discharge=simulate_discharge, spillover=spillover)
        self.subcatchment_profiles = self.calculate_subcatchment_profiles()
        #self.subcatchment_nutrients_profiles = self.calculate_subcatchment_nutrient_profiles()

    def _prepare_data(self):
        """
        Prepares the data for simulation of multiple houses in a region.

        This method performs the following steps:
            1. Clips boundaries and houses to subcatchments.
            2. Calculates household and population totals for each boundary.
            3. Optimises household probabilities and assigns occupancy types to houses.
            4. Clips houses to subcatchments and prepares household data for simulation.
        """

        probabilities = np.array([0.30, 0.34, 0.36])
        household_sizes = np.array([1, 2, 3.75])
        
        self.boundary_counts = self.spatial_clipping_and_pop_count()
        self.results = self.fit_hh_population(probabilities, household_sizes)
        
        self.houses['occupancy_type'] = None
        self.houses = self.assign_occupancy_types()
        self.clip_houses_to_subs()
        self.household_data = self.household_data_prep()


    def _clip_boundaries_to_subcatchments(self):
        """
        Clips boundaries to subcatchments and updates the boundaries GeoDataFrame.

        This method uses the union of all subcatchment geometries to clip the boundaries
        and retain only those that intersect with the subcatchments.
        """
        subs_outline = gpd.GeoDataFrame(geometry=[unary_union(self.subcatchments.geometry)], crs=self.subcatchments.crs)
        self.boundaries = gpd.sjoin(self.boundaries, subs_outline, how='inner', predicate='intersects').drop(columns='index_right')


    def _filter_population_data(self):
        """
        Filters population data to include only boundaries that intersect with subcatchments.

        This method ensures that the population data is restricted to the boundaries
        that are within the subcatchments.
        """
        self.boundaries_pop = self.boundaries_pop[self.boundaries_pop['boundary_id_code'].isin(self.boundaries['boundary_id'].unique())][['boundary_id_code', 'population']]


    def _filter_houses(self):
        """
        Filters houses to include only those within the selected boundaries.

        This method performs a spatial join to retain houses that intersect with the boundaries
        and filters for houses with the `BaseFuncti` attribute set to 'DWELLING'.
        """
        self.houses = gpd.sjoin(self.houses, self.boundaries, how='inner', predicate='intersects').drop(columns='index_right').rename(columns={'boundary_id': 'hh_boundary_id'})
        self.houses = self.houses[self.houses['function'] == 'DWELLING'][['house_id', 'hh_boundary_id', 'geometry']]

    
    def spatial_clipping_and_pop_count(self):
        """
        Clips boundaries and houses to subcatchments and calculates household and population totals.

        This method performs the following steps:
            1. Clips boundaries to subcatchments.
            2. Filters population data to include only relevant boundaries.
            3. Filters houses to include only those within the selected boundaries.
            4. Calculates household and population totals for each boundary.

        Returns:
            pd.DataFrame: A DataFrame containing household and population totals for each boundary.
        """
        self._clip_boundaries_to_subcatchments()
        self._filter_population_data()
        self._filter_houses()

        # Calculate household and population totals for each OA
        boundary_counts = (
            self.houses.groupby('hh_boundary_id')
            .size()
            .reset_index(name='household_tots')
            .merge(self.boundaries_pop, left_on='hh_boundary_id', right_on='boundary_id_code')
            .drop(columns='boundary_id_code')
            .rename(columns={'population': 'pop_tot'})
        )

        return boundary_counts
    

    def fit_hh_population(self, probabilities, household_sizes):
        """
        Fits household probabilities and calculates household counts for each boundary
        in the input DataFrame.

        Args:
            probabilities (list): Initial probabilities for each household category.
            household_sizes (list): Average household sizes for each category.

        Returns:
            dict: A dictionary where keys are boundary labels and values are nested dictionaries
                with household counts for each category and the optimised probabilities.
        """
        results = {}

        # Iterate through each row in the boundary_counts DataFrame
        for _, row in self.boundary_counts.iterrows():
            boundary_label = row['hh_boundary_id']
            total_population = float(row['pop_tot'])
            total_households = int(row['household_tots'])

            # Optimise probabilities for the current boundary
            optimised_probs = optimise_probabilities(
                starting_probs=np.array(probabilities),
                total_population=total_population,
                total_households=total_households,
                household_sizes=np.array(household_sizes)
            )

            # Calculate household counts based on the optimised probabilities
            household_counts = (optimised_probs * total_households).round().astype(int)
            households_one_person, households_two_person, households_family = household_counts
            optimised_probs = [float(round(prob, 3)) for prob in optimised_probs]

            # Store the results in the dictionary
            results[boundary_label] = {
                "one_person": int(households_one_person),
                "two_person": int(households_two_person),
                "family": int(households_family),
                "probabilities": optimised_probs
            }
        
        return results
    

    def assign_occupancy_types(self):
        """
        Assigns occupancy types to houses based on the results dictionary.

        This method loops through the results dictionary, filters houses for each boundary,
        shuffles the rows to ensure random assignment, and assigns occupancy types based on
        the number of each type available.

        Returns:
            pd.DataFrame: Updated houses GeoDataFrame with assigned occupancy types.
        """
        updated_houses = self.houses.copy()

        for boundary_id, counts in self.results.items():
            # Filter houses to rows where boundary_id matches the current key
            filtered_houses = updated_houses[updated_houses['hh_boundary_id'] == boundary_id]

            # Shuffle rows to ensure random assignment
            shuffled_houses = filtered_houses.sample(frac=1, random_state=42)

            # Get the number of each household type from the results dictionary
            one_person_count = counts['one_person']
            two_person_count = counts['two_person']
            family_count = counts['family']

            # Assign occupancy_type based on the counts using .iloc for positional slicing
            shuffled_houses.iloc[:one_person_count, shuffled_houses.columns.get_loc('occupancy_type')] = 'one_person'
            shuffled_houses.iloc[one_person_count:one_person_count + two_person_count, shuffled_houses.columns.get_loc('occupancy_type')] = 'two_person'
            shuffled_houses.iloc[one_person_count + two_person_count:one_person_count + two_person_count + family_count, shuffled_houses.columns.get_loc('occupancy_type')] = 'family'

            # Update the original DataFrame with the assigned occupancy types
            updated_houses.loc[shuffled_houses.index, 'occupancy_type'] = shuffled_houses['occupancy_type']

        return updated_houses
    

    def clip_houses_to_subs(self):
        """
        Clips houses to subcatchments.
        """
        # filter to houses contained within subs
        self.houses = self.houses[self.houses['geometry'].within(self.subcatchments.union_all())]
        self.houses = self.houses.sjoin(self.subcatchments[['subcatchment_id', 'geometry']], predicate='within').drop(columns='index_right')[['house_id','hh_boundary_id','subcatchment_id','occupancy_type','geometry']] 


    def household_data_prep(self):
        """
        Prepares household data for use in the simulation.

        This method samples a subset of houses from the `houses` GeoDataFrame, extracts their
        `TOID` and `occupancy_type`, and returns the data as a dictionary. The dictionary maps
        each house's `TOID` to its corresponding `occupancy_type`.

        Returns:
                dict: A dictionary where:
                    - Keys are `TOID` (unique identifiers for each house).
                    - Values are `occupancy_type` (type of occupancy for each house, e.g., 'one_person', 'two_person', 'family').
        """
        if self.sample:
            household_data = self.houses[['house_id', 'occupancy_type']].sample(10).set_index('house_id')['occupancy_type'].to_dict()
        else:
            household_data = self.houses[['house_id', 'occupancy_type']].set_index('house_id')['occupancy_type'].to_dict()
        
        return household_data
    

    def _house_subcatchment_mapping(self):
        """Generates a dictionary with subcatchment IDs as keys and lists of house IDs as values.

        Groups houses by their `subcatchment_id` and creates a dictionary where the keys are
        subcatchment IDs and the values are lists of house TOIDs/

        Returns:
            dict: A dictionary where:
                - Keys are `subcatchment_id` (unique identifiers for each subcatchment).
                - Values are lists of `house_id` (TOIDs) for houses in each subcatchment.
        """
        if 'subcatchment_id' not in self.houses.columns or 'house_id' not in self.houses.columns:
            raise ValueError("The houses GeoDataFrame must contain 'subcatchment_id' and 'house_id' columns.")

        # Group houses by subcatchment_id and collect house_id (TOIDs) as lists
        self.subcatchment_houses = (
            self.houses.groupby('subcatchment_id')['house_id']
            .apply(list)
            .to_dict()
        )

        return self.subcatchment_houses
    

    def calculate_subcatchment_profiles(self):
        """
        Calculates the profiles of subcatchments based on household types.

        This method generates a dictionary where the keys are subcatchment IDs and the values
        are dictionaries containing counts of each household type within that subcatchment.
        """
        self.subcatchment_houses = self._house_subcatchment_mapping()

        # Initialise a dictionary to store the aggregated profiles
        subcatchment_profiles = {}

        # Iterate through each subcatchment and its associated house IDs
        for subcatchment_id, house_ids in self.subcatchment_houses.items():
            total_profile = None  # Initialise the total profile for this subcatchment

            # Iterate through each house ID in the subcatchment
            for house_id in house_ids:
                # Retrieve the house instance from houses_instances
                house_instance = self.houses_instances.get(house_id)

                if house_instance is None:
                    # Skip if the house instance is not found
                    continue

                # Extract the consumption DataArray and select the total flow
                house_profile = (
                    house_instance.consumption
                    .sum(['enduse', 'user'])  # Sum across end uses and users
                    .sel(flowtypes='totalflow')  # Select the total flow
                )

                # Aggregate the house profile into the total profile for the subcatchment
                if total_profile is None:
                    total_profile = house_profile
                else:
                    total_profile += house_profile

            # Store the aggregated profile for the subcatchment
            if total_profile is not None:
                subcatchment_profiles[subcatchment_id] = total_profile

        return subcatchment_profiles


    def calculate_subcatchment_nutrient_profiles(self):
        """
        Calculates the total flow and weighted nutrient concentrations for each subcatchment.

        This method applies the `hh_discharge_nutrients` function to the discharge data
        of all houses and aggregates the results by subcatchment using vectorised operations.

        Args:
            hh_discharge_nutrients (function): A function that calculates nutrient concentrations
                                            and flow rates from the discharge data of a house.

        Returns:
            dict: A dictionary where:
                - Keys are `subcatchment_id` (unique identifiers for each subcatchment).
                - Values are Pandas DataFrames with the following columns:
                    - `time`: The timestamp.
                    - `total_flow`: The total flow for all houses in the subcatchment at each timestep.
                    - Nutrient columns (e.g., `nutrient_1`, `nutrient_2`, etc.) containing the
                    weighted average nutrient concentrations for the subcatchment at each timestep.
        """
        # Initialise a list to store all house nutrient data
        all_house_data = []

        # Iterate through all houses and calculate nutrient data
        for house_id, house_instance in self.houses_instances.items():
            if house_instance is None or not hasattr(house_instance, 'discharge'):
                # Skip if the house instance is not found or does not have discharge data
                continue

            # Extract the discharge data for the house
            house_discharge = house_instance.discharge.discharge

            # Apply the hh_discharge_nutrients function to calculate nutrient concentrations and flow
            house_nutrients = wq.hh_discharge_nutrients(house_discharge)

            # Add the subcatchment ID to the house nutrient data
            house_nutrients['subcatchment_id'] = self.houses.loc[self.houses['house_id'] == house_id, 'subcatchment_id'].values[0]

            # Append the house nutrient data to the list
            all_house_data.append(house_nutrients)

        # Combine all house nutrient data into a single DataFrame
        all_house_data_df = pd.concat(all_house_data, ignore_index=True)

        # Group by subcatchment and time, and calculate total flow and weighted nutrient concentrations
        grouped = all_house_data_df.groupby(['subcatchment_id', 'time'])
        subcatchment_wq_profiles = {}

        for subcatchment_id, group in grouped:
            # Calculate total flow for the subcatchment
            total_flow = group['flow'].sum()

            # Calculate weighted average nutrient concentrations
            weighted_nutrients = group.drop(columns=['subcatchment_id', 'time', 'flow']).multiply(group['flow'], axis=0).sum() / total_flow

            # Combine total flow and weighted nutrients into a single DataFrame
            subcatchment_df = pd.DataFrame(weighted_nutrients).T
            subcatchment_df['total_flow'] = total_flow
            subcatchment_df['time'] = group['time'].iloc[0]

            # Add the DataFrame to the dictionary
            if subcatchment_id not in subcatchment_wq_profiles:
                subcatchment_wq_profiles[subcatchment_id] = []
            subcatchment_wq_profiles[subcatchment_id].append(subcatchment_df)

        # Convert lists of DataFrames to a single DataFrame for each subcatchment
        for subcatchment_id in subcatchment_wq_profiles:
            subcatchment_wq_profiles[subcatchment_id] = pd.concat(subcatchment_wq_profiles[subcatchment_id], ignore_index=True)

        return subcatchment_wq_profiles
    

