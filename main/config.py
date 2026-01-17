"""Configuration management for the phabricator-review tool."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .constants import CONFIG_DIR_NAME, CONFIG_FILE_NAME


@dataclass
class Config:
    """Application configuration."""
    phabricator_url: str
    phabricator_api_token: str
    openrouter_api_key: str
    model: Optional[str] = None


def get_config_path() -> Path:
    """Get the path to the config file."""
    config_dir = os.environ.get("XDG_CONFIG_HOME")
    if not config_dir:
        config_dir = Path.home() / ".config"
    else:
        config_dir = Path(config_dir)
    
    return config_dir / CONFIG_DIR_NAME / CONFIG_FILE_NAME


def load_dotenv_file(path: Path) -> dict[str, str]:
    """Load a .env file and return a dict of key-value pairs."""
    env_vars = {}
    if not path.exists():
        return env_vars
    
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                env_vars[key.strip()] = value.strip()
    
    return env_vars


def load_config() -> Config:
    """Load configuration from config file and environment variables."""
    # Load from config file first
    config_path = get_config_path()
    config_vars = load_dotenv_file(config_path)
    
    # Load from local .env file (overrides config file)
    local_env = Path.cwd() / ".env"
    local_vars = load_dotenv_file(local_env)
    config_vars.update(local_vars)
    
    # Environment variables override everything
    phabricator_url = os.environ.get("PHABRICATOR_URL") or config_vars.get("PHABRICATOR_URL", "")
    phabricator_api_token = os.environ.get("PHABRICATOR_API_TOKEN") or config_vars.get("PHABRICATOR_API_TOKEN", "")
    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY") or config_vars.get("OPENROUTER_API_KEY", "")
    model = os.environ.get("REVIEW_MODEL") or config_vars.get("REVIEW_MODEL")
    
    # Validate required fields
    missing = []
    if not phabricator_url:
        missing.append("PHABRICATOR_URL")
    if not phabricator_api_token:
        missing.append("PHABRICATOR_API_TOKEN")
    if not openrouter_api_key:
        missing.append("OPENROUTER_API_KEY")
    
    if missing:
        raise ValueError(
            f"Missing required configuration: {', '.join(missing)}. "
            f"Run 'phabreview config' to set them."
        )
    
    return Config(
        phabricator_url=phabricator_url,
        phabricator_api_token=phabricator_api_token,
        openrouter_api_key=openrouter_api_key,
        model=model,
    )


def save_config(
    phabricator_url: str,
    phabricator_api_token: str,
    openrouter_api_key: str,
    model: Optional[str] = None,
) -> Path:
    """Save configuration to the config file."""
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    
    lines = [
        f"PHABRICATOR_URL={phabricator_url}",
        f"PHABRICATOR_API_TOKEN={phabricator_api_token}",
        f"OPENROUTER_API_KEY={openrouter_api_key}",
    ]
    
    if model:
        lines.append(f"REVIEW_MODEL={model}")
    
    config_path.write_text("\n".join(lines) + "\n")
    config_path.chmod(0o600)
    
    return config_path
