---
name: cam-code-searcher
description: Search CAM codebase for business logic, formulas, and validation rules
version: 1.0.0
---

# CAM Code Searcher

This sub-skill searches the CAM codebase to extract business logic, formulas, and validation rules that UI exploration cannot reveal.

## Why Search Code

**Proactively search the CAM codebase** to discover:
- Business rule explanations (from i18n files)
- Data delay information and warnings
- Calculation formulas and validation logic
- Hidden configuration options
- Field dependencies and conditional behavior

## Search Priority Order (Highest Value First)

### 1. i18n Files (HIGHEST PRIORITY)

**Why search first**: Contains business explanations, data delays, warnings, and status meanings that UI exploration cannot reveal.

**Location**: `/Users/jessiecao/src/cam/front/src/locales/source/en.json`

**Search patterns**:
```bash
# Search for feature-specific keys
grep -i "routine_report" /Users/jessiecao/src/cam/front/src/locales/source/en.json
grep -i "backtrack" /Users/jessiecao/src/cam/front/src/locales/source/en.json
grep -i "nav_calculation" /Users/jessiecao/src/cam/front/src/locales/source/en.json

# Search for data delay explanations
grep -i "delay\|hours\|corrected" /Users/jessiecao/src/cam/front/src/locales/source/en.json

# Search for status meanings
grep -i "status\|pending\|completed\|failed" /Users/jessiecao/src/cam/front/src/locales/source/en.json
```

**What to extract**:
- Business rule explanations (e.g., "Record capture delays up to 4 hours due to using REST APIs")
- Data delay information (e.g., "Snapshot data corrected within 8 hours")
- Status meanings and lifecycle descriptions
- Warning messages and important notes
- Tooltip text and help descriptions

### 2. Frontend Components

**Location**:
- For UI components: `/Users/jessiecao/src/cam/front/v3/components/`
- For page-specific logic: `/Users/jessiecao/src/cam/front/v3/views/`
- For shared utilities: `/Users/jessiecao/src/cam/front/v3/utils/`

**Search patterns**:
```bash
# Search for component by feature name
find /Users/jessiecao/src/cam/front/v3/components -name "*RoutineReport*" -o -name "*routineReport*"
find /Users/jessiecao/src/cam/front/v3/views -name "*routine-report*"

# Search for enum values and constants
grep -r "CUT_OFF_TIME_OPTS\|FREQUENCY_OPTIONS\|STATUS_ENUM" /Users/jessiecao/src/cam/front/v3/
```

**What to extract**:
- Component props and configuration options
- Enum values and constants (dropdown options, status values)
- Conditional logic that reveals hidden features
- UI labels and button text from the code
- Field validation rules

### 3. Backend Code

**Location**: `/Users/jessiecao/src/cam/` (search for route definitions, controllers, business logic)

**Search patterns**:
```bash
# Search for API endpoints
grep -r "routine_report\|routineReport" /Users/jessiecao/src/cam/ --include="*.py" --include="*.go"

# Search for calculation logic
grep -r "calculate_nav\|backtrack_equity" /Users/jessiecao/src/cam/ --include="*.py" --include="*.go"

# Search for validation rules
grep -r "validate\|constraint\|limit" /Users/jessiecao/src/cam/ --include="*.py" --include="*.go"
```

**What to extract**:
- API endpoint paths and parameters
- Calculation formulas and business rules (e.g., NAV calculation, fee accrual)
- Data validation constraints and limits
- Error handling and edge cases
- Database schema fields and relationships

## Real-World Example: Routine Report Feature

**Step 1: Search i18n files first**
```bash
grep -i "routine_report" /Users/jessiecao/src/cam/front/src/locales/source/en.json
```
**Found**:
- `routine_report_reason1`: "Record capture delays...up to 4 hours due to using REST APIs"
- `routine_report_reason2`: "Snapshot data...corrected within 8 hours"
- `routine_report_title1`: "Data Delays for REST API Records"

**Step 2: Search frontend components**
```bash
find /Users/jessiecao/src/cam/front/v3/components -name "*RoutineReport*"
```
**Found**: Field options, conditional logic for Contents field

**Step 3: Search backend code**
```bash
grep -r "routine_report" /Users/jessiecao/src/cam/ --include="*.py"
```
**Found**: API endpoints, validation rules, scheduling logic

## When Code Location is Unclear

If you can't find the relevant code, ask the PM:
"Can you point me to the frontend and backend code for this feature? It would help me discover any undocumented options, calculation logic, or edge cases."

## Benefits

- ✅ Discovers business rules not visible in UI (e.g., data delay explanations from i18n)
- ✅ Finds domain knowledge that UI exploration cannot reveal
- ✅ Verifies exact UI labels from source code
- ✅ Finds configuration options and variants
- ✅ Catches edge cases and conditional behavior
- ✅ Documents calculation formulas and business logic from backend
- ✅ Identifies API constraints and validation rules

## Search Techniques

### Using Grep
```bash
# Case-insensitive search
grep -i "pattern" file.json

# Recursive search in directory
grep -r "pattern" /path/to/dir/ --include="*.py"

# Multiple patterns (OR)
grep -E "pattern1|pattern2" file.json

# Context lines (show surrounding lines)
grep -C 3 "pattern" file.json
```

### Using Find
```bash
# Find files by name pattern
find /path/to/dir -name "*pattern*"

# Find files with multiple patterns (OR)
find /path/to/dir -name "*pattern1*" -o -name "*pattern2*"

# Find files by extension
find /path/to/dir -name "*.py"
```

## Output Format

Return the extracted information in this format:

```
Code Search Results for [Feature Name]:

### i18n Findings:
- [Key business rules and explanations]
- [Data delay information]
- [Warning messages]

### Frontend Findings:
- [Component props and options]
- [Enum values and constants]
- [Conditional logic]

### Backend Findings:
- [API endpoints]
- [Calculation formulas]
- [Validation rules]

### Recommendations:
- [How to incorporate findings into documentation]
- [Sections that need domain knowledge from code]
```
