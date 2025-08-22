import yaml
import platform
from pathlib import Path

def get_config_dir():
    """Get OS-appropriate config directory"""
    system = platform.system()
    if system == "Windows":
        return Path.home() / "AppData" / "Local" / "Screenie"
    elif system == "Darwin":
        return Path.home() / "Library" / "Application Support" / "Screenie"
    else:
        return Path.home() / ".config" / "screenie"


def get_config():
    """Load config from file - returns None if not found"""
    config_dir = get_config_dir()
    config_file = config_dir / "config.yaml"
    
    if not config_file.exists():
        return None
        
    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except (yaml.YAMLError, FileNotFoundError):
        return None


def get_provider_config(provider_name=None):
    """Get provider config from LiteLLM-style config"""
    config = get_config()
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
