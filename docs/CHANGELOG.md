<!---
Changelog headings can be any of:

Added: for new features.
Changed: for changes in existing functionality.
Deprecated: for soon-to-be removed features.
Removed: for now removed features.
Fixed: for any bug fixes.
Security: in case of vulnerabilities.

Release headings should be of the form:
## [X.Y.Z] - YEAR-MONTH-DAY
-->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- `Washing Machine` and `Dishwasher` enduse pattern generalised [#53](https://github.com/KWR-Water/pysimdeum/pull/53)
-  UK data and ability to change between `NL` and `UK` statistics [#73](https://github.com/KWR-Water/pysimdeum/pull/73)
- `discharge_events` bug fix [#88](https://github.com/KWR-Water/pysimdeum/pull/88)
- `KTap` enduse pattern generalised [#90](https://github.com/KWR-Water/pysimdeum/pull/90)
- `Shower` enduse discharge flow pattern switch from uniform distribution to fixed value [#93](https://github.com/KWR-Water/pysimdeum/pull/93)


### Added

- Optionally run discharge simulations linked to simulated consumptions flows [#39](https://github.com/KWR-Water/pysimdeum/pull/39)   [#45](https://github.com/KWR-Water/pysimdeum/pull/45)   [#46](https://github.com/KWR-Water/pysimdeum/pull/46)   [#48](https://github.com/KWR-Water/pysimdeum/pull/48)   [#58](https://github.com/KWR-Water/pysimdeum/pull/58)   
- Readthedocs documentation available [here](https://pysimdeum.readthedocs.io/en/latest/) [#52](https://github.com/KWR-Water/pysimdeum/pull/52)
- Spillover feature for `WashingMachine` and `Dishwasher` [#54](https://github.com/KWR-Water/pysimdeum/pull/54)
- Sample start time protection [#59](https://github.com/KWR-Water/pysimdeum/pull/59)
- Wastewater nutrient concentration [#72](https://github.com/KWR-Water/pysimdeum/pull/72)   [#81](https://github.com/KWR-Water/pysimdeum/pull/81)
- Wastewater temperature [#83](https://github.com/KWR-Water/pysimdeum/pull/83)
- `Population` class for multi-house simulations and population fitting with spatial components [#85](https://github.com/KWR-Water/pysimdeum/pull/85)
- Jupyter notebook examples [#86](https://github.com/KWR-Water/pysimdeum/pull/86)
- Infoworks wastewater profile write formatting [#91](https://github.com/KWR-Water/pysimdeum/pull/91)


## [v0.1.0]

## Initial release

This is the first release and support >=Python 3.8, please check documentation for the usage guide