# CAM Code Searcher

## Purpose

Search CAM codebase for business logic, formulas, and validation rules that UI exploration cannot reveal.

## What It Does

1. Searches i18n files for business explanations and data delays
2. Searches frontend components for UI logic and field options
3. Searches backend code for calculations and validation rules
4. Extracts domain knowledge from code
5. Returns structured findings with recommendations

## Dependencies

- Access to: `/Users/jessiecao/src/cam/` (CAM codebase)
- Specifically:
  - `/Users/jessiecao/src/cam/front/src/locales/source/en.json` (i18n)
  - `/Users/jessiecao/src/cam/front/v3/components/` (frontend)
  - `/Users/jessiecao/src/cam/front/v3/views/` (frontend)
  - Backend code (Python/Go files)

## Returns

- Business rules and explanations from i18n
- UI component options and enum values
- Calculation formulas and validation logic
- API endpoints and constraints
- Recommendations for incorporating findings into docs

## Usage

This sub-skill is called for Medium/High complexity features to extract domain knowledge that UI exploration cannot reveal.
