# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
