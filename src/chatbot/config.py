from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .log_config import LogLevel


class ChatBotConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
        case_sensitive=False,
        env_prefix="CHATBOT__",
        env_nested_delimiter="__",
        frozen=True,
    )

    # Logging:
    log_location: str = Field(default="chatbot.log")
    log_level: LogLevel = Field(default="INFO")

    # ChatBot data:
    irc_server: str
    irc_port: int = Field(default=6667)
    irc_nickname: str
    irc_channels: list[str]
