# MCP 服务配置指南

## 问题诊断

如果你遇到以下错误：
- `ModuleNotFoundError: No module named 'mcp'`
- `ModuleNotFoundError: No module named 'uvicorn'`
- `No server info found`
- 服务无法启动

这通常是因为配置不正确导致的。

### 最常见的问题

**错误日志示例**：
```
Starting new stdio process with command: uv run https://raw.githubusercontent.com/sawyer-shi/mind-map-mcp/master/server.py stdio
ModuleNotFoundError: No module named 'mcp'
```

**原因**：使用了 GitHub URL 直接运行，导致：
1. 临时目录没有安装任何依赖（mcp、pillow、matplotlib 等）
2. 无法访问 `src` 目录下的模块
3. 无法正常工作

**解决方案**：必须使用本地文件路径，不能使用 GitHub URL！

## 正确的配置方法

### ⚠️ 重要提示

**不要使用 GitHub URL 直接运行服务器！** 必须使用本地文件路径。

### 配置步骤

1. **确保已安装依赖**

```bash
pip install -r requirements.txt
```

2. **使用本地路径配置**

在 Cursor 的 MCP 配置文件中（通常是 `%APPDATA%\Cursor\User\globalStorage\mcp.json` 或类似位置），使用以下配置：

#### Windows 配置示例

```json
{
  "mcpServers": {
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
  }
}
```

#### 配置说明

- `command`: **必须使用 `python` 或 `python3`**，不要使用 `uv` 或 `uv run`
- `args`: 
  - 第一个参数：**必须是本地文件的绝对路径**，例如 `D:\Work\Cursor\mind-map-mcp\server.py`
  - 第二个参数：`stdio`（用于本地连接）
- `env`: 可选，设置环境变量（Windows 上建议设置 UTF-8 编码）

**关键点**：
- ✅ 使用 `python` 命令 + 本地绝对路径
- ❌ 不要使用 `uv run` + GitHub URL

### 常见错误配置（不要使用）

❌ **错误配置 1：使用 GitHub URL + uv run**
```json
{
  "command": "uv",
  "args": [
    "run",
    "https://raw.githubusercontent.com/sawyer-shi/mind-map-mcp/master/server.py",
    "stdio"
  ]
}
```
**问题**：
- 临时目录没有安装任何依赖（mcp、pillow、matplotlib 等）
- 无法访问 `src` 目录下的模块
- 会导致 `ModuleNotFoundError: No module named 'mcp'` 错误

❌ **错误配置 2：使用相对路径**
```json
{
  "args": [
    "./server.py",
    "stdio"
  ]
}
```
**问题**：工作目录可能不正确

✅ **正确配置：使用 python + 本地绝对路径**
```json
{
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
**优势**：
- 使用本地已安装的 Python 环境和依赖
- 可以正常访问项目中的所有模块（包括 `src` 目录）
- 不会出现模块导入错误

## 验证配置

配置完成后，重启 Cursor，然后检查 MCP 服务是否正常启动。如果仍有问题：

1. 检查 Python 路径是否正确
2. 确认所有依赖已安装：`pip install -r requirements.txt`
3. 手动测试服务器：`python server.py stdio`（应该能正常启动，等待输入）

## 其他传输方式

如果需要使用 HTTP 传输（远程连接），请参考 README.md 中的说明。

