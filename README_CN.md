# Mind Map MCP Server

**🔒 完全本地部署 - 无需外部服务和 API 密钥 - 完整的数据隐私与安全保障**

一个基于 MCP (Model Context Protocol) 的思维导图生成服务，让你无需任何外部设计工具即可从 Markdown 文本生成精美的思维导图图片。完全本地部署，无需外部服务，无需 API 密钥，所有数据都在本地处理，确保完整的数据隐私和安全。将你的想法、笔记和结构化内容转换为可视化思维导图，与你的 AI 智能体无缝集成。

## 功能特性

*   **思维导图生成** (🎨): 从 Markdown 文本创建精美、专业的思维导图，支持三种不同的布局模式。
*   **三种布局模式** (📊):
    *   **中心布局**: 放射状布局，适合核心概念和头脑风暴。
    *   **水平布局**: 从左到右的布局，适合时间线、流程和层级结构。
    *   **智能布局**: 根据内容复杂度自动选择最合适的布局。
*   **Markdown 支持** (📝): 将 Markdown 标题 (`#`) 和列表 (`-`, `1.`) 转换为结构化的思维导图层级。
*   **中文字符支持** (🈳): 内置字体检测和自动处理中文字符。
*   **图片输出** (🖼️): 生成高质量的 PNG 图片，以 Base64 编码，便于集成。
*   **三重传输支持** (🔌): stdio（本地使用）、SSE（已废弃）和 streamable HTTP（推荐用于远程连接）。
*   **远程与本地** (🌐): 可在本地与 Cursor/Claude Desktop 配合使用，也可作为远程服务运行。
*   **HTTP API** (🌍): 提供直接的 HTTP 接口，无需 MCP 协议即可生成思维导图。
*   **无需设计工具** (✨): 无需外部设计软件或手动绘图。
*   **AI 智能体集成** (🤖): 通过 MCP 协议与 AI 智能体无缝集成。
*   **完整数据隐私** (🔒): 完全本地部署，无需外部服务，无需 API 密钥，所有数据都在本地处理，确保最大程度的数据安全。


## 安装

1.  安装依赖：

```bash
pip install -r requirements.txt
```

## 使用方法 (Usage)

本服务支持三种传输方式：

### 1. Stdio 传输 (本地使用)

```bash
python server.py stdio
```

**配置示例**：

```json
{
  "mcpServers": {
    "mind-map": {
      "command": "python",
      "args": [
        "/绝对路径/path/to/mind-map-mcp-pro/server.py",
        "stdio"
      ]
    }
  }
}
```

### 2. SSE 传输 (Server-Sent Events - 已废弃)

```bash
python server.py sse
```

**SSE 连接配置**：

```json
{
  "mcpServers": {
    "mind-map": {
      "url": "http://localhost:8899/sse"
    }
  }
}
```

### 3. Streamable HTTP 传输 (推荐用于远程连接)

```bash
python server.py streamable-http
```

**Streamable HTTP 连接配置**：

```json
{
  "mcpServers": {
    "mind-map": {
      "url": "http://localhost:8899/mcp"
    }
  }
}
```

### 环境变量

**SSE 和 Streamable HTTP 传输**

当使用 SSE 或 Streamable HTTP 协议运行服务器时，你可以设置 `FASTMCP_PORT` 环境变量来控制服务器监听的端口（如果未设置，默认为 8899）。

**示例 (Windows PowerShell)**：

```powershell
$env:FASTMCP_PORT="8007"
python server.py streamable-http
```

**示例 (Linux/macOS)**：

```bash
FASTMCP_PORT=8007 python server.py streamable-http
```

**Stdio 传输**

使用 stdio 协议时，不需要设置环境变量。服务器通过标准输入/输出直接通信。

## 可用工具 (Tools)

*   `create_center_mindmap`: 生成中心放射状的脑图。
*   `create_horizontal_mindmap`: 生成水平方向的脑图。
*   `create_free_mindmap`: 智能选择布局生成脑图。

所有工具均接受 `markdown_content` 字符串作为输入。

## HTTP 图片生成 API

你也可以通过 HTTP POST 直接生成图片：

**接口地址**: `POST /generate`

**请求体**:
```json
{
  "markdown_content": "# 根节点\n- 子节点 1\n- 子节点 2",
  "layout": "free"  // 可选值: center, horizontal, free
}
```
