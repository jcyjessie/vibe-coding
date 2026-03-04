# CAM User Guide Writer

A modular Claude Code skill system for writing clear, well-structured user guide documentation for the CAM (Crypto Asset Management) system.

## Architecture

**Modular Design**: 1 main dispatcher + 6 specialized sub-skills

```
cam-user-guide-writer (Dispatcher)
├── cam-complexity-assessor      → Assess feature complexity
├── cam-doc-structure-builder    → Choose template & build outline
├── cam-browser-capture          → Browser automation + screenshots
├── cam-code-searcher            → Search codebase for business logic
├── cam-doc-formatter            → Format content with validation
└── cam-doc-validator            → Comprehensive final checks
```

## Invocation Flow

```
1. PM triggers main skill: "Write user guide for [feature]"
   ↓
2. Main skill asks: Feature name? Materials available?
   ↓
3. Invoke cam-complexity-assessor → Returns Low/Medium/High
   ↓
4. Invoke cam-doc-structure-builder → Returns outline + order number
   ↓
5. Ask PM: Use browser automation? → Invoke cam-browser-capture (optional)
   ↓
6. Ask PM: Search codebase? → Invoke cam-code-searcher (optional)
   ↓
7. Invoke cam-doc-formatter → Returns formatted markdown
   ↓
8. Invoke cam-doc-validator → Returns validation report
   ↓
9. Deliver final document to PM
```

## Sub-Skill Descriptions

### cam-complexity-assessor
Asks 3 questions to determine if a feature is Low/Medium/High complexity:
- Does it involve calculations or backend logic?
- How many distinct sub-features or workflows?
- Are there non-obvious business rules?

### cam-doc-structure-builder
Chooses appropriate template and builds section outline:
- Setup/Onboarding guide (numbered steps)
- Feature manual (plain headings + use cases)
- FAQ/Reference (Q&A format)

### cam-browser-capture
Automates screenshot capture via Playwright:
- Automatic mode: Script explores UI automatically
- Interactive mode: User operates, script captures
- Headless mode: CI/CD integration

### cam-code-searcher
Searches CAM codebase for undocumented features:
- i18n files (business rules, data delays)
- Frontend components (UI labels, field options)
- Backend code (calculations, validation logic)

### cam-doc-formatter
Applies CAM formatting rules:
- Bold UI elements: **Save**, **Confirm**
- Navigation format: **Menu > Submenu > Item**
- Bullet lists use `-` (not `*`)
- English only (no Chinese characters)

### cam-doc-validator
Comprehensive final quality check:
- Frontmatter completeness
- Structure correctness
- Content completeness (examples, use cases)
- Language and formatting
- Screenshot coverage

## Installation

### 1. Install Main Skill

```bash
claude skill install cam-user-guide-writer.skill
```

### 2. Install Sub-Skills (Automatic)

Sub-skills are automatically available when the main skill is installed. No additional installation needed.

### 3. Optional: Browser Automation Setup

```bash
pip install playwright
playwright install chromium
```

## Quick Start

### 1. Start Claude in CAM Docs Directory

```bash
cd /path/to/cam-docs
claude
```

### 2. Trigger the Skill

Say: **"I want to write a user guide for [feature name]"**

The main skill will orchestrate all sub-skills automatically.

## When to Use This Skill

| Scenario | Use This Skill? |
|----------|----------------|
| Simple UI component (button, dropdown) | ✅ Yes (Low complexity) |
| Multi-step workflow with screenshots | ✅ Yes (Medium complexity) |
| Complex feature with calculations | ✅ Yes (High complexity) |
| Quick text update to existing doc | ❌ No (edit manually) |

## Documentation

- **[WORKFLOW_DIAGRAM.md](./WORKFLOW_DIAGRAM.md)** - Visual workflow and decision points
- **[SKILL.md](./SKILL.md)** - Main dispatcher logic
- **[AUTO_CAPTURE_GUIDE.md](./AUTO_CAPTURE_GUIDE.md)** - Browser automation setup
- **[USAGE_EXAMPLE.md](./USAGE_EXAMPLE.md)** - Real-world examples
- **[CHANGELOG.md](./CHANGELOG.md)** - Version history

## Prerequisites

**Required:**
- Claude Code CLI installed
- Access to CAM docs repository (`/path/to/cam-docs`)

**Optional (for browser automation):**
```bash
pip install playwright
playwright install chromium
```

## Benefits of Modular Architecture

**Before (v3.x)**: 670-line monolithic skill
- Hard to maintain
- Mixed concerns
- Difficult to test individual components

**After (v4.0)**: 100-line dispatcher + 6 focused sub-skills
- Single responsibility per skill
- Easy to maintain and update
- Testable components
- Reusable sub-skills

## Support

For issues or questions:
- Check [AUTO_CAPTURE_GUIDE.md](./AUTO_CAPTURE_GUIDE.md) for automation troubleshooting
- Review [USAGE_EXAMPLE.md](./USAGE_EXAMPLE.md) for documentation patterns
- See [CHANGELOG.md](./CHANGELOG.md) for recent changes
