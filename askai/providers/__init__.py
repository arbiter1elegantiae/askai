"""Provider adapters for different LLM CLIs.

This package contains the base Provider interface and concrete implementations
for various LLM providers (Claude, Gemini, etc.).
"""

from askai.providers.base import Provider

__all__ = ["Provider"]
