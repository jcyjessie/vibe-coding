# Archive Directory

This directory contains historical documentation and scripts from previous versions of the cam-user-guide-writer skill.

## v1-history/

Contains documentation from the v1 development process:

- **BROWSER_AUTOMATION_UPGRADE.md** - Documentation of the browser automation upgrade process from interactive to automatic mode
- **OPTIMIZATION_SUMMARY.md** - Summary of optimizations applied during v1 development
- **SKILL_IMPROVEMENTS_APPLIED.md** - Record of skill improvements based on routine-report documentation analysis

## v1-scripts/

Contains deprecated v1 browser automation scripts that have been superseded by v2 versions:

- **auto_browse_cam.py** (13K) - Original automatic browser capture script
  - Superseded by: `auto_browse_cam_v2.py` (with enhanced menu exploration)

- **auto_browse_cam_current_tab.py** (13K) - Version that connects to currently active Chrome tab
  - Special-purpose script, not part of main workflow

- **auto_browse_cam_persistent.py** (14K) - Version using persistent browser context
  - Experimental approach, superseded by v2's storageState authentication

- **auto_login_cam.py** (4.5K) - Original login script
  - Superseded by: `auto_login_cam_v2.py`

### Why These Scripts Were Archived

The v2 scripts offer significant improvements:
- **Better authentication**: Uses Playwright's storageState pattern (similar to Kintsugi project)
- **Enhanced menu exploration**: Automatically clicks menu items and captures resulting dialogs
- **More reliable**: Better error handling and state management
- **Actively maintained**: Referenced in current skill.md documentation

## Active Scripts (in scripts/ directory)

Current production scripts:
- `auto_browse_cam_v3.py` - Main automatic browser capture with state tracking and retry mechanism
- `auto_login_cam_v3.py` - Authentication state management with headless mode support
- `browse_cam.py` - Interactive mode (manual operation with capture)
- `explore_field_dependencies.py` - Field dependency analysis tool

## v2-scripts/ (Superseded by V3 - March 2026)

V2 scripts archived after V3 release with state-driven architecture.

**Superseded by:**
- `auto_login_cam_v3.py` - Adds headless mode, retry, improved validation
- `auto_browse_cam_v3.py` - Adds state tracking, selector engine, error handling

**Why archived:**
- Click-driven architecture prone to duplicates
- Text-based selectors fragile to i18n changes
- Bare exception handling swallowed errors
- No CI/CD support (fixed headless=False)

These files are preserved for historical reference but are no longer actively maintained. The current skill documentation is in the parent directory:

- `skill.md` - Main skill documentation (v2.1)
- `CHANGELOG.md` - Version history with all improvements

## Why Archive?

These documents and scripts were moved to the archive to:
1. Keep the main directory clean and focused on current tools
2. Preserve historical context for future reference
3. Avoid confusion between old implementations and current best practices
4. Maintain a clear upgrade path from v1 to v2

## Date Archived

- Documentation: 2026-03-03
- Scripts: 2026-03-03
