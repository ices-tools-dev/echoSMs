# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added this changelog

### Changed

- Fix typos and grammar in documentation
- Give the datastore schema browser more window width in the documentation
- All documentation gets the datastore URL from one source now (it is no longer hard-coded in the documentation)

### Deprecated

### Remvoed

### Fixed

- Resolve errors in example Python code in the documentation and the Viewer program

### Security

## [0.23.0] - 2026-07-09

### Added

- Add a license property to the datastore schema
- Add geometric shape to datastore schema (unions of spheroids and bent cylinders)

### Changed

- Update documentation
- Update descriptions in datastore schema
- Prototype datastore server address is now available as `echosms.DATASTORE_URI`
- Sdjust some datastore schema property values to match relevant ICES vocabularies
 
### Fixed

- Miscellaneous bug fixes

## [0.22.0] - 2026-05-25

### Added

- Added utility function to get the echoSMs datastore schema

## [0.21.1] - 2026-05-25

### Changed

- Make validate-toml more robust

## [0.21.0] - 2026-05-24

### Added

- Added function to simplify getting WoRMS species data
- Added a validate-toml script to the package

### Changed

- Datastore schema now allows an aphia_id of 0 to represent specimens that don't have a species
- Documentation updates and corrections

## [0.20.2] - 2026-05-22

### Fixed

- Fix a bug that occurs when outline shapes without sound speed and density are converted to a KRMorganism

## [0.20.1] - 2026-05-19

### Added

- Added matplotlib to dependencies

## [0.20.0] - 2026-05-17

### Added
- Add an implementation of the boundary element method for pressure release surfaces

### Changed

- Upgrade urllib3 to resolve a security alert
- More user-visible code has type annotations
- Minor rearrangement of API documentation