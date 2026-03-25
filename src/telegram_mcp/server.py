"""FastMCP server for Telegram user account."""

from __future__ import annotations

import os

from fastmcp import FastMCP

from telegram_mcp.client import TEXT_PREVIEW_LENGTH, TelegramClient

mcp = FastMCP(
    name="telegram-mcp",
    instructions="""
Interact with your Telegram account.

Tools: send_message, get_messages, list_chats, get_me, search_messages

First run requires authentication (phone + verification code).
""",
)

_client: TelegramClient | None = None


async def _get_client() -> TelegramClient:
    global _client  # noqa: PLW0603
    if _client is None:
        _client = TelegramClient(
            api_id=int(os.environ["TELEGRAM_API_ID"]),
            api_hash=os.environ["TELEGRAM_API_HASH"],
            session_string=os.environ.get("TELEGRAM_SESSION"),
        )
    if not _client.is_connected:
        await _client.connect()
    return _client


@mcp.tool
async def send_message(chat_id: int | str, text: str) -> str:
    """Send a text message to a Telegram chat."""
    client = await _get_client()
    msg = await client.send_message(chat_id, text)
    return f"Sent to chat {msg.chat_id}. Message ID: {msg.id}"


@mcp.tool
async def get_messages(chat_id: int | str, limit: int = 20) -> str:
    """Get recent messages from a Telegram chat."""
    client = await _get_client()
    messages = await client.get_messages(chat_id, limit=limit)

    if not messages:
        return "No messages found."

    lines = [f"Found {len(messages)} messages:\n"]
    for msg in messages:
        sender = msg.sender_name or f"User {msg.sender_id}" if msg.sender_id else "Unknown"
        text = (
            msg.text[:TEXT_PREVIEW_LENGTH] + "..."
            if msg.text and len(msg.text) > TEXT_PREVIEW_LENGTH
            else msg.text
        )
        lines.append(f"[{msg.id}] {sender}: {text}")
    return "\n".join(lines)


@mcp.tool
async def list_chats(limit: int = 50) -> str:
    """List your Telegram chats/dialogs."""
    client = await _get_client()
    chats = await client.get_dialogs(limit=limit)

    if not chats:
        return "No chats found."

    lines = [f"Found {len(chats)} chats:\n"]
    for chat in chats:
        username = f" (@{chat.username})" if chat.username else ""
        lines.append(f"[{chat.id}] {chat.title}{username} - {chat.chat_type}")
    return "\n".join(lines)


@mcp.tool
async def get_me() -> str:
    """Get information about your Telegram account."""
    client = await _get_client()
    me = await client.get_me()
    return f"""ID: {me["id"]}
Name: {me["first_name"]} {me["last_name"] or ""}
Username: @{me["username"] or "N/A"}
Phone: {me["phone"]}"""


@mcp.tool
async def search_messages(chat_id: int | str, query: str, limit: int = 20) -> str:
    """Search for messages in a Telegram chat."""
    client = await _get_client()
    messages = await client.search_messages(chat_id, query, limit=limit)

    if not messages:
        return f"No messages matching '{query}'."

    lines = [f"Found {len(messages)} matching '{query}':\n"]
    for msg in messages:
        sender = msg.sender_name or f"User {msg.sender_id}" if msg.sender_id else "Unknown"
        text = (
            msg.text[:TEXT_PREVIEW_LENGTH] + "..."
            if msg.text and len(msg.text) > TEXT_PREVIEW_LENGTH
            else msg.text
        )
        lines.append(f"[{msg.id}] {sender}: {text}")
    return "\n".join(lines)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
