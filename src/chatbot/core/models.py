from enum import StrEnum
from typing import Literal

from pydantic import BaseModel


class MessageType(StrEnum):
    PRIVATE_MESSAGE = "private_message"
    CHANNEL_MESSAGE = "channel_message"
    UNCLASSIFIED_MESSAGE = "unclassified"


class PrivateMessage(BaseModel):
    message_type: Literal[MessageType.PRIVATE_MESSAGE] = MessageType.PRIVATE_MESSAGE
    sender: str
    recipient: str
    message: str


class ChannelMessage(BaseModel):
    message_type: Literal[MessageType.CHANNEL_MESSAGE] = MessageType.CHANNEL_MESSAGE
    sender: str
    channel: str
    message: str


class UnclassifiedMessage(BaseModel):
    message_type: Literal[MessageType.UNCLASSIFIED_MESSAGE] = MessageType.UNCLASSIFIED_MESSAGE
    message: str
