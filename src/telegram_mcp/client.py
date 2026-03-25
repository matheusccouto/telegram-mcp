"""Telegram client wrapper using Hydrogram for MTProto communication."""

from __future__ import annotations

import logging
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from hydrogram import Client
from hydrogram.errors import SessionPasswordNeeded

if TYPE_CHECKING:
    from hydrogram.types import Message

logger = logging.getLogger(__name__)

SESSION_DIR = Path.home() / ".telegram-mcp"

TEXT_PREVIEW_LENGTH = 100


@dataclass
class ChatInfo:
    """Information about a chat."""

    id: int
    title: str
    username: str | None
    chat_type: str


@dataclass
class MessageInfo:
    """Information about a message."""

    id: int
    chat_id: int
    text: str | None
    sender_id: int | None
    sender_name: str | None
    date: int


class TelegramClient:
    """Telegram client using Hydrogram for MTProto communication."""

    def __init__(
        self,
        api_id: int | None = None,
        api_hash: str | None = None,
        session_name: str = "telegram_mcp",
    ) -> None:
        """Initialize Telegram client.

        Args:
            api_id: Telegram API ID from my.telegram.org
            api_hash: Telegram API hash from my.telegram.org
            session_name: Name for the session file

        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self._client: Client | None = None
        self._connected = False

    @property
    def client(self) -> Client:
        """Get the Hydrogram client instance.

        Returns:
            The Hydrogram client

        Raises:
            RuntimeError: If client is not initialized

        """
        if self._client is None:
            msg = "Client not initialized. Call connect() first."
            raise RuntimeError(msg)
        return self._client

    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._connected and self._client is not None

    async def connect(self) -> bool:
        """Connect to Telegram and authenticate if needed.

        Returns:
            True if connection successful

        """
        if self.is_connected:
            return True

        if not self.api_id or not self.api_hash:
            msg = "API ID and API hash are required. Get them from https://my.telegram.org"
            raise ValueError(msg)

        SESSION_DIR.mkdir(parents=True, exist_ok=True)
        session_path = SESSION_DIR / self.session_name

        self._client = Client(
            name=str(session_path),
            api_id=self.api_id,
            api_hash=self.api_hash,
            workdir=str(SESSION_DIR),
        )

        await self._client.connect()
        self._connected = True

        if not await self._client.is_user_authorized():
            await self._authenticate()

        return True

    async def _authenticate(self) -> None:
        """Handle authentication flow with browser-based code input."""
        client = self.client

        phone = input("Enter your phone number (with country code, e.g., +5511999999999): ")  # noqa: ASYNC250

        try:
            sent_code = await client.send_code(phone)
        except Exception as e:
            msg = f"Failed to send code: {e}"
            raise RuntimeError(msg) from e

        logger.info("A verification code has been sent to your Telegram app.")
        logger.info("Check your Telegram app for the code.")

        code_url = f"https://my.telegram.org/auth?phone={phone}"
        webbrowser.open(code_url)

        code = input("\nEnter the verification code: ")  # noqa: ASYNC250

        try:
            await client.sign_in(phone, sent_code.phone_code_hash, code)
        except SessionPasswordNeeded:
            password = input("Two-factor authentication enabled. Enter your password: ")  # noqa: ASYNC250
            await client.check_password(password)
        except Exception as e:
            msg = f"Authentication failed: {e}"
            raise RuntimeError(msg) from e

        logger.info("Authentication successful!")

    async def disconnect(self) -> None:
        """Disconnect from Telegram."""
        if self._client:
            await self._client.disconnect()
            self._connected = False

    async def send_message(
        self,
        chat_id: int | str,
        text: str,
    ) -> MessageInfo:
        """Send a text message to a chat.

        Args:
            chat_id: Chat ID or username
            text: Message text

        Returns:
            Information about the sent message

        """
        message = await self.client.send_message(chat_id, text)
        return self._message_to_info(message)

    async def get_messages(
        self,
        chat_id: int | str,
        limit: int = 20,
    ) -> list[MessageInfo]:
        """Get messages from a chat.

        Args:
            chat_id: Chat ID or username
            limit: Maximum number of messages to retrieve

        Returns:
            List of message information

        """
        return [
            self._message_to_info(message)
            async for message in self.client.get_chat_history(chat_id, limit=limit)
        ]

    async def get_dialogs(self, limit: int = 50) -> list[ChatInfo]:
        """Get list of chats/dialogs.

        Args:
            limit: Maximum number of dialogs to retrieve

        Returns:
            List of chat information

        """
        dialogs: list[ChatInfo] = []

        async for dialog in self.client.get_dialogs(limit=limit):
            chat = dialog.chat
            if chat:
                dialogs.append(
                    ChatInfo(
                        id=chat.id,
                        title=chat.title or getattr(chat, "first_name", "Unknown"),
                        username=getattr(chat, "username", None),
                        chat_type=chat.type.value
                        if hasattr(chat.type, "value")
                        else str(chat.type),
                    )
                )

        return dialogs

    async def get_me(self) -> dict:
        """Get information about the authenticated user.

        Returns:
            User information dictionary

        """
        me = await self.client.get_me()
        return {
            "id": me.id,
            "first_name": me.first_name,
            "last_name": me.last_name,
            "username": me.username,
            "phone": me.phone_number,
        }

    async def search_messages(
        self,
        chat_id: int | str,
        query: str,
        limit: int = 20,
    ) -> list[MessageInfo]:
        """Search messages in a chat.

        Args:
            chat_id: Chat ID or username
            query: Search query
            limit: Maximum number of messages to retrieve

        Returns:
            List of matching messages

        """
        return [
            self._message_to_info(message)
            async for message in self.client.search_messages(chat_id, query=query, limit=limit)
        ]

    def _message_to_info(self, message: Message) -> MessageInfo:
        """Convert a Hydrogram Message to MessageInfo.

        Args:
            message: Hydrogram Message object

        Returns:
            MessageInfo dataclass

        """
        sender_name = None
        sender_id = None

        if message.from_user:
            sender_id = message.from_user.id
            sender_name = " ".join(
                filter(
                    None,
                    [message.from_user.first_name, message.from_user.last_name],
                )
            )

        return MessageInfo(
            id=message.id,
            chat_id=message.chat.id if message.chat else 0,
            text=message.text or message.caption,
            sender_id=sender_id,
            sender_name=sender_name,
            date=message.date,
        )


_client: TelegramClient | None = None


def get_client() -> TelegramClient:
    """Get or create the global Telegram client instance.

    Returns:
        The global Telegram client instance

    """
    global _client  # noqa: PLW0602
    if _client is None:
        msg = "Client not initialized. Call init_client() first."
        raise RuntimeError(msg)
    return _client


def init_client(
    api_id: int | None = None,
    api_hash: str | None = None,
    session_name: str = "telegram_mcp",
) -> TelegramClient:
    """Initialize the global Telegram client.

    Args:
        api_id: Telegram API ID
        api_hash: Telegram API hash
        session_name: Session name

    Returns:
        The initialized Telegram client

    """
    global _client  # noqa: PLW0603
    _client = TelegramClient(api_id=api_id, api_hash=api_hash, session_name=session_name)
    return _client
