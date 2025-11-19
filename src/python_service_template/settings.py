import enum
import functools
import logging
import sys
import typing as t

import structlog
from asgi_correlation_id import correlation_id
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggingLevel(str, enum.Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LoggingConfig(BaseModel):
    level: LoggingLevel = Field(description="Logging level for the application")
    format: t.Literal["JSON", "PLAIN"] = Field(
        description="Logging output format - JSON for structured logs or PLAIN for console"
    )


class CoffeeApi(BaseModel):
    host: str = Field(description="Coffee API host URL")


class Settings(BaseSettings):
    host: str = Field(description="Host address to bind the server to")
    port: int = Field(description="Port number to run the server on")
    workers: int = Field(default=1, description="Number of worker processes")
    logging: LoggingConfig = Field(description="Logging configuration settings")
    coffee_api: CoffeeApi = Field(description="Coffee API configuration")
    app_version: str = Field(default="0.1.0", description="Application version", min_length=1)
    git_commit_sha: str = Field(default="sha", description="Git commit SHA", min_length=1)

    model_config = SettingsConfigDict(
        env_file=(".env.default", ".env"),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="allow",
    )


def add_correlation_id(_, __, event_dict):
    cid = correlation_id.get()
    if cid:
        event_dict["correlation_id"] = cid
    return event_dict


def add_application_version(app_version: str, _, __, event_dict):
    event_dict["version"] = app_version
    return event_dict


def add_git_commit(git_commit: str, _, __, event_dict):
    event_dict["git_commit"] = git_commit
    return event_dict


def configure_structlog(app_version: str, git_commit: str, config: LoggingConfig) -> None:
    log_level = logging._nameToLevel.get(config.level)
    if log_level is None:
        raise ValueError(f"Invalid logging level: {config.level}")

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            add_correlation_id,
            functools.partial(add_application_version, app_version),
            functools.partial(add_git_commit, git_commit),
            structlog.processors.EventRenamer(to="message"),
            structlog.processors.StackInfoRenderer(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure stdlib logging to use structlog's ProcessorFormatter
    timestamper = structlog.processors.TimeStamper(fmt="iso")
    pre_chain = [
        structlog.stdlib.add_log_level,
        timestamper,
    ]

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stderr,
        level=log_level,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.JSONRenderer()
            if config.format == "JSON"
            else structlog.dev.ConsoleRenderer(event_key="message"),
        ],
        foreign_pre_chain=pre_chain,  # type: ignore[arg-type]
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(log_level)


def create_std_logging_config(app_version: str, git_commit: str, config: LoggingConfig) -> dict[str, t.Any]:
    """Logging configuration for uvicorn using standard logging module.

    The main goal is to render the logs the same way as structlog does.

    See:
        https://www.structlog.org/en/stable/standard-library.html#rendering-using-structlog-based-formatters-within-logging
    """
    # For verbose loggers, use the maximum of WARNING or user's configured level
    # This ensures they're at least WARNING but respects higher levels like ERROR
    user_level = logging._nameToLevel.get(config.level.value, logging.INFO)
    verbose_logger_level = logging.getLevelName(max(logging.WARNING, user_level))

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "structlog": {
                "()": "structlog.stdlib.ProcessorFormatter",
                "foreign_pre_chain": [
                    structlog.processors.TimeStamper(fmt="iso"),
                    structlog.stdlib.add_log_level,
                    structlog.processors.StackInfoRenderer(),
                ],
                "processors": [
                    structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                    add_correlation_id,
                    functools.partial(add_application_version, app_version),
                    functools.partial(add_git_commit, git_commit),
                    structlog.processors.EventRenamer(to="message"),
                    structlog.processors.JSONRenderer()
                    if config.format == "JSON"
                    else structlog.dev.ConsoleRenderer(event_key="message"),
                ],
            },
        },
        "handlers": {
            "structlog": {
                "formatter": "structlog",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["structlog"],
                "level": config.level.value,
                "propagate": False,
            },
            "uvicorn.error": {"level": config.level.value},
            "uvicorn.access": {
                "handlers": ["structlog"],
                "level": config.level.value,
                "propagate": False,
            },
            # These are verbose loggers - set to minimum WARNING but respect higher user levels
            "httpx": {
                "handlers": ["structlog"],
                "level": verbose_logger_level,
                "propagate": False,
            },
            "httpcore": {
                "handlers": ["structlog"],
                "level": verbose_logger_level,
                "propagate": False,
            },
        },
    }
