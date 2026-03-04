# Implementation Plans

This directory contains design documents and implementation plans for the CAM User Guide Writer skill.

## Purpose

These documents record:
- Design decisions and rationale
- Implementation steps and code examples
- Testing requirements
- Evolution history of the skill

## Documents

| Date | Document | Status | Description |
|------|----------|--------|-------------|
| 2026-03-04 | [skill-modularization-design.md](./2026-03-04-skill-modularization-design.md) | ✅ Completed | Design doc for v4.0.0 modularization - split monolithic skill into 6 sub-skills |
| 2026-03-04 | [skill-modularization.md](./2026-03-04-skill-modularization.md) | ✅ Completed | Implementation plan for modularization (16 tasks) |
| 2026-03-03 | [browser-automation-v3.md](./2026-03-03-browser-automation-v3.md) | ✅ Completed | Browser automation v3 upgrade - state-driven capture, robust selectors |
| 2026-03-03 | [field-dependencies-v3.md](./2026-03-03-field-dependencies-v3.md) | ✅ Completed | Field dependencies v3 implementation |
| 2026-03-03 | [field-dependencies-improvements.md](./2026-03-03-field-dependencies-improvements.md) | ✅ Completed | Field dependencies improvements |

## Naming Convention

`YYYY-MM-DD-<feature-name>[-design].md`

- `-design.md` suffix: Design document (decisions, architecture, trade-offs)
- No suffix: Implementation plan (step-by-step tasks with code examples)

## Usage

These documents are primarily for:
1. **Historical reference** - Understanding why certain decisions were made
2. **Knowledge transfer** - Onboarding new contributors
3. **Future improvements** - Learning from past implementations

When creating new features, follow the same pattern:
1. Write design doc first (if complex)
2. Get approval on design
3. Write implementation plan
4. Execute plan using `superpowers:executing-plans` or `superpowers:subagent-driven-development`
