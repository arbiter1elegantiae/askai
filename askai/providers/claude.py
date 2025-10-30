"""Claude provider adapter for Claude Code CLI.

This module implements the Provider interface for Anthropic's Claude Code CLI tool.
It translates askai requests into appropriate claude commands with model selection
and concise response constraints.
"""

import shutil
from typing import Optional

from askai.providers.base import Provider


class ClaudeProvider(Provider):
    """Provider adapter for Claude Code CLI.

    Supports Claude models: haiku (default), sonnet, opus
    Command format: claude [options] "prompt"
    """

    # Model mappings - using latest Claude 4.5 series (as of October 2025)
    MODELS = {
        "haiku": "claude-haiku-4-5-20251001",      # Haiku 4.5 - fastest, most cost-effective
        "sonnet": "claude-sonnet-4-5-20250929",    # Sonnet 4.5 - most capable
        "opus": "claude-opus-4-1-20250805",        # Opus 4.1 - complex reasoning
    }

    # Shorter aliases for convenience
    MODEL_ALIASES = {
        "haiku": "haiku",
        "sonnet": "sonnet",
        "opus": "opus",
        "haiku-4": "haiku",
        "haiku-4-5": "haiku",
        "4-5-haiku": "haiku",
        "sonnet-4": "sonnet",
        "sonnet-4-5": "sonnet",
        "4-5-sonnet": "sonnet",
        "opus-4": "opus",
        "opus-4-1": "opus",
        "4-1-opus": "opus",
    }

    @property
    def name(self) -> str:
        """Get the provider name."""
        return "claude"

    def get_default_model(self) -> str:
        """Get the default model for concise responses.

        Returns haiku as it's the fastest, most cost-effective model
        for quick, context-free queries.
        """
        return "haiku"

    def get_available_models(self) -> list[str]:
        """Get list of available Claude models.

        Returns:
            List of model identifiers (short names)
        """
        return list(self.MODELS.keys())

    def check_available(self) -> bool:
        """Check if Claude Code CLI is installed and available.

        Returns:
            True if 'claude' command is found in PATH
        """
        return shutil.which("claude") is not None

    def _resolve_model(self, model: Optional[str]) -> str:
        """Resolve model alias to canonical model identifier.

        Args:
            model: Model name or alias (e.g., 'haiku', 'sonnet-4-5')

        Returns:
            Full model identifier for Claude API

        Raises:
            ValueError: If model is not recognized
        """
        if model is None:
            model = self.get_default_model()

        # Normalize to lowercase
        model = model.lower()

        # Try alias resolution first
        if model in self.MODEL_ALIASES:
            model = self.MODEL_ALIASES[model]

        # Check if it's a valid model
        if model not in self.MODELS:
            raise ValueError(
                f"Unknown model '{model}'. Available: {', '.join(self.get_available_models())}"
            )

        return self.MODELS[model]

    def build_command(self, prompt: str, model: Optional[str] = None) -> list[str]:
        """Build the Claude CLI command.

        Constructs a command that:
        - Uses specified or default model
        - Requests concise responses (via prompt engineering)
        - Is context-free (Claude Code is stateless by default for single commands)

        Args:
            prompt: The user's question/prompt
            model: Optional model override (e.g., 'haiku', 'sonnet', 'opus')

        Returns:
            List of command arguments for subprocess

        Raises:
            ValueError: If model is not supported

        Example:
            >>> provider = ClaudeProvider()
            >>> provider.build_command("What is Python?", "haiku")
            ['claude', '--model', 'claude-haiku-4-5-20251001',
             'Answer concisely in under 100 words: What is Python?']
        """
        model_id = self._resolve_model(model)

        # Prepend instruction for concise responses to the prompt
        concise_prompt = f"Answer concisely in under 100 words: {prompt}"

        # Build command
        # Note: claude command format is: claude [options] "prompt"
        command = [
            "claude",
            "--model", model_id,
            concise_prompt
        ]

        return command

    def __str__(self) -> str:
        """String representation showing available models."""
        models = ", ".join(self.get_available_models())
        return f"claude (default: {self.get_default_model()}, available: {models})"
