# Config

The main functionality of pySimdeum is to build and populate houses with users and water end-use devices according to region (e.g. country, city, state) specific statistics as well as to simulate water usage and demand stochastically based on these statistics. To do this, the project uses a set of `.toml` config files that contain region specific statistics, stored in the `pysimdeum/data/` folder. Under the data folder default statistics are provided for the NL and UK. Alternatively users and copy this structure and provide config files of their own.

## Using Config Files

As a default pysimduem will use the NL statistics, with an optional flag to switch to UK data provided in the repo. 

Users can either:
1. Select country specific statistics available in the repo, the UK or NL
2. Provide a custom directory path containing `.toml` statistics files, following the structure provided in [Config Schema](schema.md)

To use predefined `.toml` files, specify the country code when initializing the system, or ignore the `country` flag to use default NL data.

```python
house = built_house(house_type="family", country="UK")
```

## Creating Custom Configurations

To use your own statistics, you can provide a custom directory path instead of a country code:

```python
house = built_house(house_type="family", country="/my/custom/config/")
```

The custom directory must contain `.toml` files structured as follows:
``` 
/my/custom/config/ 
└── Region/ 
    ├── diurnal_patterns.toml
    ├── household_statistics.toml 
    └── end_uses/
        ├── BathroomTap.toml
        ├── Bathtub.toml
        ├── Dishwasher.toml
        ├── KitchenTap.toml
        ├── OutsideTap.toml
        ├── Shower.toml
        ├── WashingMachine.toml
        └── WC.toml 
``` 

## Description of Files

### Dirunal Patterns

The `dirunal_patterns.toml` file contains statistical data for modeling water demand patterns based on different demographic groups and their daily activities. 
The demographics included are: 
- child
- teen 
- adult working outside the home
- adult staying inside the home
- senior

It also contains total and weekend activity. Each activity within a section is given a normal distribution `dist = 'norm'`. This configuration allows for the simulation of realistic daily water demand patterns based on the specified demographic groups and their activities.

### Household Statistics

The `household_statistics.toml` contains statistical data for modeling household compositions and their characteristics based on different household types. The file is organised into several sections, each representing a different type of household. Each section contains sub-sections for specific demographic and employment characteristics. This configuration allows for the simulation of realistic household compositions and their characteristics, which can be used to model water demand patterns based on different household types.

### End Uses

The `end_uses` folder contain `.toml` files for each household appliance that is simulated. The files contains statistical data for modeling the usage patterns of the related appliance. These files collectively provide a comprehensive model of household water usage patterns. They are organised into several sections, each representing different aspects of the appliance usage. These sections include general information about the appliance, frequency of use, and subtypes of end-uses.