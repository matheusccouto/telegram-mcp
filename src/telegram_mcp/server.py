"""FastMCP server for Telegram user account."""

from __future__ import annotations

import os

from fastmcp import FastMCP

from telegram_mcp.client import TEXT_PREVIEW_LENGTH, init_client

mcp = FastMCP(
    name="telegram-mcp",
    instructions="""
    This MCP server allows you to interact with your Telegram account.

    Available tools:
    - send_message: Send a text message to a chat
    - get_messages: Get recent messages from a chat
    - list_chats: List your chats/dialogs
    - get_me: Get information about your account
    - search_messages: Search messages in a chat

    The first time you use this server, you will need to authenticate
    by entering your phone number and verification code.
    """,
)


@mcp.tool
async def send_message(chat_id: int | str, text: str) -> str:
    """Send a text message to a Telegram chat.

    Args:
        chat_id: The chat ID (integer) or username (string, e.g., @username)
        text: The message text to send

    Returns:
        Confirmation with message details

    """
    client = init_client(
        api_id=_get_api_id(),
        api_hash=_get_api_hash(),
    )

    if not client.is_connected:
        await client.connect()

    message = await client.send_message(chat_id, text)
    return f"Message sent successfully to chat {message.chat_id}. Message ID: {message.id}"


@mcp.tool
async def get_messages(chat_id: int | str, limit: int = 20) -> str:
    """Get recent messages from a Telegram chat.

    Args:
        chat_id: The chat ID (integer) or username (string)
        limit: Maximum number of messages to retrieve (default: 20)

    Returns:
        List of messages with details

    """
    client = init_client(
        api_id=_get_api_id(),
        api_hash=_get_api_hash(),
    )

    if not client.is_connected:
        await client.connect()

    messages = await client.get_messages(chat_id, limit=limit)

    if not messages:
        return "No messages found in this chat."

    result = f"Found {len(messages)} messages:\n\n"
    for msg in messages:
        sender = msg.sender_name or f"User {msg.sender_id}" if msg.sender_id else "Unknown"
        text_preview = (
            (msg.text[:TEXT_PREVIEW_LENGTH] + "...")
            if msg.text and len(msg.text) > TEXT_PREVIEW_LENGTH
            else msg.text
        )
        result += f"[{msg.id}] {sender}: {text_preview}\n"

    return result


@mcp.tool
async def list_chats(limit: int = 50) -> str:
    """List your Telegram chats/dialogs.

    Args:
        limit: Maximum number of chats to retrieve (default: 50)

    Returns:
        List of chats with their IDs and names

    """
    client = init_client(
        api_id=_get_api_id(),
        api_hash=_get_api_hash(),
    )

    if not client.is_connected:
        await client.connect()

    chats = await client.get_dialogs(limit=limit)

    if not chats:
        return "No chats found."

    result = f"Found {len(chats)} chats:\n\n"
    for chat in chats:
        username = f" (@{chat.username})" if chat.username else ""
        result += f"[{chat.id}] {chat.title}{username} - {chat.chat_type}\n"

    return result


@mcp.tool
async def get_me() -> str:
    """Get information about your Telegram account.

    Returns:
        Your account information

    """
    client = init_client(
        api_id=_get_api_id(),
        api_hash=_get_api_hash(),
    )

    if not client.is_connected:
        await client.connect()

    me = await client.get_me()

    return f"""Your Telegram Account:
ID: {me["id"]}
Name: {me["first_name"]} {me["last_name"] or ""}
Username: @{me["username"] or "N/A"}
Phone: {me["phone"]}
"""


@mcp.tool
async def search_messages(chat_id: int | str, query: str, limit: int = 20) -> str:
    """Search for messages in a Telegram chat.

    Args:
        chat_id: The chat ID (integer) or username (string)
        query: The search query
        limit: Maximum number of messages to retrieve (default: 20)

    Returns:
        List of matching messages

    """
    client = init_client(
        api_id=_get_api_id(),
        api_hash=_get_api_hash(),
    )

    if not client.is_connected:
        await client.connect()

    messages = await client.search_messages(chat_id, query, limit=limit)

    if not messages:
        return f"No messages found matching '{query}' in this chat."

    result = f"Found {len(messages)} messages matching '{query}':\n\n"
    for msg in messages:
        sender = msg.sender_name or f"User {msg.sender_id}" if msg.sender_id else "Unknown"
        text_preview = (
            (msg.text[:TEXT_PREVIEW_LENGTH] + "...")
            if msg.text and len(msg.text) > TEXT_PREVIEW_LENGTH
            else msg.text
        )
        result += f"[{msg.id}] {sender}: {text_preview}\n"

    return result


def _get_api_id() -> int:
    """Get Telegram API ID from environment.

    Returns:
        API ID

    Raises:
        ValueError: If API ID not set

    """
    api_id = os.getenv("TELEGRAM_API_ID")
    if not api_id:
        msg = "TELEGRAM_API_ID environment variable not set. Get it from https://my.telegram.org"
        raise ValueError(msg)
    return int(api_id)


def _get_api_hash() -> str:
    """Get Telegram API hash from environment.

    Returns:
        API hash

    Raises:
        ValueError: If API hash not set

    """
    api_hash = os.getenv("TELEGRAM_API_HASH")
    if not api_hash:
        msg = "TELEGRAM_API_HASH environment variable not set. Get it from https://my.telegram.org"
        raise ValueError(msg)
    return api_hash


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
