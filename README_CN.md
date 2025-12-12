# Mind Map MCP Server

这是一个基于 MCP (Model Context Protocol) 的脑图生成服务。它支持将 Markdown 文本转换为精美的思维导图图片。

本项目复用了经过验证的成熟脑图生成算法，支持三种布局模式，并提供 Stdio 和 SSE/HTTP 两种通信协议，方便接入 Cursor、Claude Desktop 等 MCP 客户端。

## 功能特性

*   **三种布局模式**：
    *   **Center Layout (中心布局)**：适合核心概念的发散，呈放射状。
    *   **Horizontal Layout (水平布局)**：适合展示时间线、流程或层级结构，从左向右排列。
    *   **Free/Smart Layout (智能布局)**：根据内容复杂度自动选择最合适的布局。
*   **多协议支持**：同时支持标准 Stdio 传输和 SSE (Server-Sent Events) over HTTP。
*   **中文支持**：内置/自动检测中文字体，确保中文内容显示正常。

## 安装

1.  克隆或下载本项目。
2.  安装依赖：

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. Stdio 模式 (默认)

这是 MCP 客户端（如 Cursor, Claude Desktop）最常用的集成方式。

**运行命令**：
```bash
python server.py
```

**在 Cursor/Claude Desktop 中配置**：

```json
{
  "mcpServers": {
    "mind-map": {
      "command": "python",
      "args": [
        "绝对路径/path/to/mind-map-mcp-pro/server.py"
      ]
    }
  }
}
```

### 2. HTTP/SSE 模式

如果你需要通过网络访问或使用支持 SSE 的客户端。

**运行命令**：
```bash
python server.py --transport http --port 8899
```

*   **SSE 端点**: `http://localhost:8899/sse`
*   **消息端点**: `http://localhost:8899/messages`

## 可用工具 (Tools)

### `create_center_mindmap`
生成中心放射状的脑图。
*   **参数**: `markdown_content` (Markdown 格式的文本，使用 `#` 或 `-` 表示层级)

### `create_horizontal_mindmap`
生成水平方向的脑图。
*   **参数**: `markdown_content`

### `create_free_mindmap`
智能选择布局生成脑图。
*   **参数**: `markdown_content`

## 示例输入

```markdown
# 核心主题
## 子主题 A
- 细节 1
- 细节 2
## 子主题 B
1. 步骤 1
2. 步骤 2
```

## 注意事项

*   本项目依赖 `matplotlib` 和 `PIL` 进行绘图。
*   生成的图片将以 Base64 编码的形式包含在 MCP 响应中。

