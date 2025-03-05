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
people = number       # Number of people per household
households = number   # Percentage of total households

    [household_type.division_gender]
    category_1 = number  # First gender category percentage
    category_2 = number  # Second gender category percentage

    [household_type.division_age]
    child = number   # Children (0-12 years old)
    teen = number    # Teens (13-18 years old)
    adult = number   # Adults (19-64 years old)
    senior = number  # Seniors (> 65 years old)

    [household_type.job]
    category_1 = number  # Job percentage for first category
    category_2 = number  # Job percentage for second category
```

## Bathroom Tap

## Bathtub

## Dishwasher

## KitchenTap

## OutsideTap

## Shower

## Washing Machine

## WC