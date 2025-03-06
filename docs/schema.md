# Region Statistics Schema

## Diurnal Patterns

The schema has a section for each demographic (eg. child, teen etc) as well as aggregate categories (total, weekend), each containing a subsection for key activity:

- `getting_up`: Time when the person wakes up.
- `leaving_house`: Time when the person leaves the house.
- `being_away`: Duration of time spent away from home.
- `sleep`: Time when the person goes to sleep.

Each activity is specified using:

- `dist` (string): Distribution type (e.g., `'norm'`)
- `mu` (string): Mean time of the activity (in `HH:MM:SS` format)
- `sd` (string): Standard deviation of the activity time (in `HH:MM:SS` format)

Each activity will follow the structure:

```toml
[demographic]
    [demographic.activity]
        dist = "norm"
        mu = "HH:MM:SS"
        sd = "HH:MM:SS"
```

### Demographic descriptions:

| Category    | Description |
| ----------- | ----------- |
| `child`      | Represents young children (e.g., school-age)  |
| `teen`        | Represents teenagers. Notably not included in UK dataset |
| `work_ad`  | Adults who work outside the home |
| `home_ad`  | Adults who do not work outside the home |
| `senior`  | Senior citizens |
| `total`  | Aggregated routines for the entire household |
| `weekend`  | Average household routines during the weekends |

### Custom Configs

To create a custom configuration:

- Copy an existing structure from the data in the repo.
- Modify the `mu` values to represent the desired schedule.
- Adjust the `sd` values to control variability (higher values = more variation).
- Save the `.toml` file in the appropriate config directory.


## Household Statistics

This config file has a section for each household type. Household types include:

- `one_person`
- `two_person`
- `family` 

Each household section contains:

- `people` (number): Number of people per household
- `households` (number): Percentage of this household type occuring
- `division_gender`: Gender division.
    - `male` (number): Percentage of this genders presence in the household
    - `female` (number): Percentage of this genders presence in the household
- `division_age`: Age distribution. Add age grouping properties relevant
    - `age_grouping` (number): Percentage of this ages presence in the household
- `job`: Percentage of adults who work away from the home. Add properties as is relevant
    - `subdivision` (number): Percentage of this subdivision of adults that work away from the home

### Sample File Structure

```toml
[household_type]
    people = <number>       # Number of people per household
    households = <number>   # Percentage of total households

        [household_type.division_gender]
        category_1 = <number>  # First gender category percentage
        category_2 = <number>  # Second gender category percentage

        [household_type.division_age]
        child = <number>   # Children (0-12 years old)
        teen = <number>    # Teens (13-18 years old)
        adult = <number>   # Adults (19-64 years old)
        senior = <number>  # Seniors (> 65 years old)

        [household_type.job]
        category_1 = <number>  # Job percentage for first category
        category_2 = <number>  # Job percentage for second category
```

## Bathroom Tap

This file defines the statistics and parameters for the `BathroomTap` end-use in the simulation. The structure of the file is as follows:

- `classname` (string): The name of the class constructor. Must be `'BathroomTap'`.
- `penetration` (float): The penetration rate of houses with bathroom taps [%].
- `pattern_generator` (string): If a pattern exists, otherwise this field is an empty string.
- `offset` (integer): Defines the time where a second use of the end-use is blocked.
- `frequency`: the frequency distribution of the end-use
    - `distribution` (string): Type of distribution from where the frequency of the end-use will be drawn. Example: `'Poisson'`.
    - `average` (float): Average frequency of end-use.
- `subtype`: types of bathroom tap end-use. Each subtype has its own parameters
    - `subtype.appliance_use`
        - `penetration` (float): Probability of subtype use [%].
        - `temperature` (float): Temperature of the water [°C].
        - `subtype.appliance_use.duration`: Distribution and expected duration of use
            - `distribution` (string): Distribution type. Example: `'Lognormal'`.
            - `average` (string): Average duration of use. Example: `'40 Seconds'`.
        - `subtype.appliance_use.intensity`: Water usage intensity patterns.
            - `distribution` (string): Distribution type. Example: `'Uniform'`.
            - `low` (float): Lower bound of intensity.
            - `high` (float): Upper bound of intensity.
        - `subtype.appliance_use.discharge_intensity`: Discharging water intensity patterns.
            - `distribution` (string): Distribution type. Example: `'Uniform'`.
            - `low` (float): Lower bound of intensity.
            - `high` (float): Upper bound of intensity.


Bathroom tap end uses:

- Washing/Shaving
- Brushing teeth

Below is a template for adding a new end-use subtype

```python
[subtype.custom_use]
    penetration = <percentage>  # Probability of this subtype being used
    temperature = <temperature_value>  # Water temperature

        [subtype.custom_use.duration]
        distribution = '<distribution_type>'
        average = '<time_value>'

        [subtype.custom_use.intensity]
        distribution = '<distribution_type>'
        low = <low_value>
        high = <high_value>

        [subtype.custom_use.discharge_intensity]
        distribution = '<distribution_type>'
        low = <low_value>
        high = <high_value>
```


## Bathtub

This file defines the statistics and parameters for the `Bathtub` end-use in the simulation. The structure of the file is as follows:

- `classname` (string): The name of the class constructor. Must be `'Bathtub'`.
- `pattern_generator` (string): If a pattern exists, otherwise this field is an empty string.
- `temperature` (float): Temperature of used water [°C].
- `offset` (integer): Defines the time where a second use of the end-use is blocked.
- `size` (integer): Size of bathtub filling [L], this parameter is not used.
- `duration` (string): Duration of filling a bathtub depends on the size and the intensity of the filling. Example: `'10 Minutes'`.
- `intensity` (float): Fixed intensity for bathtub filling corresponds to the maximum water flow at full tap opening [L/s].
- `penetration`: Percentage of houses that have a bathtub, depending on the number of people living in a house [%]
    - `1` (integer): Penetration rate for houses with 1 person.
    - `2` (integer): Penetration rate for houses with 2 people.
    - `3` (integer): Penetration rate for houses with 3 people.
    - `4` (integer): Penetration rate for houses with 4 people.
    - `5` (integer): Penetration rate for houses with 5 people.
- `frequency`: distribution of the end-use. Bathtub use is age-dependent, therefore the input parameter of the Poisson distribution changes with age.
    - `distribution` (string): Type of distribution from where the frequency of the end-use will be drawn. Example: `'Poisson'`.
    - `frequency.average`
        - `child` (float): Average frequency for children.
        - `teen` (float): Average frequency for teenagers.
        - `work_ad` (float): Average frequency for working adults
        - `home_ad` (float): Average frequency for home adults.
        - `senior` (float): Average frequency for seniors.
        - `total` (float): Total average frequency.
- `discharge_intensity`
    - `distribution` (string): Distribution type. Example: `'Uniform'`.
    - `low` (float): Lower bound of discharge intensity.
    - `high` (float): Upper bound of discharge intensity.
- `usage_delay`
    - `distribution` (string): Distribution type. Example: `'Uniform'`.
    - `low` (integer): Lower bound of usage delay.
    - `high` (integer): Upper bound of usage delay.


## Dishwasher

This file defines the statistics and parameters for the `Dishwasher` end-use in the simulation. The structure of the file is as follows:

- `classname` (string): The name of the class constructor. Must be `Dishwasher`.
- `offset` (integer): Defines the time where a second use of the end-use is blocked.
- `temperature` (float): Temperature of used water [°C].
- `daily_pattern_input`
    - `x` (string): A string of space-separated values representing the daily pattern.
- `enduse_pattern_input`
    - `intensity` (float): Intensity of the end-use.
    - `runtime` (integer): Runtime of the end-use in seconds.
    - `cycle_times` (array of objects): Array of cycle times with start and end times in seconds.
- `discharge_pattern_input`
    - `discharge_time` (integer): Discharge time in seconds
- `penetration`: Percentage of houses that have a dishwasher, depending on the number of people living in a house [%]
    - `1` (integer): Penetration rate for houses with 1 person.
    - `2` (integer): Penetration rate for houses with 2 people.
    - `3` (integer): Penetration rate for houses with 3 people.
    - `4` (integer): Penetration rate for houses with 4 people.
    - `5` (integer): Penetration rate for houses with 5 people.
- `frequency`: frequency distribution of the end-use.
    - `distribution` (string): Type of distribution from where the frequency of the end-use will be drawn. Example: `'Poisson'`.
    - `frequency.average`
        - `1` (float): Average frequency for houses with 1 person.
        - `2` (float): Average frequency for houses with 2 people.
        - `3` (float): Average frequency for houses with 3 people.
        - `4` (float): Average frequency for houses with 4 people.
        - `5` (float): Average frequency for houses with 5 people.

## KitchenTap

This file defines the statistics and parameters for the `KitchenTap` end-use in the simulation. The structure of the file is as follows:

- `classname` (string): The name of the class constructor. Must be `'KitchenTap'`.
- `penetration` (float): The penetration rate of houses with kitchen taps [%].
- `offset` (integer): Defines the time where a second use of the end-use is blocked.
- `frequency`: frequency distribution of the end-use.
    - `distribution` (string): Type of distribution from where the frequency of the end-use will be drawn. Example: `'Negative_binomial'`.
    - `frequency.average`:
        - `1` (float): Average frequency for houses with 1 person.
        - `2` (float): Average frequency for houses with 2 people.
        - `3` (float): Average frequency for houses with 3 people.
        - `4` (float): Average frequency for houses with 4 people.
        - `5` (float): Average frequency for houses with 5 people.
    - `frequency.sigma`:
        - `1` (float): Sigma value for houses with 1 person.
        - `2` (float): Sigma value for houses with 2 people.
        - `3` (float): Sigma value for houses with 3 people.
        - `4` (float): Sigma value for houses with 4 people.
        - `5` (float): Sigma value for houses with 5 people.
- `subtype`: types of kitchen tap end-use. Each subtype has its own parameters
    - `subtype.appliance_use`
        - `penetration` (float): Probability of subtype use [%].
        - `temperature` (float): Temperature of the water [°C].
        - `subtype.appliance_use.duration`: Distribution and expected duration of use
            - `distribution` (string): Distribution type. Example: `'Lognormal'`.
            - `average` (string): Average duration of use. Example: `'40 Seconds'`.
        - `subtype.appliance_use.intensity`: Water usage intensity patterns.
            - `distribution` (string): Distribution type. Example: `'Uniform'`.
            - `low` (float): Lower bound of intensity.
            - `high` (float): Upper bound of intensity.
        - `subtype.appliance_use.discharge_intensity`: Discharging water intensity patterns.
            - `distribution` (string): Distribution type. Example: `'Uniform'`.
            - `low` (float): Lower bound of intensity.
            - `high` (float): Upper bound of intensity.

Bathroom tap types of uses (`subtype`):

- `consumption`: water for human consumption
- `dishes`: washing the dishes
- `washing_hands`: user washing their hands
- `other`

Below is a template for adding a new end-use subtype

```python
[subtype.custom_use]
    penetration = <percentage>  # Probability of this subtype being used
    temperature = <temperature_value>  # Water temperature

        [subtype.custom_use.duration]
        distribution = '<distribution_type>'
        average = '<time_value>'

        [subtype.custom_use.intensity]
        distribution = '<distribution_type>'
        low = <low_value>
        high = <high_value>

        [subtype.custom_use.discharge_intensity]
        distribution = '<distribution_type>'
        low = <low_value>
        high = <high_value>
```


## OutsideTap

This file defines the statistics and parameters for the `OutsideTap` end-use in the simulation. The structure of the file is as follows:

- `classname` (string): The name of the class constructor. Must be `'OutsideTap'`.
- `penetration` (float): The penetration rate of houses with outside taps [%].
- `offset` (integer): Defines the time where a second use of the end-use is blocked.
- `frequency`: frequency distribution of the end-use.
    - `distribution` (string): Type of distribution from where the frequency of the end-use will be drawn. Example: `'Negative_binomial'`.
    - `average` (float): Average frequency of end-use.
- `subtype`: types of kitchen tap end-use. Each subtype has its own parameters
    - `subtype.appliance_use`
        - `penetration` (float): Probability of subtype use [%].
        - `temperature` (float): Temperature of the water [°C].
        - `subtype.appliance_use.duration`: Distribution and expected duration of use
            - `distribution` (string): Distribution type. Example: `'Lognormal'`.
            - `average` (string): Average duration of use. Example: `'40 Seconds'`.
        - `subtype.appliance_use.intensity`: Water usage intensity patterns.
            - `distribution` (string): Distribution type. Example: `'Uniform'`.
            - `low` (float): Lower bound of intensity.
            - `high` (float): Upper bound of intensity.

!!! Note that this schema does not contain discharge data, as it is assumed the data does not get discharged to the network.

Outside tap types of users (`subtype`):

- `garden`: water used for gardening
- `other`

Below is a template for adding a new end-use subtype

```python
[subtype.custom_use]
    penetration = <percentage>  # Probability of this subtype being used
    temperature = <temperature_value>  # Water temperature

        [subtype.custom_use.duration]
        distribution = '<distribution_type>'
        average = '<time_value>'

        [subtype.custom_use.intensity]
        distribution = '<distribution_type>'
        low = <low_value>
        high = <high_value>

        [subtype.custom_use.discharge_intensity]
        distribution = '<distribution_type>'
        low = <low_value>
        high = <high_value>
```


## Shower

This file defines the statistics and parameters for the `Shower ` end-use in the simulation. The structure of the file is as follows:

- `classname` (string): The name of the class constructor. Must be `'Shower'`.
- `penetration` (float): The penetration rate of houses with showers [%].
- `offset` (integer): Defines the time where a second use of the end-use is blocked.
- `temperature` (integer): Temperature of used water [°C].
- `frequency`: frequency distribution of the end-use. Age dependent.
    - `distribution` (string): Type of distribution from where the frequency of the end-use will be drawn. Example: `'binomial'`.
    - `n` (float): number of showers per day
    - `frequency.p`
        - `age_group` (float): There should be a different entry for each age grouping. Value is the probability of the age taking a shower on a given day.
- `duration`: Age dependent. Duration of a shower for each of the age groups.
    - `distribution` (string): Type of distribution from where the duration of use will be drawn. Example: `'Chisquare'`.
    - `duration.df`
        - `age_group` (float): Duration of shower use by age group.
- `subtype`: types of showers. Each subtype has its own parameters
    - `subtype.appliance_use`
        - `penetration` (float): Probability of subtype use [%].
        - `intensity` (float): The fixed intensity of water flow for this subtype of shower [L/s]
        - `subtype.appliance_use.discharge_intensity`
            - `distribution` (string): Distribution type. Example: `'Uniform'`.
            - `low` (float): Lower bound of intensity.
            - `high` (float): Upper bound of intensity.


Types of Shower (`subtype`):

- `NormalShower`: A normal shower
- `FancyShower`: Combi heater with water saving shower head

```python
[subtype.custom_use]
    penetration = <percentage>  # Probability of this subtype being used
    intensity = <intensity_value>  # Fixed intensity of water flow from the shower type [L/s]

        [subtype.custom_use.discharge_intensity]
        distribution = '<distribution_type>'
        low = <low_value>
        high = <high_value>
```


## Washing Machine

This file defines the statistics and parameters for the `WashingMachine` end-use in the simulation. The structure of the file is as follows:

- `classname` (string): The name of the class constructor. Must be `'WashingMachine'`.
- `offset` (integer): Defines the time where a second use of the end-use is blocked.
- `temperature` (integer): Temperature of used water [°C].
- `daily_pattern_input`: Contains the daily pattern data.
    - `x` (string): A string of space-separated values representing the daily pattern.
- `enduse_pattern_input`: Contains the end-use pattern data.
    - `intensity` (float): Intensity of the end-use.
    - `runtime` (integer): Runtime of the end-use in seconds.
    - `cycle_times` (array of objects): Array of cycle times with start and end times in seconds.
- `discharge_pattern_input`: Contains the discharge pattern data.
    - `discharge_time` (integer): Discharge time in seconds.
- `penetration`: Percentage of houses that have a washing machine, depending on the number of people living in a house [%].
    - `1` (integer): Penetration rate for houses with 1 person.
    - `2` (integer): Penetration rate for houses with 2 people.
    - `3` (integer): Penetration rate for houses with 3 people.
    - `4` (integer): Penetration rate for houses with 4 people.
    - `5` (integer): Penetration rate for houses with 5 people.
- `frequency`: Frequency distribution of the end-use.
    - `distribution` (string): Type of distribution from where the frequency of the end-use will be drawn. Example: `'Poisson'`.
    - `frequency.average`: Average frequency of end-use.
        - `1` (float): Average frequency for houses with 1 person.
        - `2` (float): Average frequency for houses with 2 people.
        - `3` (float): Average frequency for houses with 3 people.
        - `4` (float): Average frequency for houses with 4 people.
        - `5` (float): Average frequency for houses with 5 people.


## WC

# WC Configuration

This file defines the statistics and parameters for the `Wc` (toilet) end-use in the simulation. The structure of the file is as follows:

- `classname` (string): The name of the class constructor. Must be `'Wc'`.
- `penetration` (integer): The penetration rate of houses with a WC [%].
- `offset` (integer): Defines the time where a second use of the end-use is blocked.
- `temperature` (integer): Temperature of used water [°C].
- `prob_flush_interuption` (integer): Probability that a water savings option of a toilet will be used [%].
- `intensity` (float): Fixed intensity for toilet flush corresponds to the pipe size to fill the cistern [L/s].
- `discharge_intensity` (float): Discharge intensity [L/s].
- `frequency`: Contains the frequency distribution data.
    - `distribution` (string): Type of distribution from where the frequency of the end-use will be drawn. Example: `'Poisson'`.
    - `frequency.average`: Average frequency of use, dependent on age and gender.
        - `child`: Average frequency for children.
            - `male` (float): Average frequency for male children [day^(-1)].
            - `female` (float): Average frequency for female children [day^(-1)].
            - `total` (float): Total average frequency for children [day^(-1)].
        - `teen`: Average frequency for teenagers.
            - `male` (float): Average frequency for male teenagers [day^(-1)].
            - `female` (float): Average frequency for female teenagers [day^(-1)].
            - `total` (float): Total average frequency for teenagers [day^(-1)].
        - `work_ad`: Average frequency for working adults.
            - `male` (float): Average frequency for male working adults [day^(-1)].
            - `female` (float): Average frequency for female working adults [day^(-1)].
            - `total` (float): Total average frequency for working adults [day^(-1)].
        - `home_ad`: Average frequency for home adults.
            - `male` (float): Average frequency for male home adults [day^(-1)].
            - `female` (float): Average frequency for female home adults [day^(-1)].
            - `total` (float): Total average frequency for home adults [day^(-1)].
        - `senior`: Average frequency for seniors.
            - `male` (float): Average frequency for male seniors [day^(-1)].
            - `female` (float): Average frequency for female seniors [day^(-1)].
            - `total` (float): Total average frequency for seniors [day^(-1)].
        - `total`: Overall average frequency.
            - `male` (float): Overall average frequency for males [day^(-1)].
            - `female` (float): Overall average frequency for females [day^(-1)].
            - `total` (float): Overall average frequency [day^(-1)].
- `subtype`: Different subtypes of toilets used to populate a household.
    - `subtype.appliance_use`: A type of toilet.
        - `penetration` (float): Penetration rate within end-use [%].
        - `flush_interuption` (boolean): Presence of water savings option.
        - `cistern_size` (integer): Size of cistern of toilet [L].
        - `duration` (string): Duration of water use corresponds to the filling time of the cistern.

Types of Toilets (`subtype`):

- `WcNormal`: A normal toilet.
- `WcNormalSave`: A normal toilet with a water savings option.
- `WcNew`: A new model toilet.
- `WcNewSave`: A new model toilet with a water savings option.

Template for adding a subtype:

```python
[subtype.custom_use]
    penetration = <percentage>  # Probability of this subtype being used
    flush_interuption = <boolean_value>  # presence of water savings option (true/false)
    cistern_size = <cistern_size_value> # [L]
    duration = '<duration_time>'
```
