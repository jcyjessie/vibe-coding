#!/usr/bin/env python3
"""
CAM Documentation Tool - Unified CLI

Provides three main commands:
- login: Authenticate and save session state
- browse: Automatically capture page screenshots and interactions
- deps: Explore field dependencies in forms

Usage:
    # Login first
    cam_doc login --username admin --password your-password

    # Capture a page
    cam_doc browse --url https://cam.example.com/v3/feature --feature-name my-feature

    # Explore field dependencies
    cam_doc deps --url https://cam.example.com/v3/feature --feature-name my-feature
"""

import argparse
import sys
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import core modules
try:
    from core.browser_factory import create_page
    from core.artifacts import StepRecorder
    from core.config import RuntimeConfig, load_config_from_env, apply_cli_overrides
except ImportError as e:
    logger.error(f"Failed to import core modules: {e}")
    logger.error("Make sure you're running from the scripts/ directory")
    sys.exit(1)

# Import flow modules
try:
    from flows.login_flow import perform_login_flow, save_auth_state
    from flows.browse_flow import automatic_capture_flow
    from flows.deps_flow import explore_dependencies_flow, ExplorationBudget
except ImportError as e:
    logger.error(f"Failed to import flow modules: {e}")
    logger.error("Make sure flows/ directory exists with all flow modules")
    sys.exit(1)

# Import retry handler
try:
    from retry_handler import RetryHandler, RetryableError
except ImportError as e:
    logger.error(f"Failed to import retry_handler: {e}")
    sys.exit(1)


def cmd_login(args, cfg: RuntimeConfig):
    """Execute login command"""
    logger.info("=" * 60)
    logger.info("CAM LOGIN")
    logger.info("=" * 60)

    # Get password from args or environment variable
    password = args.password or os.getenv('FRESH_MASTER_ADMIN_PASSWORD')
    if not password:
        logger.error("Password not provided")
        logger.error("Either:")
        logger.error("  1. Set environment variable: export FRESH_MASTER_ADMIN_PASSWORD='your-password'")
        logger.error("  2. Or pass --password argument")
        sys.exit(1)

    # Define login operation (for retry)
    def perform_login():
        # Create page using BrowserFactory with config
        page, cleanup = create_page(config=cfg)

        try:
            # Execute login flow
            perform_login_flow(
                page=page,
                username=args.username,
                password=password,
                base_url=cfg.base_url
            )

            # Save authentication state
            save_auth_state(page, cfg.auth_file)

        except RetryableError:
            # Re-raise retryable errors
            raise
        except Exception as e:
            logger.error(f"Login failed: {e}")
            import traceback
            traceback.print_exc()
            raise RetryableError(f"Login operation failed: {e}")
        finally:
            cleanup()

    # Execute with retry
    retry_handler = RetryHandler(max_retries=3, base_delay=2.0)
    try:
        retry_handler.execute(perform_login)
        logger.info("\n" + "=" * 60)
        logger.info("LOGIN SUCCESSFUL")
        logger.info("=" * 60)
    except RetryableError as e:
        logger.error(f"Login failed after all retries: {e}")
        sys.exit(1)


def cmd_browse(args, cfg: RuntimeConfig):
    """Execute browse command"""
    logger.info("=" * 60)
    logger.info("CAM BROWSE - AUTOMATIC CAPTURE")
    logger.info("=" * 60)

    # Create output directory
    output_dir = Path(cfg.output_dir)
    output_dir.mkdir(exist_ok=True)

    # Create page using BrowserFactory with config
    page, cleanup = create_page(
        auth_file=cfg.auth_file,
        config=cfg
    )

    try:
        # Initialize StepRecorder
        recorder = StepRecorder(
            output_dir=str(output_dir),
            feature_name=args.feature_name
        )

        # Execute browse flow
        captured_steps = automatic_capture_flow(
            page=page,
            recorder=recorder,
            target_url=args.url
        )

        if captured_steps:
            # Save results
            output_file = recorder.save_results(capture_mode="automatic_v3_state_tracking")

            logger.info("\n" + "=" * 60)
            logger.info("NEXT STEPS")
            logger.info("=" * 60)
            logger.info(f"1. Review captured data: {output_file}")
            logger.info(f"2. Review screenshots: {recorder.screenshots_dir}")
            logger.info(f"3. Use this data to generate CAM documentation")
            logger.info("=" * 60)
        else:
            logger.warning("No steps captured.")

    except KeyboardInterrupt:
        logger.info("\nCapture interrupted by user.")
    except Exception as e:
        logger.error(f"Error during capture: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        cleanup()


def cmd_deps(args, cfg: RuntimeConfig):
    """Execute field dependency exploration command"""
    logger.info("=" * 60)
    logger.info("CAM FIELD DEPENDENCY EXPLORATION")
    logger.info("=" * 60)

    # Create output directory
    output_dir = Path(cfg.output_dir)
    output_dir.mkdir(exist_ok=True)

    # Create page using BrowserFactory with config
    page, cleanup = create_page(
        auth_file=cfg.auth_file,
        config=cfg
    )

    try:
        # Initialize StepRecorder
        recorder = StepRecorder(
            output_dir=str(output_dir),
            feature_name=args.feature_name
        )

        # Initialize exploration budget from config
        budget = ExplorationBudget(
            max_steps=cfg.max_steps,
            max_states=cfg.max_states,
            max_time_seconds=cfg.max_time_seconds
        )

        # Execute deps flow
        field_dependencies = explore_dependencies_flow(
            page=page,
            recorder=recorder,
            target_url=args.url,
            budget=budget
        )

        if recorder.captured_steps:
            # Save results using StepRecorder
            output_file = recorder.save_results(capture_mode="field_dependency_exploration")

            # Update the JSON to include field_dependencies
            import json
            with open(output_file, 'r', encoding='utf-8') as f:
                result = json.load(f)

            result["field_dependencies"] = field_dependencies

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            logger.info(f"✓ Results saved to: {output_file}")
            logger.info(f"✓ Screenshots saved to: {recorder.screenshots_dir}")

            # Print dependency summary
            if field_dependencies:
                logger.info("\n" + "=" * 60)
                logger.info("DETECTED FIELD DEPENDENCIES")
                logger.info("=" * 60)
                for field, dependencies in field_dependencies.items():
                    logger.info(f"\n{field}:")
                    for option, changes in dependencies.items():
                        logger.info(f"  When '{option}' is selected:")
                        if changes.get("new_fields"):
                            logger.info(f"    - New fields appear: {', '.join(changes['new_fields'])}")
                        if changes.get("hidden_fields"):
                            logger.info(f"    - Fields hidden: {', '.join(changes['hidden_fields'])}")
                        if changes.get("value_changes"):
                            logger.info(f"    - {len(changes['value_changes'])} field value(s) changed")
                logger.info("=" * 60)

            logger.info("\n" + "=" * 60)
            logger.info("NEXT STEPS")
            logger.info("=" * 60)
            logger.info(f"1. Review dependencies: {output_file}")
            logger.info(f"2. Review screenshots: {recorder.screenshots_dir}")
            logger.info(f"3. Use this data to document field interactions")
            logger.info("=" * 60)
        else:
            logger.warning("No steps captured.")

    except KeyboardInterrupt:
        logger.info("\n\nExploration interrupted by user.")
    except Exception as e:
        logger.error(f"\nError during exploration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        cleanup()


def main():
    """Main CLI entry point"""
    # Load configuration from environment
    base_cfg = load_config_from_env()

    parser = argparse.ArgumentParser(
        description="CAM Documentation Tool - Unified CLI for login, browse, and dependency exploration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  # Login first
  cam_doc login --username admin --password your-password

  # Or use environment variable
  export FRESH_MASTER_ADMIN_PASSWORD='your-password'
  cam_doc login --username admin

  # Capture a page
  cam_doc browse --url https://fresh2.cammaster.org/v3/analysis/reporting/routine \\
    --feature-name routine-report

  # Explore field dependencies
  cam_doc deps --url https://fresh2.cammaster.org/v3/analysis/reporting/routine \\
    --feature-name routine-report

  # Run in headless mode
  cam_doc browse --url https://fresh2.cammaster.org/v3/feature \\
    --feature-name my-feature --headless

Environment Variables (override code defaults):
  CAM_BASE_URL          Base URL (default: {base_cfg.base_url})
  CAM_PROXY             HTTP proxy (default: {base_cfg.proxy})
  CAM_HEADLESS          Headless mode (default: {base_cfg.headless})
  CAM_TIMEOUT_MS        Timeout in ms (default: {base_cfg.timeout_ms})
  CAM_VIEWPORT_WIDTH    Viewport width (default: {base_cfg.viewport_width})
  CAM_VIEWPORT_HEIGHT   Viewport height (default: {base_cfg.viewport_height})
  CAM_AUTH_FILE         Auth file path (default: {base_cfg.auth_file})
  CAM_OUTPUT_DIR        Output directory (default: {base_cfg.output_dir})
  CAM_MAX_STEPS         Max exploration steps (default: {base_cfg.max_steps})
  CAM_MAX_STATES        Max unique states (default: {base_cfg.max_states})
  CAM_MAX_TIME_SECONDS  Max exploration time (default: {base_cfg.max_time_seconds})
        """
    )

    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    subparsers.required = True

    # ===== LOGIN COMMAND =====
    login_parser = subparsers.add_parser(
        'login',
        help='Authenticate and save session state',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    login_parser.add_argument(
        '--username',
        required=True,
        help='CAM username'
    )
    login_parser.add_argument(
        '--password',
        default=None,
        help='CAM password (or set FRESH_MASTER_ADMIN_PASSWORD environment variable)'
    )
    login_parser.add_argument(
        '--base-url',
        default=None,
        help=f'CAM base URL (default from config: {base_cfg.base_url})'
    )
    login_parser.add_argument(
        '--auth-file',
        default=None,
        help=f'Path to save authentication state (default from config: {base_cfg.auth_file})'
    )
    login_parser.add_argument(
        '--headless',
        action='store_true',
        default=None,
        help='Run browser in headless mode'
    )
    login_parser.set_defaults(func=cmd_login)

    # ===== BROWSE COMMAND =====
    browse_parser = subparsers.add_parser(
        'browse',
        help='Automatically capture page screenshots and interactions',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    browse_parser.add_argument(
        '--url',
        required=True,
        help='CAM feature URL to capture'
    )
    browse_parser.add_argument(
        '--feature-name',
        required=True,
        help='Feature name for output files'
    )
    browse_parser.add_argument(
        '--auth-file',
        default=None,
        help=f'Path to authentication state file (default from config: {base_cfg.auth_file})'
    )
    browse_parser.add_argument(
        '--output',
        default=None,
        help=f'Output directory for captured data (default from config: {base_cfg.output_dir})'
    )
    browse_parser.add_argument(
        '--headless',
        action='store_true',
        default=None,
        help='Run browser in headless mode'
    )
    browse_parser.set_defaults(func=cmd_browse)

    # ===== DEPS COMMAND =====
    deps_parser = subparsers.add_parser(
        'deps',
        help='Explore field dependencies in forms',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    deps_parser.add_argument(
        '--url',
        required=True,
        help='CAM feature URL to explore'
    )
    deps_parser.add_argument(
        '--feature-name',
        required=True,
        help='Feature name for output files'
    )
    deps_parser.add_argument(
        '--auth-file',
        default=None,
        help=f'Path to authentication state file (default from config: {base_cfg.auth_file})'
    )
    deps_parser.add_argument(
        '--output',
        default=None,
        help=f'Output directory for captured data (default from config: {base_cfg.output_dir})'
    )
    deps_parser.add_argument(
        '--headless',
        action='store_true',
        default=None,
        help='Run browser in headless mode'
    )
    deps_parser.add_argument(
        '--max-steps',
        type=int,
        default=None,
        help=f'Maximum number of exploration steps (default from config: {base_cfg.max_steps})'
    )
    deps_parser.add_argument(
        '--max-states',
        type=int,
        default=None,
        help=f'Maximum number of unique states to visit (default from config: {base_cfg.max_states})'
    )
    deps_parser.add_argument(
        '--max-time',
        type=int,
        default=None,
        help=f'Maximum exploration time in seconds (default from config: {base_cfg.max_time_seconds})'
    )
    deps_parser.set_defaults(func=cmd_deps)

    # Parse arguments and apply config overrides
    args = parser.parse_args()

    # Apply CLI overrides to config
    cfg = apply_cli_overrides(base_cfg, args)

    # Execute command with config
    args.func(args, cfg)


if __name__ == "__main__":
    main()
