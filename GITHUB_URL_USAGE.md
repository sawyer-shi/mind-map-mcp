# 使用 GitHub URL + uv run 配置指南

## 概述

`server_standalone.py` 是一个单文件版本，支持通过 GitHub URL 直接运行，无需本地克隆仓库。

## 工作原理

1. **依赖管理**：使用 PEP 723 格式的依赖注释，`uv run` 会自动安装所需依赖
2. **模块下载**：首次运行时自动从 GitHub 下载 `src` 模块
3. **缓存机制**：下载的模块会缓存在本地，避免重复下载

## 配置方法

### MCP 配置文件

在 Cursor 的 MCP 配置文件中（`%APPDATA%\Cursor\User\globalStorage\mcp.json` 或 `~/.cursor/mcp.json`），使用以下配置：

```json
{
  "mcpServers": {
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

### 要求

- 已安装 `uv` 工具：https://github.com/astral-sh/uv
- 网络连接（首次运行需要下载模块）

## 首次运行

首次运行时，`server_standalone.py` 会：
1. 自动安装依赖（mcp、pillow、matplotlib、numpy）
2. 从 GitHub 下载 `src` 模块到缓存目录
3. 启动 MCP 服务器

**缓存位置**：
- Windows: `%LOCALAPPDATA%\mind-map-mcp\src`
- Linux/macOS: `~/.cache/mind-map-mcp/src`

## 优势与限制

### 优势
- ✅ 一键安装，无需克隆仓库
- ✅ 自动依赖管理
- ✅ 自动模块下载和缓存
- ✅ 适合快速试用

### 限制
- ⚠️ 首次运行需要网络连接
- ⚠️ 首次运行可能较慢（需要下载模块）
- ⚠️ 仅支持 stdio 模式（不支持 HTTP 传输）
- ⚠️ 需要安装 `uv` 工具

## 与本地安装的对比

| 特性 | GitHub URL + uv run | 本地安装 |
|------|---------------------|----------|
| 安装速度 | 首次较慢 | 快速 |
| 网络要求 | 首次需要 | 不需要 |
| 功能完整性 | stdio 模式 | 全部功能 |
| 性能 | 良好 | 最佳 |
| 维护性 | 自动更新 | 手动更新 |

## 故障排除

### 问题：下载失败

如果 GitHub 无法访问，可以：
1. 使用本地安装方式（推荐）
2. 手动下载 `src` 模块到缓存目录

### 问题：依赖安装失败

确保已正确安装 `uv`：
```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 问题：模块导入错误

清除缓存并重新下载：
```bash
# Windows
rmdir /s "%LOCALAPPDATA%\mind-map-mcp"

# Linux/macOS
rm -rf ~/.cache/mind-map-mcp
```

## 推荐使用场景

- 🎯 快速试用和测试
- 🎯 临时使用
- 🎯 不想本地克隆仓库

## 生产环境推荐

对于生产环境或长期使用，**强烈推荐使用本地安装方式**：
- 更好的性能
- 完整的功能支持
- 不依赖网络
- 更易于维护

参考 [MCP_CONFIG.md](MCP_CONFIG.md) 了解本地安装配置方法。

