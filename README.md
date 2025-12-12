# Mind Map MCP Server

An MCP (Model Context Protocol) server for generating mind map images from Markdown text.

## Features

*   **Three Layout Modes**:
    *   **Center Layout**: Radial layout, best for core concepts.
    *   **Horizontal Layout**: Left-to-right layout, best for timelines/processes.
    *   **Free/Smart Layout**: Automatically selects the best layout based on complexity.
*   **Dual Protocol Support**: Supports both Stdio and SSE/HTTP transports.
*   **Chinese Support**: Built-in font detection for Chinese characters.

## Installation

1.  Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### 1. Stdio Mode (Default)

Use this for integration with Cursor or Claude Desktop.

```bash
python server.py
```

**Configuration Example**:

```json
{
  "mcpServers": {
    "mind-map": {
      "command": "python",
      "args": [
        "/absolute/path/to/mind-map-mcp-pro/server.py"
      ]
    }
  }
}
```

### 2. HTTP/SSE Mode

```bash
python server.py --transport http --port 8899
```

*   **SSE Endpoint**: `http://localhost:8899/sse`
*   **Messages Endpoint**: `http://localhost:8899/messages`

## Tools

*   `create_center_mindmap`: Generate a radial mind map.
*   `create_horizontal_mindmap`: Generate a horizontal mind map.
*   `create_free_mindmap`: Smart layout selection.

All tools accept a `markdown_content` string as input.

