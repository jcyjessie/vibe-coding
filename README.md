# CAM User Guide Writer

A Claude Code skill for writing clear, well-structured user guide documentation for the CAM (Crypto Asset Management) system.

## What This Skill Does

Helps product managers create comprehensive CAM feature documentation by:
- Assessing complexity and choosing the right approach
- Automating screenshot capture (optional)
- Searching codebase for undocumented features
- Following CAM docs standards (VuePress, frontmatter)

## Quick Start (3 Steps)

### 1. Install the Skill

```bash
claude skill install cam-user-guide-writer.skill
```

### 2. Start Claude in CAM Docs Directory

```bash
cd /path/to/cam-docs
claude
```

### 3. Trigger the Skill

Say: **"I want to write a user guide for [feature name]"**

The skill will:
- Assess complexity (Low/Medium/High)
- Choose information gathering method
- Generate structured documentation

## When to Use This Skill

| Scenario | Use This Skill? |
|----------|----------------|
| Simple UI component (button, dropdown) | ✅ Yes (Low complexity) |
| Multi-step workflow with screenshots | ✅ Yes (Medium complexity) |
| Complex feature with calculations | ✅ Yes (High complexity) |
| Quick text update to existing doc | ❌ No (edit manually) |

## Documentation

- **[WORKFLOW_DIAGRAM.md](./WORKFLOW_DIAGRAM.md)** - Visual workflow and decision points (start here!)
- **[SKILL.md](./SKILL.md)** - Rules and constraints for Claude (mandatory reading for the AI)
- **[AUTO_CAPTURE_GUIDE.md](./AUTO_CAPTURE_GUIDE.md)** - Browser automation setup and usage
- **[USAGE_EXAMPLE.md](./USAGE_EXAMPLE.md)** - Real-world documentation examples
- **[CHANGELOG.md](./CHANGELOG.md)** - Version history and improvements

## Prerequisites

**Required:**
- Claude Code CLI installed
- Access to CAM docs repository (`/path/to/cam-docs`)

**Optional (for browser automation):**
```bash
pip install playwright
playwright install chromium
```

## Support

For issues or questions:
- Check [AUTO_CAPTURE_GUIDE.md](./AUTO_CAPTURE_GUIDE.md) for automation troubleshooting
- Review [USAGE_EXAMPLE.md](./USAGE_EXAMPLE.md) for documentation patterns
- See [CHANGELOG.md](./CHANGELOG.md) for recent changes
