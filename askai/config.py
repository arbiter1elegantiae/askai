"""Configuration management for askai.

This module handles loading, saving, and validating user configuration.
Configuration is stored in ~/.config/askai/config.json

Default configuration structure:
{
    "default_provider": "claude",
    "default_models": {
        "claude": "haiku",
        "gemini": "gemini-flash"
    },
    "max_response_words": 100
}
"""

import json
import os
from pathlib import Path
from typing import Any, Optional


class ConfigManager:
    """Manages askai configuration file.

    Handles reading/writing config from ~/.config/askai/config.json
    with sensible defaults and validation.
    """

    # Default configuration
    DEFAULT_CONFIG = {
        "default_provider": "claude",
        "default_models": {
            "claude": "haiku",
            "gemini": "gemini-flash",
        },
        "max_response_words": 100,
    }

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize configuration manager.

        Args:
            config_path: Optional custom config path (defaults to ~/.config/askai/config.json)
        """
        if config_path is None:
            # Use XDG_CONFIG_HOME if set, otherwise ~/.config
            config_home = os.environ.get("XDG_CONFIG_HOME")
            if config_home:
                base_path = Path(config_home)
            else:
                base_path = Path.home() / ".config"

            self.config_path = base_path / "askai" / "config.json"
        else:
            self.config_path = config_path

        self._config: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """Load configuration from file or create with defaults."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)

                # Merge loaded config with defaults (in case new keys are added)
                self._config = self._merge_with_defaults(loaded_config)

            except (json.JSONDecodeError, OSError) as e:
                # If config is corrupted, fall back to defaults
                print(f"Warning: Failed to load config from {self.config_path}: {e}")
                print("Using default configuration.")
                self._config = self.DEFAULT_CONFIG.copy()
        else:
            # No config file exists, use defaults
            self._config = self.DEFAULT_CONFIG.copy()
            # Optionally create the config file
            self._save()

    def _merge_with_defaults(self, loaded_config: dict[str, Any]) -> dict[str, Any]:
        """Merge loaded config with defaults to ensure all keys exist.

        Args:
            loaded_config: Configuration loaded from file

        Returns:
            Merged configuration with all required keys
        """
        merged = self.DEFAULT_CONFIG.copy()

        # Deep merge for nested dicts like default_models
        for key, value in loaded_config.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = {**merged[key], **value}
            else:
                merged[key] = value

        return merged

    def _save(self) -> None:
        """Save current configuration to file.

        Creates parent directories if they don't exist.
        Uses restrictive permissions (0o600) for security.
        """
        try:
            # Create config directory if it doesn't exist
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            # Write config with proper formatting
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, sort_keys=True)

            # Set restrictive permissions (user read/write only)
            os.chmod(self.config_path, 0o600)

        except OSError as e:
            print(f"Warning: Failed to save config to {self.config_path}: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: Configuration key (supports dot notation, e.g., 'default_models.claude')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        # Support dot notation for nested keys
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any, save: bool = True) -> None:
        """Set a configuration value.

        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
            save: Whether to persist to file immediately (default: True)
        """
        # Support dot notation for nested keys
        keys = key.split(".")
        config = self._config

        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]

        # Set the final key
        config[keys[-1]] = value

        if save:
            self._save()

    def get_default_provider(self) -> str:
        """Get the default provider name.

        Returns:
            Provider name (e.g., 'claude', 'gemini')
        """
        return self.get("default_provider", "claude")

    def get_default_model(self, provider: str) -> Optional[str]:
        """Get the default model for a specific provider.

        Args:
            provider: Provider name

        Returns:
            Model name or None if not configured
        """
        return self.get(f"default_models.{provider}")

    def set_default_provider(self, provider: str) -> None:
        """Set the default provider.

        Args:
            provider: Provider name
        """
        self.set("default_provider", provider)

    def set_default_model(self, provider: str, model: str) -> None:
        """Set the default model for a provider.

        Args:
            provider: Provider name
            model: Model name
        """
        self.set(f"default_models.{provider}", model)

    def get_max_response_words(self) -> int:
        """Get the maximum response words setting.

        Returns:
            Maximum words for concise responses
        """
        return self.get("max_response_words", 100)

    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults and save."""
        self._config = self.DEFAULT_CONFIG.copy()
        self._save()

    def __str__(self) -> str:
        """String representation of current configuration."""
        return json.dumps(self._config, indent=2)

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"<ConfigManager: {self.config_path}>"
