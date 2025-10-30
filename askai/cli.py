"""CLI argument parsing for askai.

This module handles command-line argument parsing using argparse.
Supports provider selection, model selection, and various utility flags.

Usage examples:
    askai "what is python?"
    askai -p gemini "what is rust?"
    askai -m sonnet "explain async/await"
    askai -p claude -m opus "complex question"
    askai --list-providers
    askai --list-models claude
"""

import argparse
import sys

from askai import __version__


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog="askai",
        description="Context-free, one-shot LLM queries with concise answers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  askai "what is python?"                    # Use default provider/model
  askai -p gemini "what is rust?"            # Specify provider
  askai -m sonnet "explain async/await"      # Specify model
  askai -p claude -m opus "complex question" # Both provider and model
  askai --list-providers                     # List available providers
  askai --list-models claude                 # List models for a provider
  askai --config-path                        # Show config file location
  askai --version                            # Show version

configuration:
  Default provider and models are stored in ~/.config/askai/config.json
  You can edit this file directly or use the askai configuration commands.
        """,
    )

    # Positional argument - the prompt
    parser.add_argument(
        "prompt",
        type=str,
        nargs="?",  # Optional to allow --list-providers without prompt
        help="The question or prompt to ask the LLM",
    )

    # Provider selection
    parser.add_argument(
        "-p",
        "--provider",
        type=str,
        help="LLM provider to use (default: from config or 'claude')",
        metavar="PROVIDER",
    )

    # Model selection
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        help="Model to use (default: provider's default for concise responses)",
        metavar="MODEL",
    )

    # Information flags
    parser.add_argument(
        "--list-providers",
        action="store_true",
        help="List available providers and exit",
    )

    parser.add_argument(
        "--list-models",
        type=str,
        metavar="PROVIDER",
        help="List available models for a provider and exit",
    )

    parser.add_argument(
        "--config-path",
        action="store_true",
        help="Show configuration file path and exit",
    )

    parser.add_argument(
        "--config-show",
        action="store_true",
        help="Show current configuration and exit",
    )

    parser.add_argument(
        "--config-reset",
        action="store_true",
        help="Reset configuration to defaults",
    )

    # Version
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show version and exit",
    )

    # Verbose output
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output (show command being executed)",
    )

    # Dry run - show command without executing
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the command that would be executed without running it",
    )

    return parser


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments.

    Args:
        args: Optional list of arguments (defaults to sys.argv)

    Returns:
        Parsed arguments namespace

    Raises:
        SystemExit: If arguments are invalid or help is requested
    """
    parser = create_parser()
    parsed = parser.parse_args(args)

    # Validation: ensure we have a prompt if not using info flags
    if not any(
        [
            parsed.list_providers,
            parsed.list_models,
            parsed.config_path,
            parsed.config_show,
            parsed.config_reset,
        ]
    ):
        if not parsed.prompt:
            parser.error("the following arguments are required: prompt")

    return parsed


def validate_args(args: argparse.Namespace) -> None:
    """Validate parsed arguments for logical consistency.

    Args:
        args: Parsed arguments namespace

    Raises:
        ValueError: If arguments are logically inconsistent
    """
    # If model is specified without provider, that's fine - we'll use default provider
    # But we should warn if the model might not be compatible

    # If --list-models is used, ensure a provider is specified
    if args.list_models and not args.list_models.strip():
        raise ValueError("--list-models requires a provider name")

    # If both --dry-run and any config flags are set, that's confusing
    if args.dry_run and any([args.config_path, args.config_show, args.config_reset]):
        raise ValueError("--dry-run cannot be used with configuration flags")


def print_help() -> None:
    """Print help message and exit."""
    parser = create_parser()
    parser.print_help()
    sys.exit(0)


if __name__ == "__main__":
    # Allow testing the parser directly
    args = parse_args()
    print(f"Parsed arguments: {args}")
