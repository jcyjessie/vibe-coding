#!/usr/bin/env python3
"""
Artifacts - Unified screenshot and step recording for CAM automation scripts.

Provides StepRecorder class that handles:
- Screenshot capture with metadata
- Step tracking and numbering
- JSON output generation

Usage:
    from core.artifacts import StepRecorder

    recorder = StepRecorder(output_dir="captured_data", feature_name="my-feature")

    # Capture a step
    step_data = recorder.capture_step(
        page=page,
        step_name="01-initial-page",
        description="Initial page load",
        extra_data={"field": "value"}
    )

    # Save all captured steps to JSON
    output_file = recorder.save_results()
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class StepRecorder:
    """
    Records automation steps with screenshots and metadata.

    Handles screenshot capture, step numbering, and JSON output generation
    for browser automation workflows.
    """

    def __init__(self, output_dir: str = "captured_data", feature_name: str = "feature"):
        """
        Initialize StepRecorder.

        Args:
            output_dir: Directory for screenshots and JSON output
            feature_name: Name of the feature being captured (for output filename)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.screenshots_dir = self.output_dir / "screenshots"
        self.screenshots_dir.mkdir(exist_ok=True)

        self.feature_name = feature_name
        self.captured_steps: List[Dict[str, Any]] = []
        self.step_counter = 1

    def capture_step(
        self,
        page,
        step_name: str,
        description: str,
        extra_data: Optional[Dict[str, Any]] = None,
        full_page: bool = False
    ) -> Dict[str, Any]:
        """
        Capture a screenshot and record step metadata.

        Args:
            page: Playwright page object
            step_name: Unique name for this step (e.g., "01-initial-page")
            description: Human-readable description of what this step shows
            extra_data: Optional additional data to include in step metadata
            full_page: Whether to capture full page screenshot (default: False)

        Returns:
            Dictionary containing step metadata including screenshot path
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_filename = f"{step_name}_{timestamp}.png"
        screenshot_path = self.screenshots_dir / screenshot_filename

        # Take screenshot
        page.screenshot(path=str(screenshot_path), full_page=full_page)

        # Build step metadata
        step_data = {
            "step_number": self.step_counter,
            "step_name": step_name,
            "description": description,
            "url": page.url,
            "title": page.title(),
            "screenshot": str(screenshot_filename),
            "timestamp": timestamp
        }

        # Add extra data if provided
        if extra_data:
            step_data.update(extra_data)

        # Log the capture
        logger.info(f"Step {self.step_counter}: {description}")
        logger.info(f"  Screenshot: {screenshot_filename}")

        # Store and increment
        self.captured_steps.append(step_data)
        self.step_counter += 1

        return step_data

    def save_results(self, capture_mode: str = "automated") -> Path:
        """
        Save all captured steps to JSON file.

        Args:
            capture_mode: Description of capture mode (e.g., "automated", "field_dependency_exploration")

        Returns:
            Path to the saved JSON file
        """
        output_file = self.output_dir / f"{self.feature_name}_captured.json"

        result = {
            "feature_name": self.feature_name,
            "capture_date": datetime.now().isoformat(),
            "capture_mode": capture_mode,
            "total_steps": len(self.captured_steps),
            "steps": self.captured_steps
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        logger.info(f"Results saved to: {output_file}")
        logger.info(f"Screenshots saved to: {self.screenshots_dir}")

        return output_file

    def get_step_count(self) -> int:
        """Get the number of steps captured so far."""
        return len(self.captured_steps)

    def get_latest_step(self) -> Optional[Dict[str, Any]]:
        """Get the most recently captured step, or None if no steps captured."""
        return self.captured_steps[-1] if self.captured_steps else None
