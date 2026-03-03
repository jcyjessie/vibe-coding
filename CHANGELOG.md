# CAM User Guide Writer Skill - Changelog

## [3.0.0] - 2026-03-03

### Added
- State tracking module to prevent duplicate captures
- Selector abstraction layer with priority fallback system
- Retry mechanism with exponential backoff
- Headless mode for CI/CD integration
- Comprehensive error handling and logging

### Changed
- Refactored from click-driven to state-driven architecture
- Replaced text-based selectors with robust selector engine
- Improved login validation logic

### Fixed
- URL inconsistency between docstring and default argument
- Swallowed exceptions now properly logged
- Login success validation now checks for error messages

## Version 2.1 - 2026-03-03

### Improvements Based on ChatGPT Feedback

This update implements three priority improvements suggested by ChatGPT to enhance output stability and workflow clarity.

#### 1. Added Self-Check Phase (Priority 1 - Highest Impact)

**Problem**: Documents were sometimes delivered with formatting errors, missing required sections, or incorrect frontmatter.

**Solution**: Added comprehensive Step 7 "Self-check before delivery" with validation checklist:
- **Frontmatter Validation**: Verify all required fields, permalink format, order value, date format
- **Structure Validation**: Check for numbered top-level headings, verify document type matches feature
- **Content Completeness**: Ensure Example section (for config features), Use Cases (for complex features), support contact (for beta)
- **Language and Formatting**: No Chinese characters, proper bolding, correct navigation paths, bullet list format
- **Screenshot Coverage**: Every section has screenshots, complex interactions have multiple screenshots

This dramatically improves output stability by catching common errors before delivery.

#### 2. Enhanced Task Decomposition (Priority 2)

**Problem**: Document type selection was implicit, making it unclear which template to use.

**Solution**: Upgraded Step 3 "Identify the document type and select template" with explicit analysis:
- Clear criteria for each document type (Setup/Feature Manual/FAQ)
- Examples of when to use each type
- Explicit template selection based on feature characteristics

This makes the workflow more systematic and reduces ambiguity.

#### 3. Automated Order Number Suggestion (Priority 3)

**Problem**: Choosing the `order` value required manual inspection of existing files.

**Solution**: Added Step 2.5 "Determine file order number" with automated workflow:
- List existing files using `ls` command
- Analyze order pattern in similar documents
- Suggest order value with reasoning
- Wait for PM confirmation

This moves toward true AI engineering by automating file system analysis.

### Workflow Summary (Updated)

The complete workflow now follows this structure:

1. **Step 0**: Assess complexity and choose approach
2. **Step 1**: Understand the feature (via browser automation, materials, or Q&A)
3. **Step 1.5**: Search related code (for Medium/High complexity)
4. **Step 2**: Check existing docs for context
5. **Step 2.5**: Determine file order number (NEW)
6. **Step 3**: Identify document type and select template (ENHANCED)
7. **Step 4**: Draft structure and wait for PM approval
8. **Step 5**: Write content
9. **Step 6**: Mark screenshot placeholders
10. **Step 7**: Self-check before delivery (NEW)

### Impact

These improvements elevate the skill from "generates documentation" to "generates validated, correctly-formatted documentation with systematic quality control."

## Version 2.0 - 2026-03-03

### Major Improvements

This update is based on real-world usage experience and addresses key quality issues discovered during documentation creation.

### 1. Duplicate Documentation Prevention (Step 2)

**Problem**: Created duplicate documentation (34.home-components-config.md) when comprehensive documentation (35.home-manual.md) already existed.

**Solution**: Added mandatory duplicate check before creating new documents:
- Must search existing docs in `docs/user-guide/` for similar features
- Must read potentially overlapping documents to verify no duplication
- If duplicate exists, ask PM whether to update existing doc, merge content, or clarify distinction

### 2. Use Cases Now Mandatory for Complex Features

**Problem**: Documentation lacked practical application examples showing real-world value.

**Solution**:
- Made "Use Cases" section MANDATORY for complex features in Feature Manual Structure
- Requires 2-3 detailed scenarios showing how different user roles use the feature
- Each use case must describe user role, goal, workflow, and outcomes
- Added reference to 35.home-manual.md as exemplar (Portfolio Manager for Funding-Rate Arbitrage, LongShort Strategy, Middle/Back Office Users)

### 3. Complete Screenshot Coverage Requirements

**Problem**: Documentation had incomplete visual guidance, missing screenshots for menu interactions and dialog flows.

**Solution**: Enhanced screenshot requirements:
- Every major workflow step must have at least one screenshot
- Complex interactions require multiple screenshots showing:
  - Trigger action (e.g., clicking menu button)
  - Opened state (menu/dialog visible)
  - Result state (after action completed)
- Added specific example: Tab sharing workflow needs 4 screenshots (menu button → opened menu → Share dialog → shared tab indicator)
- Emphasized use of automated browser capture tools for complete coverage

### 4. Enhanced Browser Automation Script

**Problem**: Original script captured menu buttons but didn't explore menu items, missing critical workflow documentation.

**Solution**: Updated auto_browse_cam_v2.py with menu exploration:
- After clicking a menu button, automatically clicks each menu item (Rename, Duplicate, Share, Delete, etc.)
- Captures resulting dialogs and actions for each menu item
- Re-opens menu between items to explore all options
- Updated skill documentation to reference `auto_browse_cam_v2.py` (not old `auto_browse_cam.py`)

### 5. New Documentation Quality Standards Section

**Problem**: No clear quality checklist for finalizing documentation.

**Solution**: Added "Documentation Quality Standards" section with 5 checkpoints:
1. No Duplicate Documentation - verify no existing doc covers same feature
2. Complete Screenshot Coverage - every workflow step visually documented
3. Use Cases Included - 2-3 real-world scenarios for complex features
4. Comprehensive Workflow Documentation - primary + reverse actions + all options
5. Accurate UI Labels - all field names, buttons, menus match actual product

### 6. Enhanced Step 5 Writing Requirements

**Problem**: Unclear when use cases are required and how many screenshots are needed.

**Solution**:
- Explicitly marked use cases as MANDATORY for complex features
- Required screenshots for each major action in step-by-step content
- Emphasized multiple screenshots for complex interactions (menu opening, dialog appearing, result state)
- Added reference to 35.home-manual.md "Overall Use Case" section as comprehensive example

## Technical Changes

### Modified Files
- `skill.md` - Main skill documentation with all improvements above
- `scripts/auto_browse_cam_v2.py` - Enhanced with `_explore_menu_items()` method

### New Sections in skill.md
- "Documentation Quality Standards" (after "Content Completeness Requirements")
- Enhanced "Screenshots and Images" section with detailed requirements
- Updated "Step 2: Check existing docs" with duplicate detection mandate
- Updated "Option A: Live browser automation" with v2 script capabilities

## Migration Notes

For existing documentation:
- Review existing docs against new quality standards
- Add use cases to complex feature documentation that lacks them
- Supplement incomplete screenshot coverage using auto_browse_cam_v2.py
- Check for duplicate documentation and consolidate where appropriate

## Example Reference

See 35.home-manual.md as the gold standard for:
- Comprehensive use cases (3 detailed scenarios for different user roles)
- Complete screenshot coverage (20 screenshots covering all workflows)
- Clear structure with table of contents
- Real-world examples with specific parameter values
