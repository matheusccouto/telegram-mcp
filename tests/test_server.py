"""Tests for MCP server tools."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from telegram_mcp.client import ChatInfo, MessageInfo
from telegram_mcp.server import (
    _get_api_hash,
    _get_api_id,
    get_me,
    get_messages,
    list_chats,
    search_messages,
    send_message,
)


class TestServerHelpers:
    """Tests for server helper functions."""

    def test_get_api_id_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test getting API ID from environment."""
        monkeypatch.setenv("TELEGRAM_API_ID", "12345678")
        assert _get_api_id() == 12345678

    def test_get_api_id_raises_when_not_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that _get_api_id raises when not set."""
        monkeypatch.delenv("TELEGRAM_API_ID", raising=False)
        with pytest.raises(ValueError, match="TELEGRAM_API_ID environment variable not set"):
            _get_api_id()

    def test_get_api_hash_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test getting API hash from environment."""
        monkeypatch.setenv("TELEGRAM_API_HASH", "abcdef1234567890")
        assert _get_api_hash() == "abcdef1234567890"

    def test_get_api_hash_raises_when_not_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that _get_api_hash raises when not set."""
        monkeypatch.delenv("TELEGRAM_API_HASH", raising=False)
        with pytest.raises(ValueError, match="TELEGRAM_API_HASH environment variable not set"):
            _get_api_hash()


class TestServerTools:
    """Tests for MCP server tools."""

    @pytest.mark.asyncio
    async def test_send_message(
        self,
        monkeypatch: pytest.MonkeyPatch,
        mock_api_credentials: tuple[int, str],
    ) -> None:
        """Test send_message tool."""
        api_id, api_hash = mock_api_credentials
        monkeypatch.setenv("TELEGRAM_API_ID", str(api_id))
        monkeypatch.setenv("TELEGRAM_API_HASH", api_hash)

        mock_message = MessageInfo(
            id=1,
            chat_id=123456789,
            text="Test message",
            sender_id=987654321,
            sender_name="Test User",
            date=1234567890,
        )

        with patch("telegram_mcp.server.init_client") as mock_init:
            mock_client = AsyncMock()
            mock_client.is_connected = True
            mock_client.send_message = AsyncMock(return_value=mock_message)
            mock_init.return_value = mock_client

            result = await send_message(123456789, "Test message")

            assert "Message sent successfully" in result
            assert "123456789" in result

    @pytest.mark.asyncio
    async def test_get_messages(
        self,
        monkeypatch: pytest.MonkeyPatch,
        mock_api_credentials: tuple[int, str],
    ) -> None:
        """Test get_messages tool."""
        api_id, api_hash = mock_api_credentials
        monkeypatch.setenv("TELEGRAM_API_ID", str(api_id))
        monkeypatch.setenv("TELEGRAM_API_HASH", api_hash)

        mock_messages = [
            MessageInfo(
                id=1,
                chat_id=123456789,
                text="Hello",
                sender_id=987654321,
                sender_name="User 1",
                date=1234567890,
            ),
            MessageInfo(
                id=2,
                chat_id=123456789,
                text="World",
                sender_id=987654322,
                sender_name="User 2",
                date=1234567891,
            ),
        ]

        with patch("telegram_mcp.server.init_client") as mock_init:
            mock_client = AsyncMock()
            mock_client.is_connected = True
            mock_client.get_messages = AsyncMock(return_value=mock_messages)
            mock_init.return_value = mock_client

            result = await get_messages(123456789, limit=10)

            assert "Found 2 messages" in result
            assert "Hello" in result
            assert "World" in result

    @pytest.mark.asyncio
    async def test_get_messages_empty(
        self,
        monkeypatch: pytest.MonkeyPatch,
        mock_api_credentials: tuple[int, str],
    ) -> None:
        """Test get_messages tool with empty result."""
        api_id, api_hash = mock_api_credentials
        monkeypatch.setenv("TELEGRAM_API_ID", str(api_id))
        monkeypatch.setenv("TELEGRAM_API_HASH", api_hash)

        with patch("telegram_mcp.server.init_client") as mock_init:
            mock_client = AsyncMock()
            mock_client.is_connected = True
            mock_client.get_messages = AsyncMock(return_value=[])
            mock_init.return_value = mock_client

            result = await get_messages(123456789, limit=10)

            assert "No messages found" in result

    @pytest.mark.asyncio
    async def test_list_chats(
        self,
        monkeypatch: pytest.MonkeyPatch,
        mock_api_credentials: tuple[int, str],
    ) -> None:
        """Test list_chats tool."""
        api_id, api_hash = mock_api_credentials
        monkeypatch.setenv("TELEGRAM_API_ID", str(api_id))
        monkeypatch.setenv("TELEGRAM_API_HASH", api_hash)

        mock_chats = [
            ChatInfo(id=1, title="Chat 1", username="chat1", chat_type="group"),
            ChatInfo(id=2, title="Chat 2", username=None, chat_type="private"),
        ]

        with patch("telegram_mcp.server.init_client") as mock_init:
            mock_client = AsyncMock()
            mock_client.is_connected = True
            mock_client.get_dialogs = AsyncMock(return_value=mock_chats)
            mock_init.return_value = mock_client

            result = await list_chats(limit=10)

            assert "Found 2 chats" in result
            assert "Chat 1" in result
            assert "Chat 2" in result

    @pytest.mark.asyncio
    async def test_get_me(
        self,
        monkeypatch: pytest.MonkeyPatch,
        mock_api_credentials: tuple[int, str],
    ) -> None:
        """Test get_me tool."""
        api_id, api_hash = mock_api_credentials
        monkeypatch.setenv("TELEGRAM_API_ID", str(api_id))
        monkeypatch.setenv("TELEGRAM_API_HASH", api_hash)

        mock_user = {
            "id": 123456789,
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "phone": "+5511999999999",
        }

        with patch("telegram_mcp.server.init_client") as mock_init:
            mock_client = AsyncMock()
            mock_client.is_connected = True
            mock_client.get_me = AsyncMock(return_value=mock_user)
            mock_init.return_value = mock_client

            result = await get_me()

            assert "John Doe" in result
            assert "johndoe" in result
            assert "+5511999999999" in result

    @pytest.mark.asyncio
    async def test_search_messages(
        self,
        monkeypatch: pytest.MonkeyPatch,
        mock_api_credentials: tuple[int, str],
    ) -> None:
        """Test search_messages tool."""
        api_id, api_hash = mock_api_credentials
        monkeypatch.setenv("TELEGRAM_API_ID", str(api_id))
        monkeypatch.setenv("TELEGRAM_API_HASH", api_hash)

        mock_messages = [
            MessageInfo(
                id=1,
                chat_id=123456789,
                text="Found this keyword",
                sender_id=987654321,
                sender_name="User",
                date=1234567890,
            ),
        ]

        with patch("telegram_mcp.server.init_client") as mock_init:
            mock_client = AsyncMock()
            mock_client.is_connected = True
            mock_client.search_messages = AsyncMock(return_value=mock_messages)
            mock_init.return_value = mock_client

            result = await search_messages(123456789, "keyword")

            assert "Found 1 messages" in result
            assert "keyword" in result
