from pathlib import Path
from typing import Any
import yaml


def get_backend_root() -> Path:
    """
    Returns the path to the backend root.

    Returns:
        Path: path to backend root.
    """

    # .parent goes up to the 'core' folder, and the second .parent goes up to the root of the backend.
    return Path(__file__).resolve().parent.parent


def load_config() -> dict[str, Any]:
    """
    Loads the configuration from the YAML file specified in the backend root.

    Raises:
        FileNotFoundError: If the config file is not found in the backend root.
        ValueError: If the config file is empty.

    Returns:
        dict[str, Any]: The loaded configuration.
    """

    config_path: Path = get_backend_root() / "config.yaml"
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
            if config is None:
                raise ValueError("Config file 'config.yaml' is empty.")
            return config
    except FileNotFoundError:
        raise FileNotFoundError("Config file 'config.yaml' not found.")


def get_paths(config: dict[str, Any]) -> dict[str, Path]:
    path_config = config.get("Paths")
    new_path_config = {}
    for path_name, path_value in path_config.items():
        new_path_config[path_name] = Path(path_value)
        
    return new_path_config


def get_llm_config(config: dict[str, Any]) -> dict[str, Any]:
    return config.get("LLM")
