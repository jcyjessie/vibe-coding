# Changelog

## [2.0.0] - 2026-03-03

### Changed
- Refactored state comparison to use baseline instead of chain comparison
- Improved dropdown options collection to capture all available options
- Replaced fixed sleep delays with proper wait conditions
- Enhanced error handling with specific exception types
- Implemented stratified sampling for dropdown option exploration

### Fixed
- False negatives when fields return to baseline state
- Missing dropdown options in captured state
- Race conditions from fixed timeout delays
- Silent failures from bare except blocks
- Poor coverage from sequential sampling

## [1.0.0] - 2026-03-02

### Added
- Initial field dependency exploration functionality
