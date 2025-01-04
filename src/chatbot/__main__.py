import asyncio

from chatbot.chuck_norris_bot import ChuckNorrisBot
from chatbot.core import BotConnectionInstance
from chatbot.core.config import ChatBotConfig
from chatbot.core.log_config import setup_logging


async def amain() -> None:
    config = ChatBotConfig()
    setup_logging(config.log_location, config.log_level)
    conn = BotConnectionInstance(
        server=config.irc_server,
        port=config.irc_port,
        nickname=config.irc_nickname,
    )
    chuck_norris_bot = ChuckNorrisBot(conn, config.irc_channels)
    await chuck_norris_bot.run()


def main() -> None:
    asyncio.run(amain())


if __name__ == "__main__":
    main()
