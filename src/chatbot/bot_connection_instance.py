import asyncio
import logging
from typing import AsyncGenerator

from . import utils as chat_utils

logger = logging.getLogger(__name__)

RECONNECT_WAIT_TIME = 1


class BotConnectionInstance:
    """
    TODO: Implement registration protocol
    TODO: Implement logging in, at least into UnrealIRCD
    TODO: Implement aliases (signing in with nickname, but using alias)
    TODO: Implement _disconnected event / re-connection
    TODO: Implement proper logging
    TODO: Implement message throtling
    TODO: Handle re-join channels on re-connect
    """

    _server: str
    _port: int
    _nickname: str
    _connected: asyncio.Event
    _incoming_message_queues: list[asyncio.Queue]
    _incoming_message_queues_lock: asyncio.Lock
    _outgoing_message_queue: asyncio.Queue
    _reader: asyncio.StreamReader | None = None
    _writer: asyncio.StreamWriter | None = None
    _channels: list[str] = []

    def __init__(
        self,
        *,
        server: str,
        port: int,
        nickname: str,
    ):
        self._server = server
        self._port = port
        self._nickname = nickname
        self._connected = asyncio.Event()
        self._incoming_message_queues = []
        self._incoming_message_queues_lock = asyncio.Lock()
        self._outgoing_message_queue = asyncio.Queue()

    async def connect(self, alias: str | None = None):
        """
        Connect to the IRC server.
        """
        print(f"Connecting to {self._server} on port {self._port}...")

        if self._reader and self._writer:
            logger.warning("Already connected to the server")
        else:
            self._reader, self._writer = await asyncio.open_connection(self._server, self._port)

        await self._send_registration(alias)
        asyncio.create_task(self._communicate())
        await self._connected.wait()

    async def join_channel(self, channel: str) -> None:
        """
        Join a channel on the server.
        """
        if not channel.startswith("#"):
            channel = "#" + channel
        self._channels.append(chat_utils.format_channel_name(channel))
        await self._write(f"JOIN {channel}")

    async def leave_channel(self, channel: str) -> None:
        """
        Leave a channel on the server.
        """
        self._channels.remove(chat_utils.format_channel_name(channel))
        await self._write(f"PART {channel}")

    async def send_message_to_channel(self, channel: str, message: str):
        """
        Enqueue a message to be sent to the channel.
        """
        await self._outgoing_message_queue.put(f"PRIVMSG {channel} :{message}")

    async def messages(self) -> AsyncGenerator[str, None]:
        """
        Yield messages from the server.
        """
        queue: asyncio.Queue = asyncio.Queue()

        try:
            async with self._incoming_message_queues_lock:
                self._incoming_message_queues.append(queue)
            while True:
                message = await queue.get()
                yield message
                queue.task_done()
                # XXX: Can probably be handled better
                await asyncio.sleep(0.1)
        finally:
            async with self._incoming_message_queues_lock:
                self._incoming_message_queues.remove(queue)

    async def _write(self, *messages: str):
        """
        Write a message to the server.
        """
        if not self._writer:
            raise ConnectionError("Not connected to the server")

        for message in messages:
            self._writer.write(f"{message}\r\n".encode())

        await self._writer.drain()

    async def _communicate(self) -> None:
        """
        Communicate with the server.
        """
        await asyncio.gather(
            # Listen to incoming messages:
            self._listen_to_incoming_messages(),
            # Process messages from the queue:
            self._listen_to_outgoing_messages(),
        )

    async def _send_registration(self, alias: str | None = None):
        """
        Send NICK and USER messages to register the bot.
        """
        nickname = alias or self._nickname
        await self._write(
            f"NICK {nickname}",
            f"USER {nickname} 0 * :{nickname}",
        )

    async def _listen_to_incoming_messages(self) -> None:
        """
        Listen to incoming messages and respond accordingly.
        """
        while True:
            # TODO: Handle reader not defined
            data = await self._reader.read(1024)
            if data:
                message = data.decode("utf-8")
                print(f"Received: {message}")

                if message.startswith(":"):
                    parts = message.split()
                    if parts[1] in ["001", "376", "422"]:
                        server_name = parts[0][1:]
                        print(f"Connected to server: {server_name}")
                        self._connected.set()

                # Respond to PING from the server to keep the connection alive:
                if message.startswith("PING"):
                    await self._write(f"PONG {message.split()[1]}")

                # All the other messages are to be sent to the consumers:
                async with self._incoming_message_queues_lock:
                    await asyncio.gather(*(queue.put(message) for queue in self._incoming_message_queues))

    async def _listen_to_outgoing_messages(self) -> None:
        """
        Process messages from the message queue and send them to the server.
        """
        while True:
            message = await self._outgoing_message_queue.get()
            if message is None:  # Exit condition
                break
            await self._write(message)
            print(f"Consumed: {message}")
            self._outgoing_message_queue.task_done()  # Indicate item has been processed
