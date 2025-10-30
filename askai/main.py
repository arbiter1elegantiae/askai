"""Main entry point for askai CLI tool."""

import subprocess
import sys

from askai.cli import parse_args, validate_args
from askai.config import ConfigManager
from askai.providers.claude import ClaudeProvider


def get_provider(provider_name: str):
    """Get provider instance by name.

    Args:
        provider_name: Provider name (e.g., 'claude', 'gemini')

    Returns:
        Provider instance

    Raises:
        ValueError: If provider is not supported
    """
    providers = {
        "claude": ClaudeProvider,
        # Add more providers here as they're implemented
        # "gemini": GeminiProvider,
    }

    if provider_name not in providers:
        available = ", ".join(providers.keys())
        raise ValueError(f"Unknown provider '{provider_name}'. Available: {available}")

    return providers[provider_name]()


def list_providers():
    """List all available providers."""
    providers = ["claude"]  # Add more as implemented
    print("Available providers:")
    for provider_name in providers:
        provider = get_provider(provider_name)
        available = "✓" if provider.check_available() else "✗"
        print(f"  {available} {provider}")


def list_models(provider_name: str):
    """List models for a provider.

    Args:
        provider_name: Provider name
    """
    try:
        provider = get_provider(provider_name)
        print(f"Available models for {provider_name}:")
        for model in provider.get_available_models():
            default = " (default)" if model == provider.get_default_model() else ""
            print(f"  - {model}{default}")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point for askai CLI."""
    try:
        # Parse arguments
        args = parse_args()
        validate_args(args)

        # Load configuration
        config = ConfigManager()

        # Handle info/config commands
        if args.list_providers:
            list_providers()
            return 0

        if args.list_models:
            list_models(args.list_models)
            return 0

        if args.config_path:
            print(f"Configuration file: {config.config_path}")
            return 0

        if args.config_show:
            print(config)
            return 0

        if args.config_reset:
            config.reset_to_defaults()
            print("Configuration reset to defaults")
            print(config)
            return 0

        # Determine provider and model
        provider_name = args.provider or config.get_default_provider()
        provider = get_provider(provider_name)

        # Check if provider is available
        if not provider.check_available():
            print(
                f"Error: {provider_name} CLI not found. Please install it first.",
                file=sys.stderr,
            )
            sys.exit(1)

        # Determine model
        model = args.model or config.get_default_model(provider_name) or provider.get_default_model()

        # Build command
        try:
            command = provider.build_command(args.prompt, model)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

        # Show command if verbose or dry-run
        if args.verbose or args.dry_run:
            print(f"Command: {' '.join(command)}", file=sys.stderr)

        if args.dry_run:
            return 0

        # Execute command
        result = subprocess.run(command, capture_output=False, text=True)
        return result.returncode

    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
