"""Base provider interface for LLM CLI adapters.

This module defines the abstract interface that all provider adapters must implement.
Each provider translates askai requests into the appropriate CLI command for that
provider's tool (e.g., claude, gemini).
"""

from abc import ABC, abstractmethod


class Provider(ABC):
    """Abstract base class for LLM provider adapters.

    Each provider adapter is responsible for:
    1. Translating prompts into provider-specific CLI commands
    2. Managing model selection (with sensible defaults for concise responses)
    3. Checking if the provider's CLI tool is installed
    4. Enforcing context-free, concise response constraints
    """

    @abstractmethod
    def build_command(self, prompt: str, model: str | None = None) -> list[str]:
        """Build the CLI command to execute for this provider.

        This method should construct a command that:
        - Is context-free (no conversation history)
        - Requests concise responses (< 100 words)
        - Uses the specified model or default

        Args:
            prompt: The user's question/prompt
            model: Optional model override (uses default if None)

        Returns:
            List of command arguments suitable for subprocess.run()
            Example: ["claude", "--no-context", "--model", "haiku", "prompt here"]

        Raises:
            ValueError: If the model is not supported by this provider
        """
        pass

    @abstractmethod
    def get_default_model(self) -> str:
        """Get the default model for concise responses.

        This should be a fast, lightweight model suitable for quick answers.
        Examples: 'haiku' for Claude, 'gemini-flash' for Gemini

        Returns:
            Model identifier string
        """
        pass

    @abstractmethod
    def get_available_models(self) -> list[str]:
        """Get list of available models for this provider.

        Returns:
            List of model identifiers that can be passed to build_command()
            Example: ['haiku', 'sonnet', 'opus'] for Claude
        """
        pass

    @abstractmethod
    def check_available(self) -> bool:
        """Check if this provider's CLI tool is installed and available.

        This should verify that the required CLI tool is in PATH and executable.
        Example: Check if 'claude' command exists for Claude provider

        Returns:
            True if provider CLI is available, False otherwise
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the provider name.

        Returns:
            Provider name identifier (e.g., 'claude', 'gemini')
            This should be lowercase and match the CLI command name
        """
        pass

    def validate_model(self, model: str) -> bool:
        """Validate if a model is supported by this provider.

        Args:
            model: Model identifier to validate

        Returns:
            True if model is supported, False otherwise
        """
        return model in self.get_available_models()

    def __str__(self) -> str:
        """String representation of the provider."""
        return f"{self.name} (default: {self.get_default_model()})"

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"<Provider: {self.name}>"
