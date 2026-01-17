"""Constants for the phabricator-review tool."""

from pathlib import Path

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

DEFAULT_MODEL = "xiaomi/mimo-v2-flash:free"

# Terminal colors
COLOR_TITLE = "\033[96m"
COLOR_SECTION = "\033[95m"
COLOR_ADD = "\033[32m"
COLOR_REMOVE = "\033[31m"
COLOR_NOTICE = "\033[93m"
COLOR_RESET = "\033[0m"

# Config directory name
CONFIG_DIR_NAME = "phab-reviewer"
CONFIG_FILE_NAME = "config.env"

# Review output directory
REVIEW_OUTPUT_DIR = str(Path.home() / "Documents" / "Phabreview")
