# askai

A simple CLI tool for context-free, one-shot LLM queries with concise answers.

## Installation

**Requirements:** Python 3.12+

```bash
# With uv (recommended)
uv pip install -e .

# With pip
pip install -e .
```

## Features

- **Simple**: Single command execution, no conversation history
- **Fast**: Optimized for quick answers (< 100 words by default)
- **Flexible**: Switch between providers and models easily
- **Secure**: Input validation and safe subprocess execution
- **Configurable**: Persistent preferences in `~/.config/askai/config.json`

## Usage

### Basic Commands

```bash
askai "your question"              # Use defaults
askai -p gemini "your question"    # Choose provider
askai -m haiku "your question"     # Choose model
```

### Information Commands

```bash
askai --list-providers             # Show available providers
askai --list-models claude         # Show models for provider
askai --config-show                # Display current configuration
askai --config-path                # Show config file location
askai --version                    # Show version
```

### Utility Flags

```bash
askai -v "question"                # Verbose (show command)
askai --dry-run "question"         # Preview without executing
```

## Configuration

Configuration is stored in `~/.config/askai/config.json`:

```json
{
  "default_provider": "claude",
  "default_models": {
    "claude": "haiku"
  },
  "max_response_words": 100
}
```

Edit this file directly or use:
```bash
askai --config-show                # View current config
askai --config-reset               # Reset to defaults
```

## Supported Providers

### Claude (Anthropic)

**Requirements:** [Claude Code CLI](https://claude.com/claude-code) installed and configured

**Available models:**
- `haiku` - Claude Haiku 4.5 (fastest, default)
- `sonnet` - Claude Sonnet 4.5 (most capable)
- `opus` - Claude Opus 4.1 (complex reasoning)

**Aliases supported:** `haiku-4-5`, `sonnet-4`, `opus-4-1`, etc.

### Gemini (Google)

*Coming in v0.2.0*

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Roadmap

- [x] v0.1.0 - Claude provider support
- [ ] v0.2.0 - Gemini provider support
- [ ] v0.3.0 - OpenAI provider support
- [ ] v1.0.0 - Stable release with full test coverage
