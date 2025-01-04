import re

from chatbot.core.models import ChannelMessage, PrivateMessage, UnclassifiedMessage

# E.g.: ':moonHarvest!moonHarves@Clk-E666DD8.skybroadband.com PRIVMSG #test_room :enjoy\r\n'
CHANNEL_MESSAGE_PATTERN = re.compile(r"^:(?P<sender>\S+) PRIVMSG (?P<channel>#\S+) :(?P<message>.+)\r\n$")


def format_channel_name(channel: str) -> str:
    if channel.startswith("#"):
        return channel
    return "#" + channel


def parse_message(full_message: str) -> ChannelMessage | PrivateMessage | UnclassifiedMessage:
    """
    Parse a message from the IRC server.
    """
    # Handle channel messages:
    match = re.match(CHANNEL_MESSAGE_PATTERN, full_message)
    if match:
        return ChannelMessage(
            sender=match.group("sender"),
            channel=match.group("channel"),
            message=match.group("message"),
        )

    # Handle private messages:
    # TODO

    # Handle channel messages:
    return UnclassifiedMessage(message=full_message)
