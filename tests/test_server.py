"""Tests for MCP server - integration tests require real credentials."""

from __future__ import annotations

import os

import pytest

API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
SESSION_STRING = os.getenv("TELEGRAM_SESSION")
HAS_CREDENTIALS = API_ID is not None and API_HASH is not None and SESSION_STRING is not None


@pytest.mark.skipif(
    not HAS_CREDENTIALS,
    reason="TELEGRAM_API_ID, TELEGRAM_API_HASH and TELEGRAM_SESSION not set",
)
@pytest.mark.asyncio
async def test_send_message() -> None:
    from telegram_mcp.server import send_message

    result = await send_message("me", "Test from telegram-mcp")
    assert "Sent to chat" in result
