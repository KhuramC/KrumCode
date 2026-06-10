from pathlib import Path
import yaml
from enum import StrEnum
from pydantic import BaseModel, FilePath, model_validator, ValidationError
from dotenv import load_dotenv


class PathsConfig(BaseModel):
    repo_list_path: Path
    repo_dest_dir: Path
    database_dir: Path
    environment: Path


class LLMProvider(StrEnum):
    GOOGLE = "google"
    OPENAI = "openai"
    # ANTHROPIC= "anthropic"
    GROQ = "groq"
    # LOCAL = "local"

    @property
    def base_url(self) -> str:
        match self:
            case LLMProvider.GOOGLE:
                return "https://generativelanguage.googleapis.com/v1beta/openai"
            case LLMProvider.OPENAI:
                return "https://api.openai.com/v1"
            case LLMProvider.GROQ:
                return "https://api.groq.com/openai/v1"


class LLMConfig(BaseModel):
    provider: LLMProvider
    model_name: str


class OverallConfig(BaseModel):
    Paths: PathsConfig
    LLM: LLMConfig


config: OverallConfig | None = None


def get_backend_root() -> Path:
    """
    Returns the path to the backend root.

    Returns:
        Path: Path to backend root.
    """

    # .parent goes up to the 'core' folder, and the second .parent goes up to the root of the backend.
    return Path(__file__).resolve().parent.parent


def load_environment(paths: PathsConfig) -> None:
    """
    Loads the environment variables.
    """
    load_dotenv(dotenv_path=get_backend_root() / paths.environment)


def load_config() -> OverallConfig:
    """
    Loads the configuration from the YAML file specified in the backend root.

    Raises:
        FileNotFoundError: If the config file is not found in the backend root.
        ValueError: If the config file is not configured to the specifications above.

    Returns:
        OverallConfig: The loaded configuration.
    """
    global config
    if config is None:

        config_path: Path = get_backend_root() / "config.yaml"
        if not config_path.is_file():
            raise FileNotFoundError(
                f"Config file 'config.yaml' not found at {config_path}"
            )
        raw_config = yaml.safe_load(config_path.read_text()) or {}
        try:
            config = OverallConfig(**raw_config)
            load_environment(config.Paths)
            return config
        except ValidationError as e:
            raise ValueError(f"Configuration file is incorrectly configured: {e}")
    else:
        return config
