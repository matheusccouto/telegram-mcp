"""Telegram client wrapper using Hydrogram for MTProto communication."""

from __future__ import annotations

import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from hydrogram import Client

if TYPE_CHECKING:
    from hydrogram.types import Message

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
        api_id: int,
        api_hash: str,
        session_name: str = "telegram_mcp",
    ) -> None:
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self._client: Client | None = None
        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected and self._client is not None

    async def connect(self) -> bool:
        if self.is_connected:
            return True

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
        phone = input("Enter your phone number (with country code, e.g., +5511999999999): ")  # noqa: ASYNC250

        sent_code = await self._client.send_code(phone)

        print("\nA verification code has been sent to your Telegram app.")  # noqa: T201
        print("Check your Telegram app for the code.")  # noqa: T201

        webbrowser.open(f"https://my.telegram.org/auth?phone={phone}")

        code = input("\nEnter the verification code: ")  # noqa: ASYNC250

        await self._client.sign_in(phone, sent_code.phone_code_hash, code)

    async def disconnect(self) -> None:
        if self._client:
            await self._client.disconnect()
            self._connected = False

    async def send_message(self, chat_id: int | str, text: str) -> MessageInfo:
        message = await self._client.send_message(chat_id, text)
        return self._message_to_info(message)

    async def get_messages(self, chat_id: int | str, limit: int = 20) -> list[MessageInfo]:
        return [
            self._message_to_info(msg)
            async for msg in self._client.get_chat_history(chat_id, limit=limit)
        ]

    async def get_dialogs(self, limit: int = 50) -> list[ChatInfo]:
        return [
            ChatInfo(
                id=d.chat.id,
                title=d.chat.title or getattr(d.chat, "first_name", "Unknown"),
                username=getattr(d.chat, "username", None),
                chat_type=getattr(d.chat.type, "value", str(d.chat.type)),
            )
            async for d in self._client.get_dialogs(limit=limit)
            if d.chat
        ]

    async def get_me(self) -> dict:
        me = await self._client.get_me()
        return {
            "id": me.id,
            "first_name": me.first_name,
            "last_name": me.last_name,
            "username": me.username,
            "phone": me.phone_number,
        }

    async def search_messages(
        self, chat_id: int | str, query: str, limit: int = 20
    ) -> list[MessageInfo]:
        return [
            self._message_to_info(msg)
            async for msg in self._client.search_messages(chat_id, query=query, limit=limit)
        ]

    def _message_to_info(self, message: Message) -> MessageInfo:
        sender_id = None
        sender_name = None

        if message.from_user:
            sender_id = message.from_user.id
            sender_name = " ".join(
                filter(None, [message.from_user.first_name, message.from_user.last_name])
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
    global _client  # noqa: PLW0602
    if _client is None:
        msg = "Client not initialized. Call init_client() first."
        raise RuntimeError(msg)
    return _client


def init_client(api_id: int, api_hash: str, session_name: str = "telegram_mcp") -> TelegramClient:
    global _client  # noqa: PLW0603
    _client = TelegramClient(api_id=api_id, api_hash=api_hash, session_name=session_name)
    return _client
