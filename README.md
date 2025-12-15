# Mind Map MCP Server

**🔒 Fully Local Deployment - No External Services or API Keys Required - Complete Data Privacy & Security**


A Model Context Protocol (MCP) server that lets you generate beautiful mind map images from Markdown text without needing any external design tools. Deploy completely locally with no external services, no API keys, and no data leaving your machine - ensuring complete data privacy and security. Transform your ideas, notes, and structured content into visual mind maps with your AI agent.

## Features

*   **Mind Map Generation** (🎨): Create beautiful, professional mind maps from Markdown text with three distinct layout modes.
*   **Three Layout Modes** (📊): 
    *   **Center Layout**: Radial layout, perfect for core concepts and brainstorming.
    *   **Horizontal Layout**: Left-to-right layout, ideal for timelines, processes, and hierarchical structures.
    *   **Free/Smart Layout**: Automatically selects the best layout based on content complexity.
*   **Markdown Support** (📝): Convert Markdown headers (`#`) and lists (`-`, `1.`) into structured mind map hierarchies.
*   **Chinese Character Support** (🈳): Built-in font detection and automatic handling for Chinese characters.
*   **Image Output** (🖼️): Generate high-quality PNG images encoded in Base64 for easy integration.
*   **Triple Transport Support** (🔌): stdio (for local use), SSE (deprecated), and streamable HTTP (recommended for remote connections).
*   **Remote & Local** (🌐): Works both locally with Cursor/Claude Desktop and as a remote service.
*   **HTTP API** (🌍): Direct HTTP endpoint for generating mind maps without MCP protocol.
*   **Zero Dependencies on Design Tools** (✨): No need for external design software or manual drawing.
*   **AI Agent Integration** (🤖): Seamlessly integrate with AI agents through MCP protocol.
*   **Complete Data Privacy** (🔒): Fully local deployment with no external services, no API keys required, and all data stays on your machine for maximum security.


## Installation

### Quick Install (Recommended)

Run the installation script to automatically configure everything:

```bash
# Clone the repository first
git clone https://github.com/sawyer-shi/mind-map-mcp.git
cd mind-map-mcp

# Run the installation script
python install.py
```

The script will:
- Install all required dependencies
- Generate the correct MCP configuration
- Save the configuration to Cursor's MCP settings

### Manual Installation

1.  Install dependencies:

```bash
pip install -r requirements.txt
```

2.  Configure MCP server manually (see [MCP_CONFIG.md](MCP_CONFIG.md) for details)

## Usage

The server supports three transport methods:

### 1. Stdio Transport (for local use)

```bash
python server.py stdio
```

**Configuration Example**:

```json
{
  "mcpServers": {
    "mind-map": {
      "command": "python",
      "args": [
        "/absolute/path/to/mind-map-mcp/server.py",
        "stdio"
      ]
    }
  }
}
```

⚠️ **Important**: 
- **Recommended**: Use a **local absolute path** to `server.py` for best performance and reliability.
- **Alternative**: You can use `server_standalone.py` with GitHub URL + `uv run` (see below).

### Using GitHub URL with uv run (Alternative)

If you want to use GitHub URL for one-click installation, use `server_standalone.py`:

```json
{
  "mcpServers": {
    "mind-map": {
      "command": "uv",
      "args": [
        "run",
        "https://raw.githubusercontent.com/sawyer-shi/mind-map-mcp/master/server_standalone.py",
        "stdio"
      ]
    }
  }
}
```

**Note**: The standalone version will automatically download `src` modules from GitHub on first run, which may be slower than using a local installation. See [GITHUB_URL_USAGE.md](GITHUB_URL_USAGE.md) for detailed instructions.

### 2. SSE Transport (Server-Sent Events - Deprecated)

```bash
python server.py sse
```

**SSE transport connection**:

```json
{
  "mcpServers": {
    "mind-map": {
      "url": "http://localhost:8899/sse"
    }
  }
}
```

### 3. Streamable HTTP Transport (Recommended for remote connections)

```bash
python server.py streamable-http
```

**Streamable HTTP transport connection**:

```json
{
  "mcpServers": {
    "mind-map": {
      "url": "http://localhost:8899/mcp"
    }
  }
}
```

### Environment Variables

**SSE and Streamable HTTP Transports**

When running the server with the SSE or Streamable HTTP protocols, you can set the `FASTMCP_PORT` environment variable to control the port the server listens on (default is 8899 if not set).

**Example (Windows PowerShell)**:

```powershell
$env:FASTMCP_PORT="8007"
python server.py streamable-http
```

**Example (Linux/macOS)**:

```bash
FASTMCP_PORT=8007 python server.py streamable-http
```

**Stdio Transport**

When using the stdio protocol, no environment variables are required. The server communicates directly through standard input/output.

## Tools

*   `create_center_mindmap`: Generate a radial mind map.
*   `create_horizontal_mindmap`: Generate a horizontal mind map.
*   `create_free_mindmap`: Smart layout selection.

All tools accept a `markdown_content` string as input.

## HTTP Generation API

You can also generate images directly via HTTP POST:

**Endpoint**: `POST /generate`

**Body**:
```json
{
  "markdown_content": "# Root\n- Child 1\n- Child 2",
  "layout": "free"  // Options: center, horizontal, free
}
```
