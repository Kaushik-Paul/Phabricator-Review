# Phabricator Review CLI

**Automate your code reviews with LLM-powered precision.**

Phabricator Review CLI is a powerful, extensible tool designed to bring modern AI analysis to your Phabricator workflow. It goes beyond simple diff viewing by providing deep, context-aware feedback on legacy and modern codebases alike. Whether you're dealing with the quirks of Python 2.7, complex AngularJS scopes, or intricate CSS architectures, this CLI acts as an tireless expert reviewer, catching bugs, enforcing best practices, and saving hours of manual effort.

## Why Phabricator Review?

- **Deep Context Analysis**: Understands cross-file implications and legacy framework patterns.
- **Enforces Organizational Standards**: Automatically flags magic values, hardcoded colors, and deprecated patterns.
- **Actionable Feedback**: Provides precise line-level suggestions with code snippets for immediate fixes.
- **Seamless Workflow Integration**: Generates detailed, shareable Markdown reports in seconds.
- **Extensible & Configurable**: Works with any OpenRouter-supported model, tailored to your specific stack.

## Features

- Fetch revision metadata, raw diff, and grouped change summaries
- Generate LLM reviews with file paths, line numbers, and code snippets
- `--only-review` flag to print just the review section
- `--save-review` flag to save detailed markdown report with code snippets
- `--model` flag to override LLM model at runtime
- Interactive `config` command to persist credentials
- Colored terminal output for easier scanning
- Specialized prompts for Python 2.7, AngularJS, jQuery, CSS/LESS, and Jinja2

## Installation

### Global Installation (recommended for use from any directory)

```bash
# Install globally with pipx (works from any directory)
pipx install /home/kaushik/Kaushik/Projects/phabricator-review

# Or add to your shell profile (~/.bashrc or ~/.zshrc):
alias phabreview='/home/kaushik/Kaushik/Projects/phabricator-review/.venv/bin/phabreview'
```

### Local Development

```bash
cd /home/kaushik/Kaushik/Projects/phabricator-review
uv sync

# Run with uv (from project directory only)
uv run phabreview D12345
```

## Configuration

First-time setup stores credentials in `~/.config/phab-reviewer/config.env`:

```bash
phabreview config
```

Or provide values via flags:

```bash
phabreview config \
  --phabricator-url=https://phab.example.com/api/ \
  --phabricator-token=cli-xxxx \
  --openrouter-key=sk-or-xxxx \
  --model=anthropic/claude-sonnet-4
```

### Required Environment Variables

- `PHABRICATOR_URL` - Phabricator Conduit API base URL
- `PHABRICATOR_API_TOKEN` - Phabricator API token
- `OPENROUTER_API_KEY` - OpenRouter API key

### Optional

- `REVIEW_MODEL` - LLM model to use (default from constants)

## Usage

Review a revision:

```bash
phabreview D33113
```

Review with only the LLM output:

```bash
phabreview --only-review D33113
```

Generate a markdown review file (saved to `~/Documents/Phabreview/`):

```bash
phabreview --save-review D33113
```

Override the LLM model for a single review:

```bash
phabreview --model anthropic/claude-sonnet-4 D33113
```

Display help:

```bash
phabreview --help
```

## Environment Override

You can provide credentials via:
1. Environment variables (highest priority)
2. Local `.env` file in current directory
3. Config file at `~/.config/phab-reviewer/config.env`

## Customization

The LLM reviewer can be tailored to your specific needs by modifying the prompts in `main/prompts.py`. Adjust the review guidelines to match your organization's coding standards and technology stack.

## License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## Acknowledgements

This project is a Python-based evolution inspired by the original [phabReview](https://github.com/bogusdeck/phabReview)
