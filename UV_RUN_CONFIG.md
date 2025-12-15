# uv run 配置示例

## 快速配置

将你的 MCP 配置文件中的 `mind-map-mcp` 部分替换为以下配置：

### 完整配置示例

```json
{
  "mcpServers": {
    "excel-mcp-server": {
      "command": "uvx excel-mcp-server stdio",
      "env": {}
    },
    "mind-map-mcp": {
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

### 仅 mind-map-mcp 部分

如果你只想修改 `mind-map-mcp` 部分，将：

```json
"mind-map-mcp": {
  "command": "python",
  "args": [
    "D:\\Work\\Cursor\\mind-map-mcp\\server.py",
    "stdio"
  ],
  "env": {
    "PYTHONIOENCODING": "utf-8"
  }
}
```

替换为：

```json
"mind-map-mcp": {
  "command": "uv",
  "args": [
    "run",
    "https://raw.githubusercontent.com/sawyer-shi/mind-map-mcp/master/server_standalone.py",
    "stdio"
  ]
}
```

## 配置步骤

1. **确保已安装 uv**
   ```bash
   # 检查是否已安装
   uv --version
   
   # 如果未安装，访问：https://github.com/astral-sh/uv
   ```

2. **修改配置文件**
   - Windows: `%APPDATA%\Cursor\User\globalStorage\mcp.json` 或 `C:\Users\你的用户名\.cursor\mcp.json`
   - 使用上面的配置替换 `mind-map-mcp` 部分

3. **重启 Cursor**

4. **首次运行**
   - 首次运行时会自动下载依赖和 src 模块
   - 可能需要几秒钟时间
   - 后续运行会使用缓存，速度更快

## 测试

配置完成后，在 Cursor 中尝试使用思维导图工具：
- `create_center_mindmap`
- `create_horizontal_mindmap`
- `create_free_mindmap`

## 故障排除

### 如果遇到 "uv: command not found"
- 需要先安装 uv：https://github.com/astral-sh/uv
- Windows: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

### 如果下载失败
- 检查网络连接
- 可以回退到本地安装方式（使用 `python` + 本地路径）

### 查看日志
- 在 Cursor 的 MCP 日志中查看详细错误信息

