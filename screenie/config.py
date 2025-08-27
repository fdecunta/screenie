import os
import platform
from pathlib import Path
import tomllib


def create_config_file(config_file):
    """Create config file with API keys"""
    config_template = """\
# Configuration file for API keys and endpoints.
#
# - Section headers (inside [brackets]) MUST match the model names used in your recipes.
# - The keys (API_KEY, endpoint, etc.) must match what LiteLLM expects.
# - Refer to LiteLLM provider docs for the required values:
#   https://docs.litellm.ai/docs/providers
#
# Example: If your recipe calls "openai/gpt-4o", you need a section [openai/gpt-4o]
# below with a valid OPENAI_API_KEY.

["openai/gpt-4o"]
# Replace with your OpenAI API key.
OPENAI_API_KEY = "your-api-key"

["anthropic/claude-opus-4-20250514"]
# Replace with your Anthropic API key.
ANTHROPIC_API_KEY = "your-api-key"

["gradient_ai/llama3.3-70b-instruct"]
# Replace with your Gradient AI key.
GRADIENT_AI_API_KEY = "your-api-key"

["xai/grok-3-mini-beta"]
# Replace with your xAI key.
XAI_API_KEY = "your-api-key"
"""

    with open(config_file, "w") as f:
        f.write(config_template)


def get_config_dir():
    """Get OS-appropriate config directory. Create if not exist"""
    system = platform.system()
    if system == "Windows":
        config_dir = Path.home() / "AppData" / "Local" / "Screenie"
    elif system == "Darwin":
        config_dir = Path.home() / "Library" / "Application Support" / "Screenie"
    else:
        config_dir = Path.home() / ".config" / "screenie"

    if not config_dir.exists():
        config_dir.mkdir()

    return config_dir


def get_config_file() -> Path:
    """Get path to configuration file"""
    config_dir = get_config_dir()
    config_file = config_dir / "config.toml"

    if not config_file.exists():
        create_config_file(config_file)

    return config_file


def load_config() -> str:
    """Read config file"""
    config_file = get_config_file()

    if not config_file.exists():
        create_config_file(config_file)

    with open(config_file, 'rb') as f:
        return tomllib.load(f)


def load_model_keys(model: str):
    """Get provider config from LiteLLM-style config"""
    config = load_config()
        
    if not config:
        raise ValueError("No configuration file found")
    
    for key, value in config[model].items():
        os.environ[key] = value

