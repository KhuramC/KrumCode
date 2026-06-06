from pathlib import Path
import configparser

# Default Configuration
DEFAULT_REPO_FILE = "./repos.txt"  # File containing list of repo URLS
DEFAULT_DEST_DIR = "./data/repos"  # Directory where repos will be cloned or updated


def get_project_root() -> Path:
    """
    Returns the path to the project root.

    Returns:
        Path: path to project root.
    """

    # .parent goes up to the 'core' folder, and the second .parent goes up to the root.
    return Path(__file__).resolve().parent.parent


def load_config() -> configparser.ConfigParser:
    """
    Loads the configuration from the file specified in the project root.

    Raises:
        FileNotFoundError: If the config file is not found in the project root.

    Returns:
        configparser.ConfigParser: The loaded configuration parser.
    """

    config = configparser.ConfigParser()
    config_path = get_project_root() / "config.cfg"
    if config.read(config_path):
        return config
    raise FileNotFoundError("Config file not found.")


def get_repo_file(config: configparser.ConfigParser) -> Path:
    return get_project_root() / config.get(
        "Paths", "REPO_FILE", fallback=DEFAULT_REPO_FILE
    )


def get_dest_dir(config: configparser.ConfigParser) -> Path:
    return get_project_root() / config.get(
        "Paths", "DEST_DIR", fallback=DEFAULT_DEST_DIR
    )
