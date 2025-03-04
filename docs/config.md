# Config

The main functionality of pySimdeum is to build and populate houses with users and water end-use devices according to region (e.g. country, city, state) specific statistics as well as to simulate water usage and demand stochastically based on these statistics. To do this we have create a set of `.toml` config files that contain region specific statistics. In the codebase we have statistics for the NL and the UK, users can choose either set of statistics or provide a config set of their own.

## Configuring Region Statistics

PySimdeum allows the user to select the region specific statistics in order to build and populate houses, and to stochastically model water demand according to their needs. As a default, when simulating a house and users, pysimduem will use the NL statistics, unless directed otherwise. Users can either:
1. Select country specific statistics available in the repo, the UK or NL
2. Provide a custom directory path containing `.toml` statistics files, following the structure provided in [Config Schema](schema.md)


## File Structure

In the codebase there are regional specific statistics for the UK and NL. 

``` /pysimdeum/data/ ├── Region/ │ ├── diurnal_patterns.toml │ ├── household_statistics.toml │ ├── end_uses/ │ ├── BathroomTap.toml │ ├── Bathtub.toml │ ├── Dishwasher.toml │ ├── KitchenTap.toml │ ├── OutsideTap.toml │ ├── Shower.toml │ ├── WashingMachine.toml │ └── WC.toml ``` 

### Dirunal Patterns

The `dirunal_patterns.toml` file contains statistical data for modeling water demand patterns based on different demographic groups and their daily activities. The demographics included are child, teen, adult working outside the home, adult staying inside the home and senior. It also contains total and weekend activity. Each activity within a section is given a normal distribution `dist = 'norm'`. This configuration allows for the simulation of realistic daily water demand patterns based on the specified demographic groups and their activities.

### Household Statistics

The `household_statistics.toml` contains statistical data for modeling household compositions and their characteristics based on different household types. The file is organized into several sections, each representing a different type of household. Each section contains sub-sections for specific demographic and employment characteristics. This configuration allows for the simulation of realistic household compositions and their characteristics, which can be used to model water demand patterns based on different household types.

### End Uses

The `end_uses` folder contains `.toml` files for each household appliance that is simulated. The files contains statistical data for modeling the usage patterns of the related appliance. These files collectively provide a comprehensive model of household water usage patterns. They are  organized into several sections, each representing different aspects of the appliance usage. These sections include general information about the appliance, frequency of use, and subtypes of end-uses.