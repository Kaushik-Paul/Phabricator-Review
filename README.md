# Phabricator Review CLI

LLM-powered code review for Phabricator revisions using OpenRouter.

## Features

- Fetch revision metadata, raw diff, and grouped change summaries
- Generate LLM reviews with file paths, line numbers, and code snippets
- `--only-review` flag to print just the review section
- `--generate-review` flag to save detailed markdown report with code snippets
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
phabreview --generate-review D33113
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

## Review Rules

The LLM reviewer enforces these organization-specific guidelines:

- **CSS Colors**: No hardcoded `#` color literals - use `colors.less` variables
- **Magic Values**: Extract to shared constants across HTML/CSS/JS
- **Tooltip Text**: Define as constants, not inline strings
- **Duplicate Constants**: Consolidate to single shared location
- **Python 2.7**: Proper unicode handling, print statements, exception syntax, mutable defaults
- **AngularJS**: Dependency injection, scope management, directive usage, $rootScope avoidance
- **jQuery**: Avoid deprecated methods, prevent memory leaks, cache selectors
- **Jinja2**: Proper escaping, macro usage, template inheritance

## License

[MIT](LICENSE)

## Acknowledgements

This project is a Python port inspired by [phabReview](https://github.com/bogusdeck/phabReview).
