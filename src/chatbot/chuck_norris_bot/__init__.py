import asyncio

from chatbot import utils as chat_utils
from chatbot.bot_connection_instance import BotConnectionInstance
from chatbot.models import MessageType

from .jokes import get_chuck_norris_joke


class ChuckNorrisBot:
    JOKE_COMMAND = "!chuck"

    def __init__(self, conn: BotConnectionInstance, channels: list[str]):
        self._bot = conn
        self._channels = channels

    async def run(self) -> None:
        await self._bot.connect()
        await asyncio.gather(*(self._bot.join_channel(channel) for channel in self._channels))
        await self.handle_messages()

    async def handle_messages(self):
        async for message in self._bot.messages():
            parsed_message = chat_utils.parse_message(message)
            if (
                parsed_message.message_type == MessageType.CHANNEL_MESSAGE
                and parsed_message.message == self.JOKE_COMMAND
            ):
                joke = await get_chuck_norris_joke()
                await self._bot.send_message_to_channel(parsed_message.channel, joke)
