# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- CHANGELOD.md

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
