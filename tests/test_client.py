"""Tests for TelegramClient - integration tests require real credentials."""

from __future__ import annotations

import os

import pytest

from telegram_mcp.client import ChatInfo, MessageInfo, TelegramClient

API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
HAS_CREDENTIALS = API_ID is not None and API_HASH is not None


@pytest.mark.skipif(not HAS_CREDENTIALS, reason="TELEGRAM_API_ID and TELEGRAM_API_HASH not set")
class TestTelegramClientIntegration:
    """Integration tests with real Telegram API."""

    @pytest.fixture
    async def client(self) -> TelegramClient:
        client = TelegramClient(
            api_id=int(API_ID),  # type: ignore[arg-type]
            api_hash=API_HASH,  # type: ignore[arg-type]
            session_name="test_session",
        )
        yield client
        if client.is_connected:
            await client.disconnect()

    @pytest.mark.asyncio
    async def test_connect(self, client: TelegramClient) -> None:
        result = await client.connect()
        assert result is True
        assert client.is_connected

    @pytest.mark.asyncio
    async def test_get_me(self, client: TelegramClient) -> None:
        await client.connect()
        me = await client.get_me()
        assert "id" in me
        assert "first_name" in me
        assert isinstance(me["id"], int)

    @pytest.mark.asyncio
    async def test_get_dialogs(self, client: TelegramClient) -> None:
        await client.connect()
        dialogs = await client.get_dialogs(limit=5)
        assert isinstance(dialogs, list)
        if dialogs:
            assert isinstance(dialogs[0], ChatInfo)

    @pytest.mark.asyncio
    async def test_send_message_to_saved_messages(self, client: TelegramClient) -> None:
        await client.connect()
        msg = await client.send_message("me", "Test message from telegram-mcp")
        assert isinstance(msg, MessageInfo)
        assert msg.text == "Test message from telegram-mcp"

    @pytest.mark.asyncio
    async def test_get_messages_from_saved_messages(self, client: TelegramClient) -> None:
        await client.connect()
        await client.send_message("me", "Test for get_messages")
        messages = await client.get_messages("me", limit=1)
        assert isinstance(messages, list)
        assert len(messages) >= 1


class TestDataclasses:
    """Tests for dataclasses without API calls."""

    def test_chat_info(self) -> None:
        chat = ChatInfo(id=123, title="Test", username="test", chat_type="private")
        assert chat.id == 123
        assert chat.title == "Test"
        assert chat.username == "test"
        assert chat.chat_type == "private"

    def test_message_info(self) -> None:
        msg = MessageInfo(
            id=1, chat_id=123, text="Hello", sender_id=456, sender_name="User", date=0
        )
        assert msg.id == 1
        assert msg.text == "Hello"

    def test_message_info_none_text(self) -> None:
        msg = MessageInfo(id=1, chat_id=123, text=None, sender_id=None, sender_name=None, date=0)
        assert msg.text is None
