"""Tests for MCP server - integration tests require real credentials."""

from __future__ import annotations

import os

import pytest

from telegram_mcp.server import get_me, get_messages, list_chats, search_messages, send_message

API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
HAS_CREDENTIALS = API_ID is not None and API_HASH is not None


@pytest.mark.skipif(not HAS_CREDENTIALS, reason="TELEGRAM_API_ID and TELEGRAM_API_HASH not set")
class TestServerIntegration:
    """Integration tests with real Telegram API."""

    @pytest.mark.asyncio
    async def test_send_message(self) -> None:
        result = await send_message("me", "Test from telegram-mcp server")
        assert "Sent to chat" in result

    @pytest.mark.asyncio
    async def test_get_messages(self) -> None:
        result = await get_messages("me", limit=5)
        assert "messages" in result.lower()

    @pytest.mark.asyncio
    async def test_list_chats(self) -> None:
        result = await list_chats(limit=5)
        assert "chats" in result.lower()

    @pytest.mark.asyncio
    async def test_get_me(self) -> None:
        result = await get_me()
        assert "ID:" in result
        assert "Phone:" in result

    @pytest.mark.asyncio
    async def test_search_messages(self) -> None:
        result = await search_messages("me", "test", limit=5)
        assert isinstance(result, str)
