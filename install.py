#!/usr/bin/env python3
"""
安装脚本：帮助用户正确配置 Mind Map MCP Server

此脚本会：
1. 检查并安装依赖
2. 生成正确的 MCP 配置文件
3. 提供配置说明
"""

import os
import sys
import json
import subprocess
import platform
from pathlib import Path

def get_mcp_config_path():
    """获取 MCP 配置文件路径"""
    system = platform.system()
    if system == "Windows":
        # Windows: %APPDATA%\Cursor\User\globalStorage\mcp.json
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "Cursor" / "User" / "globalStorage" / "mcp.json"
    elif system == "Darwin":  # macOS
        # macOS: ~/Library/Application Support/Cursor/User/globalStorage/mcp.json
        home = os.path.expanduser("~")
        return Path(home) / "Library" / "Application Support" / "Cursor" / "User" / "globalStorage" / "mcp.json"
    else:  # Linux
        # Linux: ~/.config/Cursor/User/globalStorage/mcp.json
        home = os.path.expanduser("~")
        return Path(home) / ".config" / "Cursor" / "User" / "globalStorage" / "mcp.json"
    
    return None

def install_dependencies():
    """安装依赖"""
    print("正在检查依赖...")
    required_modules = ["mcp", "PIL", "matplotlib", "numpy"]
    missing_modules = []
    
    for module in required_modules:
        try:
            if module == "PIL":
                __import__("PIL")
            else:
                __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if not missing_modules:
        print("✓ 所有依赖已安装")
        return True
    
    print(f"发现缺失的依赖: {', '.join(missing_modules)}")
    print("正在安装依赖...")
    try:
        requirements_file = Path(__file__).parent / "requirements.txt"
        if not requirements_file.exists():
            print("✗ 未找到 requirements.txt 文件")
            return False
        
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
        print("✓ 依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 依赖安装失败，请手动运行: pip install -r requirements.txt")
        print(f"错误详情: {e}")
        return False

def generate_config():
    """生成 MCP 配置"""
    # 获取当前脚本所在目录的绝对路径
    current_dir = Path(__file__).parent.absolute()
    server_path = current_dir / "server.py"
    
    # 转换为适合操作系统的路径格式
    if platform.system() == "Windows":
        server_path_str = str(server_path).replace("\\", "\\\\")
    else:
        server_path_str = str(server_path)
    
    config = {
        "mcpServers": {
            "mind-map-mcp": {
                "command": sys.executable,
                "args": [
                    server_path_str,
                    "stdio"
                ]
            }
        }
    }
    
    # 如果是 Windows，添加编码环境变量
    if platform.system() == "Windows":
        config["mcpServers"]["mind-map-mcp"]["env"] = {
            "PYTHONIOENCODING": "utf-8"
        }
    
    return config

def main():
    print("=" * 60)
    print("Mind Map MCP Server 安装向导")
    print("=" * 60)
    print()
    
    # 1. 检查依赖
    if not install_dependencies():
        print("\n请先安装依赖后再运行此脚本。")
        return 1
    
    # 2. 生成配置
    print("\n正在生成 MCP 配置...")
    config = generate_config()
    
    # 3. 获取配置文件路径
    config_path = get_mcp_config_path()
    if not config_path:
        print("\n无法确定 MCP 配置文件路径，请手动配置。")
        print("\n配置内容：")
        print(json.dumps(config, indent=2, ensure_ascii=False))
        return 1
    
    # 4. 读取现有配置（如果存在）
    existing_config = {}
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                existing_config = json.load(f)
        except Exception as e:
            print(f"警告：无法读取现有配置文件: {e}")
            existing_config = {}
    
    # 5. 合并配置
    if "mcpServers" not in existing_config:
        existing_config["mcpServers"] = {}
    
    existing_config["mcpServers"]["mind-map-mcp"] = config["mcpServers"]["mind-map-mcp"]
    
    # 6. 备份现有配置
    if config_path.exists():
        backup_path = config_path.with_suffix(".json.backup")
        try:
            import shutil
            shutil.copy2(config_path, backup_path)
            print(f"✓ 已备份现有配置到: {backup_path}")
        except Exception as e:
            print(f"警告：无法备份配置文件: {e}")
    
    # 7. 写入配置
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(existing_config, f, indent=2, ensure_ascii=False)
        print(f"✓ 配置已写入: {config_path}")
    except Exception as e:
        print(f"✗ 无法写入配置文件: {e}")
        print("\n请手动将以下配置添加到 MCP 配置文件：")
        print(json.dumps(config, indent=2, ensure_ascii=False))
        return 1
    
    # 8. 完成
    print("\n" + "=" * 60)
    print("安装完成！")
    print("=" * 60)
    print("\n下一步：")
    print("1. 重启 Cursor")
    print("2. 检查 MCP 服务是否正常启动")
    print(f"\n配置文件位置: {config_path}")
    print("\n如果遇到问题，请参考 MCP_CONFIG.md")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

