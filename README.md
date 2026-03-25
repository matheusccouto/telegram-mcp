# telegram-mcp

MCP server for Telegram user account - send and receive messages via MTProto.

This server allows you to interact with your personal Telegram account using the Model Context Protocol (MCP). It uses Hydrogram (a maintained fork of Pyrogram) for MTProto communication.

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

### Using uvx (Recommended)

```bash
uvx telegram-mcp
```

### Using pip

```bash
pip install telegram-mcp
```

## Configuration

1. Get your API credentials from [my.telegram.org](https://my.telegram.org):
   - Go to "API development tools"
   - Create a new application
   - Copy the `api_id` and `api_hash`

2. Set environment variables:

```bash
export TELEGRAM_API_ID="your_api_id"
export TELEGRAM_API_HASH="your_api_hash"
```

## Usage with Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "telegram": {
      "command": "uvx",
      "args": ["telegram-mcp"],
      "env": {
        "TELEGRAM_API_ID": "your_api_id",
        "TELEGRAM_API_HASH": "your_api_hash"
      }
    }
  }
}
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
        "TELEGRAM_API_HASH": "your_api_hash"
      }
    }
  }
}
```

## Authentication

On first run, the server will:

1. Ask for your phone number (with country code, e.g., `+5511999999999`)
2. Open a browser for verification code input
3. Send a verification code to your Telegram app
4. Ask for the verification code
5. If 2FA is enabled, ask for your password

After authentication, a session file is saved at `~/.telegram-mcp/` for future use.

## Available Tools

### send_message

Send a text message to a chat.

```
Arguments:
- chat_id: The chat ID (integer) or username (string, e.g., @username)
- text: The message text to send
```

### get_messages

Get recent messages from a chat.

```
Arguments:
- chat_id: The chat ID (integer) or username (string)
- limit: Maximum number of messages to retrieve (default: 20)
```

### list_chats

List your Telegram chats/dialogs.

```
Arguments:
- limit: Maximum number of chats to retrieve (default: 50)
```

### get_me

Get information about your Telegram account.

### search_messages

Search for messages in a chat.

```
Arguments:
- chat_id: The chat ID (integer) or username (string)
- query: The search query
- limit: Maximum number of messages to retrieve (default: 20)
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/matheusccouto/telegram-mcp.git
cd telegram-mcp

# Install dependencies with uv
uv sync --all-extras

# Run linter
uv run ruff check .

# Run tests
uv run pytest
```

### Project Structure

```
telegram-mcp/
├── src/telegram_mcp/
│   ├── __init__.py
│   ├── client.py      # Telegram client wrapper
│   └── server.py      # MCP server implementation
├── tests/
│   ├── conftest.py
│   ├── test_client.py
│   └── test_server.py
├── pyproject.toml
└── README.md
```

## Security Notes

- Your session file is stored locally at `~/.telegram-mcp/`
- API credentials are only needed for initial authentication
- Never share your `api_id`, `api_hash`, or session files
- This uses your personal Telegram account, not a bot

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- [FastMCP](https://github.com/PrefectHQ/fastmcp) - MCP framework
- [Hydrogram](https://github.com/hydrogram/hydrogram) - Telegram MTProto library