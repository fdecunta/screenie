import yaml
import platform
from pathlib import Path


def create_config_file(config_file):
    """
    Create config file following the format used by Litellm
    https://docs.litellm.ai/docs/proxy/configs
    """
    config_template = {
        "default": "openai-gpt-4",
        "model_list": [
            {
                "model_name": "openai-gpt-4",
                "litellm_params": {
                    "model": "gpt-4",
                    "api_key": "sk-your-openai-key-here"
                }
            },
            {
                "model_name": "anthropic-claude",
                "litellm_params": {
                    "model": "claude-3-sonnet",
                    "api_key": "your-anthropic-key-here"
                }
            },
            {
                "model_name": "DigitalOcean-llama3.3",
                "litellm_params": {
                    "model": "gradient_ai/llama3.3-70b-instruct",
                    "api_key": "DigitalOcean-endpoint-inference-key"
                }
            }
        ]
    }

    with open(config_file, "w") as f:
        yaml.dump(config_template, f, default_flow_style=False, sort_keys=False)


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


def get_config_file():
    """Get path to configuration file"""
    config_dir = get_config_dir()
    config_file = config_dir / "config.yaml"

    if not config_file.exists():
        create_config_file(config_file)

    return config_file


def read_config_file():
    """Read config file"""
    config_file = get_config_file()

    if not config_file.exists():
        create_config_file(config_file)
    
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)


def get_model_config(provider_name=None):
    """Get provider config from LiteLLM-style config"""
    config = read_config_file()
    if not config:
        raise ValueError("No configuration file found")
    
    if "model_list" not in config:
        raise ValueError("No model_list found in configuration")
    
    if "default" not in config:
        raise ValueError("No default provider specified in configuration")
    
    # Use specified provider or the configured default
    provider_name = provider_name or config["default"]
    
    # Find the provider
    for model_config in config["model_list"]:
        if model_config["model_name"] == provider_name:
            provider_config = model_config["litellm_params"].copy()
            provider_config["name"] = model_config["model_name"]
            return provider_config
    
    raise ValueError(f"Provider '{provider_name}' not found in configuration")
