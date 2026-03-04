# CAM Doc Structure Builder

## Purpose

Choose document template and build section outline for CAM user guide documentation.

## What It Does

1. Checks existing docs for duplicates and context
2. Determines appropriate file order number
3. Selects document template (Setup Guide / Feature Manual / FAQ)
4. Builds section outline with descriptions
5. Presents structure proposal to PM for approval

## Dependencies

- Reads: `/Users/jessiecao/src/cam-docs/docs/user-guide/`
- Reads: `/Users/jessiecao/src/cam-docs/docs/common-features/`

## Returns

- Document type recommendation
- Suggested order value with reasoning
- Complete section outline
- Awaits PM approval before content writing

## Usage

This sub-skill is called after complexity assessment and information gathering, before content writing begins.
