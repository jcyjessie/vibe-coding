# CAM User Guide Writer - Usage Example

This document shows how to use the skill with automated browser capture.

## Complete Workflow Example

### Scenario
You need to write documentation for the "Portfolio Snapshot" feature in CAM.

### Step-by-Step Process

#### 1. Start the Conversation

```
User: "I need to write a user guide for the Portfolio Snapshot feature"
```

#### 2. Skill Triggers and Asks About Capture Method

```
Assistant: "I'll help you write the Portfolio Snapshot user guide.

First, let me ask: Do you want to use automated browser capture or provide information manually?

Option A: Automated Browser Capture (Recommended)
- I'll guide you to run a script that captures screenshots and UI labels automatically
- Requires: Chrome with debugging port, Playwright installed
- Benefits: Accurate UI labels, complete workflow, organized screenshots

Option B: Manual Information Gathering
- You describe the feature and I'll ask questions
- Traditional Q&A approach

Which option would you prefer?"
```

#### 3. User Chooses Automated Capture

```
User: "Let's use automated capture. I have Chrome and can install Playwright."
```

#### 4. Assistant Guides Setup

```
Assistant: "Great! Let's set up automated capture:

Step 1: Install Playwright (if not already installed)
```bash
pip install playwright
playwright install chromium
```

Step 2: Start Chrome with debugging port
Open a terminal and run:
```bash
chrome --remote-debugging-port=9222
```

Step 3: Log into CAM in that Chrome window
Navigate to your CAM instance and log in normally.

Step 4: Run the capture script
In another terminal:
```bash
cd /Users/jessiecao/.claude/skills/cam-user-guide-writer/scripts
python browse_cam.py --url https://your-cam-url.com/portfolio --feature-name portfolio-snapshot
```

The script will enter interactive mode. Perform these actions in the browser:
1. Click 'Create Snapshot' button
2. Fill in snapshot name
3. Click 'Confirm'
4. View the created snapshot
5. Click 'Export' button
6. Select export format

After each action, come back to the terminal, press ENTER, and describe what you did.

Let me know when you've completed the capture!"
```

#### 5. User Runs Capture and Provides Data

```
User: "Done! The captured data is at captured_data/portfolio-snapshot_captured.json"
```

#### 6. Assistant Reads Captured Data

```
Assistant: [Reads the JSON file]

"Perfect! I've analyzed the captured data. Here's what I found:

Captured workflow:
- Step 1: Click 'Create Snapshot' button
- Step 2: Enter snapshot name in 'Snapshot Name' field
- Step 3: Click 'Confirm' button
- Step 4: View snapshot in 'Snapshots' table
- Step 5: Click 'Export' button
- Step 6: Select 'CSV' format

UI Elements found:
- Buttons: 'Create Snapshot', 'Confirm', 'Export', 'Delete'
- Input fields: 'Snapshot Name', 'Description'
- Navigation: Portfolio > Snapshots

Now let me propose a document structure..."
```

#### 7. Assistant Proposes Structure (Step 4 - MANDATORY)

```
Assistant: "Proposed structure for Portfolio Snapshot:

## Introduction
Brief overview of portfolio snapshot feature and its benefits

## Important Notes
- Snapshot frequency limitations
- Data retention period

## What is a Portfolio Snapshot
Explanation of snapshot concept and use cases

## User Guide
### Create a Snapshot
### View Snapshots
### Export Snapshot Data
### Delete a Snapshot

## Tips
Best practices for snapshot management

## FAQ
- How often can I create snapshots?
- How long are snapshots retained?
- Can I schedule automatic snapshots?

Does this structure work for you?"
```

#### 8. User Approves Structure

```
User: "Yes, looks good. Please write the full document."
```

#### 9. Assistant Writes Complete Document

```
Assistant: [Generates complete markdown document with:
- Correct frontmatter
- All sections from the outline
- Screenshots referenced from captured data
- Exact UI labels from captured data
- Comprehensive coverage of all actions
- Tips and FAQ sections
- Proper markdown formatting]
```

## Example Captured Data Format

```json
{
  "feature_name": "portfolio-snapshot",
  "capture_date": "2024-02-28T14:30:00",
  "total_steps": 6,
  "steps": [
    {
      "step_number": 1,
      "step_name": "step-1",
      "description": "Click Create Snapshot button",
      "url": "https://cam.example.com/portfolio",
      "title": "Portfolio - CAM",
      "screenshot": "step-1_20240228_143000.png",
      "buttons": [
        {"text": "Create Snapshot", "type": "button"},
        {"text": "Export", "type": "button"},
        {"text": "Refresh", "type": "button"}
      ],
      "input_fields": [],
      "headings": [
        {"level": "H1", "text": "Portfolio Overview"},
        {"level": "H2", "text": "Snapshots"}
      ]
    },
    {
      "step_number": 2,
      "step_name": "step-2",
      "description": "Enter snapshot name",
      "url": "https://cam.example.com/portfolio/snapshot/create",
      "title": "Create Snapshot - CAM",
      "screenshot": "step-2_20240228_143030.png",
      "buttons": [
        {"text": "Confirm", "type": "button"},
        {"text": "Cancel", "type": "button"}
      ],
      "input_fields": [
        {"placeholder": "Enter snapshot name", "name": "snapshot_name", "type": "text"},
        {"placeholder": "Optional description", "name": "description", "type": "textarea"}
      ],
      "headings": [
        {"level": "H1", "text": "Create New Snapshot"}
      ]
    }
  ]
}
```

## Benefits of This Workflow

1. **Accuracy**: UI labels are captured exactly as they appear
2. **Completeness**: All user actions are recorded
3. **Efficiency**: Faster than manual description
4. **Screenshots**: Automatically organized and named
5. **Consistency**: Same process for all features

## Fallback to Manual Mode

If automated capture fails or is not feasible:

```
Assistant: "I see the automated capture isn't working. Let's switch to manual mode.

Can you tell me:
1. What does the Portfolio Snapshot feature do?
2. What are the main user actions (create, view, export, delete)?
3. What are the exact button labels in the UI?
4. Are there any limitations or prerequisites?"
```

Then proceed with traditional Q&A workflow.
