# telegram-mcp

MCP server for Telegram user account - send and receive messages via MTProto.

## Features

- **Send messages** to any chat, group, or channel
- **Get messages** from chats
- **List chats** and dialogs
- **Search messages** in chats
- **Get account info**

## Requirements

- Python 3.13+
- Telegram API credentials (from [my.telegram.org](https://my.telegram.org))

## Installation

```bash
uvx telegram-mcp
```

## Configuration

### 1. Get API credentials

1. Go to [my.telegram.org](https://my.telegram.org)
2. Login with your phone number
3. Go to "API development tools"
4. Create a new application
5. Copy `api_id` and `api_hash`

### 2. Generate session string

```python
import asyncio
from hydrogram import Client

async def main():
    app = Client(
        name="telegram_mcp",
        api_id=YOUR_API_ID,
        api_hash="YOUR_API_HASH",
    )
    await app.start()
    print(await app.export_session_string())
    await app.stop()

asyncio.run(main())
```

This will ask for your phone number and send a verification code to your Telegram app.

### 3. Set environment variables

```bash
export TELEGRAM_API_ID="your_api_id"
export TELEGRAM_API_HASH="your_api_hash"
export TELEGRAM_SESSION="your_session_string"
```

## Usage with Claude Code / OpenCode

Add to your MCP settings:

```json
{
  "mcpServers": {
    "telegram": {
      "command": "uvx",
      "args": ["telegram-mcp"],
      "env": {
        "TELEGRAM_API_ID": "your_api_id",
        "TELEGRAM_API_HASH": "your_api_hash",
        "TELEGRAM_SESSION": "your_session_string"
      }
    }
  }
}
```

## Available Tools

| Tool | Description |
|------|-------------|
| `send_message` | Send a text message to a chat |
| `get_messages` | Get recent messages from a chat |
| `list_chats` | List your Telegram chats/dialogs |
| `get_me` | Get information about your account |
| `search_messages` | Search for messages in a chat |

## Development

```bash
git clone https://github.com/matheusccouto/telegram-mcp.git
cd telegram-mcp
uv sync --all-extras
uv run ruff check .
uv run pytest
```

## Security

- Session string is stored in memory, not on disk
- Never share your `api_id`, `api_hash`, or `session_string`
- This uses your personal Telegram account, not a bot

## License

MIT License

## Acknowledgments

- [FastMCP](https://github.com/PrefectHQ/fastmcp) - MCP framework
- [Hydrogram](https://github.com/hydrogram/hydrogram) - Telegram MTProto library