# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.1] - 2022-03-28

### Added

- Use multiprocessing for database operations.
- Add '--version' cli key to print version number.

### Fixed

- Logging of unsupported content-type

## [0.2.0] - 2022-03-28

### Added

- Multiprocess data parsing with [ray](https://www.ray.io/) framework.
- Settings option for number of processes to spawn. Default is 1.
- Initial unit tests for faddr-db cli entry point.

### Changed

- Improved some logging messages.

### Removed

- Disable python 3.10 support for now, as [ray doesn't support it yet](https://github.com/ray-project/ray/issues/19116).

## [0.1.0] - 2022-03-26

### Added

- Settings option "database.revisions" to specify number of revisions to keep. Older revisions will be deleted.

### Changed

- Separated parsing into function.

### Fixed

- Renamed 'enabled' to 'is_enabled' in rancid repo dir parser.

### Removed

- Removed 'router_db_raw_string' property as it was user for debug only

## [0.0.12] - 2022-03-24

### Changed

- Rename default_mapping to mapping in settings.rancid

### Fixed

- Convert device hostname to lowercase in rancid config path
- In ttp templates mark regex as regex with 'r' to silence deprecation warnings

## [0.0.11] - 2022-03-20

### Added

- Debug logging in database submodule
- Detect primary/preferred and vrrp addresses in juniper-junos ttp template

### Changed

- Updated README.md

### Fixed

- Search query network list compilation

## [0.0.10] - 2022-03-17

### Changed

- Combine networks into list and use it in a single query

### Fixed

- Raise exception in Parser class if loaded config file is empty
- Only parse config file if it's enabled in router.db
- Made working IP space MASK regex
- Detect and store only digits as s_vlan and c_vlan

## [0.0.9] - 2022-03-15

### Added

- Sort ip_address search results by device name, than by interface name, than by ip_address.

### Changed

- RancidDir class now detects path's level automatically and can be created with path's level "dir", "group" and "repo".
- Made outbox table box edges square.

### Fixed

- Fix RANCID-CONTENT-TYPE detection for 3rd-party rancid scripts.
- Add one space padding for result table for easy double-click select.
- Add 'PermissionError' exception for 'RancidDir' folder scan

### Removed

- Removed 'rancid.dirs.kind' field from settings and test fixtures.

## [0.0.8] - 2022-03-13

### Added

- Huawei VRP configuration parsing.
- Huawei VRP configuration gathered by rancid (hwlogin/hwrancid) and other related test fixtures.
- Detect 'shutdown' on interface for all profiles. Record it as boolean 'is_disabled'

## [0.0.7] - 2022-03-10

### Added

- Cisco IOS-XR configuration parsing.
- Some INFO level logging for faddr-db.

### Changed

- Compact output table style .
- Debug short key in CLI changes from "-d" to "-D".

### Fixed

- Disabled text wrapping for output table in "faddr" for all columns except "Description".

## [0.0.6] - 2022-03-08

### Added

- Juniper Junos configuration parsing.

### Changed

- Parser's output structure format. "interfaces" now is dict instean of list.
- ipv4 and ipv6 combined into single ip structure/QLALchemy class.

## [0.0.5] - 2022-03-07

### Added

- Working Database class
- 'faddr' cli entry point for data querying
- Print result as pretty table with rich module

### Changed

- "dir" and "file" params in settings.database renamed to "path" and "name"
- Switched from TinyDB to SQLAlchemy as DB engine

### Removed

- Deleted dataclasses.py with unused pydantic dataclasses

## [0.0.4] - 2022-02-08

### Added

- ttp package for configuration files parsing
- rich module for pretty printing
- Parser class to work with ttp
- Unit tests for Parser class
- cisco-ios ttp template parses basic data: interface, ipv4, ACL, vrf, admin status

### Fixed

- Set rancid's custom content-type suffix as "-faddr" in all fixtures

## [0.0.3] - 2022-02-01

### Added

- CHANGELOG.md
- poetry module as dev dependency
- tox-poetry module for better tox integration
- python 3.10 profile in tox config
- coverage as explicit dev dependency
- unit tests for faddr.rancid and faddr.settings

### Changed

- Rewritten RancidDir class. Now it supports both rancid root dir and raw repo as input
- Rewritten FaddrSettings class. Settings now use pydantic's BaseConfig.
- Updated .gitignore

### Fixed

- Pylint warnings
- Prospector warnings
- yamllint warnings in fixtures

## [0.0.3] - 2021-12-31

### Added

- Loading config from file and parsing CMD and ENV

### Changed

- Switched from dataclass to pydantic
- Updated pyenv python versions

## [0.0.2] - 2021-10-26

### Added

- Enabled logging with loguru
- Control logging level via enviroment variable FADDR_DEBUG

### Changed

- Simplified CiscoIOSDevice class

### Fixed

- Added exception handling for unreadable directories inside rancid base dir

## [0.0.1] - 2021-10-24

### Added

- Base structure of a project
- CLI tool to generate DB
- Using TyniDB for now
- Parsing Cisco IOS configuration for basic ip address and interface related data works
- Unit tests with pytest
- Created README.md
- GitHub Automation runs unit test on variable versions of OS and python
- Ready for publishing in PyPI
