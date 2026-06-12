import logging
from enum import StrEnum
from pathlib import Path
from typing import Annotated

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, FilePath, ValidationError
from pydantic.networks import IPvAnyAddress

logger = logging.getLogger("utils")


class PathsConfig(BaseModel):
    """
    The configuration for the necessary paths. The files need to exist when loaded in. The directories do not.
    """

    repo_list_path: FilePath
    env_path: FilePath
    repo_dest_dir: Path
    database_dir: Path


class LLMProvider(StrEnum):
    """
    Supported LLM providers and their associated URLs for accessing their APIs.
    """

    GOOGLE = "google"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    LOCAL = "local"

    @property
    def base_url(self) -> str:
        match self:
            case LLMProvider.GOOGLE:
                return "https://generativelanguage.googleapis.com/v1beta/openai"
            case LLMProvider.OPENAI:
                return "https://api.openai.com/v1"
            case LLMProvider.ANTHROPIC:
                # TODO: look into edge case with anthropic with the API
                return ""
            case LLMProvider.GROQ:
                return "https://api.groq.com/openai/v1"
            case LLMProvider.LOCAL:
                # TODO: add extra thing in config for the url for local LLMs.
                # test with ollama?
                return ""


class LLMConfig(BaseModel):
    """
    The configuration for the LLM.
    """

    provider: LLMProvider
    model_name: str


class ServerConfig(BaseModel):
    """
    The configuration for the backend server.
    """

    host: IPvAnyAddress
    port: Annotated[int, Field(ge=1, le=65535)]
    development: bool  # whether to deploy for development or not.


class LoggingLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class PackageLevels(BaseModel):
    """
    The logging levels associated with each subdirectory/package.
    """

    api: LoggingLevel = LoggingLevel.INFO
    rag: LoggingLevel = LoggingLevel.INFO
    utils: LoggingLevel = LoggingLevel.WARNING


class LoggingConfig(BaseModel):
    """Configuration for logging."""

    show_time: bool = True
    levels: PackageLevels = PackageLevels()


class OverallConfig(BaseModel):
    """
    The overall configuration for the RAG/backend. Given by the YAML file.
    """

    Paths: PathsConfig
    LLM: LLMConfig
    Server: ServerConfig
    Logging: LoggingConfig


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
    load_dotenv(dotenv_path=get_backend_root() / paths.env_path)


def load_config() -> OverallConfig:
    """
    Loads the configuration from the YAML file specified in the backend root.

    Raises:
        FileNotFoundError: If the config file is not found in the backend root.
        ValueError: If the config file is not configured to the specifications above.

    Returns:
        OverallConfig: The loaded configuration.
    """

    config_path: Path = get_backend_root() / "config.yaml"
    if not config_path.is_file():
        raise FileNotFoundError(f"Config file 'config.yaml' not found at {config_path}")
    raw_config = yaml.safe_load(config_path.read_text()) or {}
    try:
        config = OverallConfig(**raw_config)
        load_environment(config.Paths)
        configure_logging(config.Logging)
        return config
    except ValidationError as e:
        raise ValueError(f"Configuration file is incorrectly configured: {e}") from None


# global config instance
_config: OverallConfig | None = None


def get_config() -> OverallConfig:
    """
    Loads the configuration from the YAML file specified in the backend root.

    Raises:
        FileNotFoundError: If the config file is not found in the backend root.
        ValueError: If the config file is not configured to the specifications above.

    Returns:
        OverallConfig: The loaded configuration.
    """
    if _config is None:
        return load_config()
    else:
        return _config


def configure_logging(config: LoggingConfig) -> None:
    """
    Configures the logging based on the configuration.
    """
    log = "%(asctime)s " if config.show_time else ""
    log += "[%(levelname)s] %(name)s: %(message)s"

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(log))

    for name, level in (
        ("api", config.levels.api),
        ("rag", config.levels.rag),
        ("utils", config.levels.utils),
    ):
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)
