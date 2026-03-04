# PHASE 1 Complete: BrowserFactory

## What Changed

Created shared `BrowserFactory` module that unifies browser setup logic across all three scripts.

## Files Modified

### New Files
- `scripts/core/__init__.py` - Package marker
- `scripts/core/browser_factory.py` - Unified browser setup with `create_page()` function

### Modified Files
- `scripts/auto_login_cam_v3.py`
  - Removed manual playwright/browser/context management (lines 199-208)
  - Now uses `create_page()` from BrowserFactory
  - Simplified cleanup logic

- `scripts/auto_browse_cam_v3.py`
  - Removed `self.playwright`, `self.browser`, `self.context` attributes
  - Replaced `launch_browser()` implementation with `create_page()` call
  - Simplified `close()` method to just call `self.cleanup()`

- `scripts/explore_field_dependencies.py`
  - Removed `self.playwright`, `self.browser`, `self.context` attributes
  - Replaced `launch_browser()` implementation with `create_page()` call
  - Simplified `close()` method to just call `self.cleanup()`

## Key Design Decisions

1. **Return tuple pattern**: `create_page()` returns `(page, cleanup)` to ensure proper resource cleanup
2. **Optional auth**: `auth_file` parameter is optional - login flow doesn't need it
3. **Consistent defaults**: All browser settings (proxy, viewport, channel) centralized
4. **Error handling**: FileNotFoundError raised if auth_file specified but missing

## Verification

- ✅ All scripts compile without syntax errors
- ✅ BrowserFactory imports successfully
- ✅ No breaking changes to existing APIs

## Next Steps

Proceed to PHASE 2: Create shared Artifacts module (StepRecorder).
