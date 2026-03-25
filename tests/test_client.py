"""Tests for TelegramClient."""

from __future__ import annotations

import pytest

from telegram_mcp import client as client_module
from telegram_mcp.client import (
    ChatInfo,
    MessageInfo,
    TelegramClient,
    init_client,
)


class TestTelegramClient:
    """Tests for TelegramClient class."""

    def test_init(self, mock_api_credentials: tuple[int, str]) -> None:
        """Test client initialization."""
        api_id, api_hash = mock_api_credentials
        client = TelegramClient(api_id=api_id, api_hash=api_hash)

        assert client.api_id == api_id
        assert client.api_hash == api_hash
        assert client.session_name == "telegram_mcp"
        assert client._client is None  # noqa: SLF001
        assert not client.is_connected

    def test_init_custom_session(self, mock_api_credentials: tuple[int, str]) -> None:
        """Test client initialization with custom session name."""
        api_id, api_hash = mock_api_credentials
        client = TelegramClient(api_id=api_id, api_hash=api_hash, session_name="custom_session")

        assert client.session_name == "custom_session"

    def test_client_property_raises_when_not_initialized(
        self,
        mock_api_credentials: tuple[int, str],
    ) -> None:
        """Test that accessing client property raises when not initialized."""
        api_id, api_hash = mock_api_credentials
        client = TelegramClient(api_id=api_id, api_hash=api_hash)

        with pytest.raises(RuntimeError, match="Client not initialized"):
            _ = client.client

    def test_is_connected_false_initially(self, mock_api_credentials: tuple[int, str]) -> None:
        """Test that is_connected is False initially."""
        api_id, api_hash = mock_api_credentials
        client = TelegramClient(api_id=api_id, api_hash=api_hash)

        assert not client.is_connected


class TestChatInfo:
    """Tests for ChatInfo dataclass."""

    def test_chat_info_creation(self) -> None:
        """Test ChatInfo creation."""
        chat = ChatInfo(
            id=123456789,
            title="Test Chat",
            username="testchat",
            chat_type="group",
        )

        assert chat.id == 123456789
        assert chat.title == "Test Chat"
        assert chat.username == "testchat"
        assert chat.chat_type == "group"

    def test_chat_info_without_username(self) -> None:
        """Test ChatInfo without username."""
        chat = ChatInfo(
            id=123456789,
            title="Private Chat",
            username=None,
            chat_type="private",
        )

        assert chat.username is None


class TestMessageInfo:
    """Tests for MessageInfo dataclass."""

    def test_message_info_creation(self) -> None:
        """Test MessageInfo creation."""
        message = MessageInfo(
            id=1,
            chat_id=123456789,
            text="Hello, world!",
            sender_id=987654321,
            sender_name="John Doe",
            date=1234567890,
        )

        assert message.id == 1
        assert message.chat_id == 123456789
        assert message.text == "Hello, world!"
        assert message.sender_id == 987654321
        assert message.sender_name == "John Doe"
        assert message.date == 1234567890

    def test_message_info_without_text(self) -> None:
        """Test MessageInfo without text."""
        message = MessageInfo(
            id=1,
            chat_id=123456789,
            text=None,
            sender_id=987654321,
            sender_name="John Doe",
            date=1234567890,
        )

        assert message.text is None


class TestGlobalClient:
    """Tests for global client functions."""

    def test_init_client(self, mock_api_credentials: tuple[int, str]) -> None:
        """Test init_client function."""
        api_id, api_hash = mock_api_credentials
        client = init_client(api_id=api_id, api_hash=api_hash)

        assert client.api_id == api_id
        assert client.api_hash == api_hash

    def test_get_client_raises_when_not_initialized(self) -> None:
        """Test get_client raises when not initialized."""
        client_module._client = None  # noqa: SLF001

        with pytest.raises(RuntimeError, match="Client not initialized"):
            client_module.get_client()
