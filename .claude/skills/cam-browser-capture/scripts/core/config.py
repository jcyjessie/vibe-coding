#!/usr/bin/env python3
"""
Runtime Configuration - Unified config layer for CAM documentation tools

Provides centralized configuration with:
- Code defaults
- Environment variable overrides
- CLI argument overrides

Environment Variables:
    CAM_BASE_URL - Base URL for CAM (default: https://fresh2.cammaster.org)
    CAM_PROXY - HTTP proxy URL (default: http://localhost:7890)
    CAM_CHANNEL - Browser channel (default: chromium)
    CAM_HEADLESS - Run in headless mode (default: false)
    CAM_TIMEOUT_MS - Default timeout in milliseconds (default: 30000)
    CAM_VIEWPORT_WIDTH - Browser viewport width (default: 1920)
    CAM_VIEWPORT_HEIGHT - Browser viewport height (default: 1080)
    CAM_AUTH_FILE - Path to auth state file (default: .auth/state.json)
    CAM_OUTPUT_DIR - Output directory for captured data (default: captured_data)
    CAM_MAX_OPTIONS_PER_FIELD - Max dropdown options to test (default: 5)
"""

import os
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class RuntimeConfig:
    """Runtime configuration for CAM documentation tools"""

    # Connection settings
    base_url: str = "https://fresh2.cammaster.org"
    proxy: Optional[str] = "http://localhost:7890"

    # Browser settings
    channel: str = "chromium"
    headless: bool = False
    timeout_ms: int = 30000
    viewport_width: int = 1920
    viewport_height: int = 1080

    # File paths
    auth_file: str = ".auth/state.json"
    output_dir: str = "captured_data"

    # Exploration settings
    max_options_per_field: int = 5
    max_steps: int = 100
    max_states: int = 50
    max_time_seconds: int = 300

    def to_viewport(self) -> Dict[str, int]:
        """Convert viewport settings to Playwright format"""
        return {
            "width": self.viewport_width,
            "height": self.viewport_height
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "base_url": self.base_url,
            "proxy": self.proxy,
            "channel": self.channel,
            "headless": self.headless,
            "timeout_ms": self.timeout_ms,
            "viewport": self.to_viewport(),
            "auth_file": self.auth_file,
            "output_dir": self.output_dir,
            "max_options_per_field": self.max_options_per_field,
            "max_steps": self.max_steps,
            "max_states": self.max_states,
            "max_time_seconds": self.max_time_seconds,
        }


def load_config_from_env() -> RuntimeConfig:
    """
    Load configuration from environment variables.

    Falls back to code defaults if env vars not set.

    Returns:
        RuntimeConfig with values from env or defaults
    """
    def get_bool(key: str, default: bool) -> bool:
        """Parse boolean from env var"""
        value = os.getenv(key)
        if value is None:
            return default
        return value.lower() in ('true', '1', 'yes', 'on')

    def get_int(key: str, default: int) -> int:
        """Parse integer from env var"""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default

    def get_str(key: str, default: str) -> str:
        """Get string from env var"""
        return os.getenv(key, default)

    def get_optional_str(key: str, default: Optional[str]) -> Optional[str]:
        """Get optional string from env var"""
        value = os.getenv(key)
        if value is None:
            return default
        # Allow empty string to disable (e.g., CAM_PROXY="")
        if value == "":
            return None
        return value

    return RuntimeConfig(
        base_url=get_str("CAM_BASE_URL", "https://fresh2.cammaster.org"),
        proxy=get_optional_str("CAM_PROXY", "http://localhost:7890"),
        channel=get_str("CAM_CHANNEL", "chromium"),
        headless=get_bool("CAM_HEADLESS", False),
        timeout_ms=get_int("CAM_TIMEOUT_MS", 30000),
        viewport_width=get_int("CAM_VIEWPORT_WIDTH", 1920),
        viewport_height=get_int("CAM_VIEWPORT_HEIGHT", 1080),
        auth_file=get_str("CAM_AUTH_FILE", ".auth/state.json"),
        output_dir=get_str("CAM_OUTPUT_DIR", "captured_data"),
        max_options_per_field=get_int("CAM_MAX_OPTIONS_PER_FIELD", 5),
        max_steps=get_int("CAM_MAX_STEPS", 100),
        max_states=get_int("CAM_MAX_STATES", 50),
        max_time_seconds=get_int("CAM_MAX_TIME_SECONDS", 300),
    )


def apply_cli_overrides(cfg: RuntimeConfig, args) -> RuntimeConfig:
    """
    Apply CLI argument overrides to configuration.

    Args:
        cfg: Base configuration (from env or defaults)
        args: Parsed argparse Namespace

    Returns:
        New RuntimeConfig with CLI overrides applied
    """
    # Create a copy of the config
    overrides = {}

    # Apply overrides from CLI args (only if provided)
    if hasattr(args, 'base_url') and args.base_url is not None:
        overrides['base_url'] = args.base_url

    if hasattr(args, 'headless') and args.headless is not None:
        overrides['headless'] = args.headless

    if hasattr(args, 'auth_file') and args.auth_file is not None:
        overrides['auth_file'] = args.auth_file

    if hasattr(args, 'output') and args.output is not None:
        overrides['output_dir'] = args.output

    if hasattr(args, 'max_steps') and args.max_steps is not None:
        overrides['max_steps'] = args.max_steps

    if hasattr(args, 'max_states') and args.max_states is not None:
        overrides['max_states'] = args.max_states

    if hasattr(args, 'max_time') and args.max_time is not None:
        overrides['max_time_seconds'] = args.max_time

    # Create new config with overrides
    return RuntimeConfig(
        base_url=overrides.get('base_url', cfg.base_url),
        proxy=cfg.proxy,  # Proxy not overridable via CLI (use env var)
        channel=cfg.channel,  # Channel not overridable via CLI
        headless=overrides.get('headless', cfg.headless),
        timeout_ms=cfg.timeout_ms,
        viewport_width=cfg.viewport_width,
        viewport_height=cfg.viewport_height,
        auth_file=overrides.get('auth_file', cfg.auth_file),
        output_dir=overrides.get('output_dir', cfg.output_dir),
        max_options_per_field=cfg.max_options_per_field,
        max_steps=overrides.get('max_steps', cfg.max_steps),
        max_states=overrides.get('max_states', cfg.max_states),
        max_time_seconds=overrides.get('max_time_seconds', cfg.max_time_seconds),
    )
