# CAM User Guide Writer

A Claude Code skill for writing clear, well-structured user guide documentation for the CAM (Crypto Asset Management) system.

## What This Skill Does

This skill helps product managers create comprehensive documentation for CAM features by:

- **Assessing complexity** and choosing the right documentation approach
- **Automating screenshot capture** from your browser (optional)
- **Searching codebase** to discover undocumented features
- **Following CAM docs standards** (VuePress frontmatter, formatting rules)
- **Preventing common mistakes** (Chinese characters, wrong markdown syntax)

## Key Features

✅ **Complexity-based workflow** - Automatically scales from simple button docs to complex feature guides
✅ **Browser automation** - Capture screenshots and UI labels automatically
✅ **Code search** - Find frontend/backend implementation details
✅ **Modular architecture** - Only loads what you need (40% token savings for simple docs)
✅ **Fail-safe for large features** - Suggests splitting into multiple docs to prevent context overflow

## Installation

### Method 1: Using the .skill file (Recommended)

```bash
# Install the skill
claude skill install cam-user-guide-writer.skill

# Verify installation
ls ~/.claude/skills/cam-user-guide-writer
```

### Method 2: Manual installation

```bash
# Extract to skills directory
mkdir -p ~/.claude/skills/cam-user-guide-writer
tar -xzf cam-user-guide-writer.skill -C ~/.claude/skills/cam-user-guide-writer
```

### Method 3: From Git repository (if available)

```bash
cd ~/.claude/skills/
git clone <repository-url> cam-user-guide-writer
```

## Prerequisites

### Required
- Claude Code CLI installed
- Access to CAM docs repository

### Optional (for browser automation)
```bash
# Install Playwright for automated screenshot capture
pip install playwright
playwright install chromium
```

## Configuration

### Path Setup

The skill uses default paths for the primary CAM development environment. If your paths are different, you'll need to update them:

**Default paths**:
- CAM docs: `/Users/jessiecao/src/cam-docs/`
- CAM code: `/Users/jessiecao/src/cam/`

**To configure for your environment**:
When the skill asks about paths, provide your actual repository locations.

## How to Use

### Basic Usage

1. **Start Claude Code** in your CAM docs directory:
   ```bash
   cd /path/to/cam-docs
   claude
   ```

2. **Trigger the skill** with any of these phrases:
   - "I want to write a user guide for [feature name]"
   - "Help me document the [feature] feature"
   - "Create CAM documentation for [feature]"
   - "Write docs for [feature]"

3. **Follow the workflow**:
   - The skill will assess complexity (Low/Medium/High)
   - Choose information gathering method (A/B/C)
   - Review and approve the outline
   - Write the documentation

### Complexity Levels

**Low Complexity** (Simple UI component):
- Examples: Button, dropdown, simple filter
- Approach: Manual Q&A → outline → write
- Time: ~10-15 minutes

**Medium Complexity** (Multiple interactions):
- Examples: Date picker with presets, account selector
- Approach: Manual Q&A or browser capture → outline → write
- Time: ~20-30 minutes

**High Complexity** (Calculations, backend logic):
- Examples: NAV calculation, backtrack, fee accrual
- Approach: Browser capture + code search → outline → write
- Time: ~45-60 minutes

### Information Gathering Options

**Option A: Live Browser Automation**
- You have access to CAM and can open the feature
- The skill connects to your Chrome and captures screenshots automatically
- Best for: UI-heavy features with complex interactions

**Option B: Multiple Complementary Materials (Recommended)**
- You provide any combination of materials:
  - Screen recordings (MP4, MOV, GIF) showing workflows
  - Design documents (Word, PDF, Figma) with requirements
  - Existing documentation (wiki, PRD, specs)
  - Screenshots (PNG, JPG) of key UI states
- The skill synthesizes information from all sources
- Best for: Comprehensive documentation with business context

**Option C: Manual Q&A**
- You describe the feature verbally
- The skill asks clarifying questions
- Best for: Simple features or when no materials available

**Most Common**: Option B with multiple materials that complement each other (e.g., design doc + screen recording, PRD + screenshots)

## File Structure

```
cam-user-guide-writer/
├── README.md                    # This file
├── SKILL.md                     # Main skill workflow (310 lines)
├── OPTIMIZATION_SUMMARY.md      # Architecture and design decisions
├── references/                  # Detailed guides (loaded on-demand)
│   ├── formatting-guide.md      # Formatting rules, HTML patterns
│   ├── browser-automation.md    # Playwright capture guide
│   └── code-search.md           # Codebase search techniques
├── scripts/                     # Automation tools
│   └── browse_cam.py            # Browser automation script
└── evals/                       # Test cases (optional)
```

## Examples

### Example 1: Simple UI Component (Low Complexity)

```
You: "I want to document the Export button in Table View"

Skill: Assesses as Low complexity → Manual Q&A
- Asks about button location, behavior, export formats
- Proposes outline
- Writes concise documentation
- Time: ~10 minutes
```

### Example 2: Complex Feature with Multiple Materials (High Complexity)

```
You: "I need to document the Account Backtrack feature. I have a PRD document and a screen recording."

Skill: Assesses as High complexity → Option B (multiple materials)
- Asks you to provide the PRD and video
- Extracts business requirements from PRD
- Extracts UI workflows from screen recording
- Searches frontend code for configuration options
- Searches backend code for calculation formulas
- Cross-references all sources for accuracy
- Proposes comprehensive outline
- Writes detailed documentation with formulas
- Time: ~45 minutes
```

### Example 3: Very Large Feature (Split Docs)

```
You: "I want to document Fund Accounting. I have design docs, Figma mockups, and technical specs."

Skill: Detects 5+ sub-features → Suggests splitting
- Reviews all provided materials
- Identifies major sub-features
- Proposes: fund-accounting-overview.md
- Proposes: fund-accounting-nav.md
- Proposes: fund-accounting-fees.md
- Proposes: fund-accounting-reports.md
- Prevents context overflow
```

## Tips for Best Results

1. **Provide multiple complementary materials**: Design doc + screen recording works better than either alone
2. **Be specific about the feature**: "Time Selector component" is better than "time picker"
3. **List all materials upfront**: "I have a PRD, 2 screen recordings, and 5 screenshots"
4. **Review the outline carefully**: It's easier to fix structure before writing
5. **Provide code locations if needed**: If the skill can't find code, tell it where to look
6. **Cross-reference materials**: If design doc and implementation differ, clarify which is correct

## Troubleshooting

### Skill doesn't trigger
- Make sure you mention "user guide", "documentation", or "docs"
- Try: "I want to write a CAM user guide for [feature]"

### Browser automation fails
- Check Chrome is running with `--remote-debugging-port=9222`
- Verify you're logged into CAM
- Check Playwright is installed: `pip list | grep playwright`

### Screenshots have Chinese characters
- The skill will detect this and ask you to recapture
- Make sure CAM UI is set to English before capturing

### Code search finds nothing
- Provide the code location: "The code is in /path/to/component"
- The skill will search both frontend and backend

### Context overflow / 502 errors
- The skill will suggest splitting large features
- Follow the suggestion to create multiple smaller docs

## Advanced Usage

### Custom Paths

If working in a different environment:

```
You: "I want to document [feature]"
Skill: "What does this feature do?"
You: "It's a [description]. By the way, my CAM docs are at /custom/path/cam-docs"
Skill: Will use your custom path
```

### Combining with External Docs

```
You: "I want to document [feature]. I have a PRD, a screen recording, and some screenshots."
Skill: Chooses Option B (multiple complementary materials)
You: [Provide the PRD path, video file, and screenshot files]
Skill:
- Extracts business requirements from PRD
- Extracts UI workflows from screen recording
- Uses screenshots to verify UI states
- Cross-references all materials for accuracy
- Identifies any discrepancies and asks for clarification
- Writes comprehensive documentation
```

## Token Savings

The skill is optimized for efficiency:

- **Low complexity docs**: ~40% fewer tokens (skip automation + code search)
- **Medium complexity docs**: ~20% fewer tokens (skip code search)
- **High complexity docs**: Similar token usage (load all references)

## Support

If you encounter issues:

1. Check this README first
2. Review `OPTIMIZATION_SUMMARY.md` for architecture details
3. Check the skill's reference files in `references/`
4. Contact the skill maintainer (original creator)

## Version History

- **v1.0** (2026-03-02): Initial optimized version
  - Modular architecture with reference files
  - Complexity gate with fail-safe
  - Backend code search
  - Browser automation support
  - 40% token savings for simple docs

## Contributing

If you improve this skill:

1. Test with at least 3 different complexity levels
2. Update `OPTIMIZATION_SUMMARY.md` with your changes
3. Increment version in this README
4. Share the updated `.skill` file with the team

## License

Internal use only - CAM documentation team
