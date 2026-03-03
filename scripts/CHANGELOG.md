# Changelog

## [3.0.0] - 2026-03-04

### Added
- Structured state change types with semantic classification (URL change, dialog opened/closed, field added/removed, options changed, validation error)
- Global exploration budget control with hard limits (max steps, states, time, retries)
- Login strong signal validation with home selector and API verification strategies
- ExplorationBudget class for preventing exploration time explosion
- LoginValidator class for robust login verification
- Integration tests for v3 features

### Changed
- `_compare_states()` now returns semantic change types instead of generic "appeared/modified/disappeared"
- Login verification now uses multiple validation strategies (selector + API)
- Exploration loop now checks budget constraints before each interaction

### Improved
- Better interpretability of state changes for LLM-based documentation generation
- More predictable execution time with hard budget limits
- More reliable login verification with fallback strategies

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
