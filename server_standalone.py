#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "mcp",
#     "pillow",
#     "matplotlib",
#     "numpy",
# ]
# ///
"""
Standalone Mind Map MCP Server
Supports running from GitHub URL with uv run

This version downloads the src modules from GitHub if they're not available locally.
"""

import asyncio
import base64
import json
import argparse
import sys
import os
import urllib.request
import tempfile
import importlib.util
import time

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool, 
    TextContent, 
    ImageContent, 
    EmbeddedResource, 
    CallToolResult,
    CallToolRequest
)

# Try to import src modules, if not available, download from GitHub
def ensure_src_modules():
    """Ensure src modules are available, download from GitHub if needed"""
    try:
        from src import mind_map_center
        from src import mind_map_free
        from src import mind_map_horizontal
        return mind_map_center, mind_map_free, mind_map_horizontal
    except ImportError:
        # If running from GitHub URL, download src modules with caching
        import hashlib
        
        # Use user's cache directory for persistent storage
        if sys.platform == 'win32':
            cache_base = os.path.join(os.environ.get('LOCALAPPDATA', tempfile.gettempdir()), 'mind-map-mcp')
        else:
            cache_base = os.path.join(os.path.expanduser('~'), '.cache', 'mind-map-mcp')
        
        cache_dir = os.path.join(cache_base, 'src')
        os.makedirs(cache_dir, exist_ok=True)
        
        base_url = "https://raw.githubusercontent.com/sawyer-shi/mind-map-mcp/master/src/"
        modules = ["mind_map_center.py", "mind_map_free.py", "mind_map_horizontal.py"]
        
        # Create __init__.py if it doesn't exist
        init_file = os.path.join(cache_dir, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w", encoding="utf-8") as f:
                f.write("")
        
        # Download modules (with caching)
        for module_name in modules:
            file_path = os.path.join(cache_dir, module_name)
            url = base_url + module_name
            
            # Only download if file doesn't exist or is old (older than 1 day)
            should_download = True
            if os.path.exists(file_path):
                file_age = time.time() - os.path.getmtime(file_path)
                if file_age < 86400:  # 1 day
                    should_download = False
            
            if should_download:
                try:
                    print(f"Downloading {module_name} from GitHub...", file=sys.stderr)
                    with urllib.request.urlopen(url, timeout=10) as response:
                        content = response.read().decode('utf-8')
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(content)
                except Exception as e:
                    if not os.path.exists(file_path):
                        print(f"Failed to download {module_name}: {e}", file=sys.stderr)
                        raise
                    else:
                        print(f"Download failed, using cached {module_name}", file=sys.stderr)
        
        # Add to sys.path and import
        sys.path.insert(0, cache_base)
        from src import mind_map_center
        from src import mind_map_free
        from src import mind_map_horizontal
        
        return mind_map_center, mind_map_free, mind_map_horizontal

# Initialize modules
try:
    mind_map_center, mind_map_free, mind_map_horizontal = ensure_src_modules()
except Exception as e:
    print(f"Error loading modules: {e}", file=sys.stderr)
    print("Please ensure you have cloned the repository locally.", file=sys.stderr)
    sys.exit(1)

# Initialize the MCP server
server = Server("mind-map-mcp")

# Helper function to execute the tool logic and convert to MCP response
def execute_tool(tool_class, markdown_content: str) -> List[Any]:
    tool_instance = tool_class()
    
    params = {
        "markdown_content": markdown_content,
        "filename": "mindmap"
    }
    
    generator = tool_instance._invoke(params)
    
    content = []
    
    try:
        for message in generator:
            if message["type"] == "blob":
                blob_data = message["blob"]
                mime_type = message["meta"].get("mime_type", "image/png")
                encoded_data = base64.b64encode(blob_data).decode("utf-8")
                
                content.append(ImageContent(
                    type="image",
                    data=encoded_data,
                    mimeType=mime_type
                ))
                
            elif message["type"] == "text":
                content.append(TextContent(
                    type="text",
                    text=message["text"]
                ))
                
            elif message["type"] == "json":
                json_str = json.dumps(message["data"], ensure_ascii=False, indent=2)
                content.append(TextContent(
                    type="text", 
                    text=f"Metadata:\n{json_str}"
                ))
                
    except Exception as e:
        content.append(TextContent(
            type="text",
            text=f"Error executing tool: {str(e)}"
        ))
        
    return content

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    return [
        Tool(
            name="create_center_mindmap",
            description="Create a radial/center layout mind map from Markdown text. Best for core-concept maps.",
            inputSchema={
                "type": "object",
                "properties": {
                    "markdown_content": {
                        "type": "string",
                        "description": "The markdown content to visualize as a mind map. Use headers (#) or list items (-/1.) to define hierarchy."
                    }
                },
                "required": ["markdown_content"]
            }
        ),
        Tool(
            name="create_horizontal_mindmap",
            description="Create a horizontal (left-to-right) layout mind map from Markdown text. Best for timelines or process flows.",
            inputSchema={
                "type": "object",
                "properties": {
                    "markdown_content": {
                        "type": "string",
                        "description": "The markdown content to visualize as a mind map."
                    }
                },
                "required": ["markdown_content"]
            }
        ),
        Tool(
            name="create_free_mindmap",
            description="Create a smart/free structure mind map. Automatically chooses between Center and Horizontal layouts based on complexity.",
            inputSchema={
                "type": "object",
                "properties": {
                    "markdown_content": {
                        "type": "string",
                        "description": "The markdown content to visualize as a mind map."
                    }
                },
                "required": ["markdown_content"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> List[TextContent | ImageContent | EmbeddedResource]:
    if not arguments:
        raise ValueError("Missing arguments")
    
    markdown_content = arguments.get("markdown_content")
    if not markdown_content:
        raise ValueError("Missing markdown_content")

    if name == "create_center_mindmap":
        tool_class = mind_map_center.get_tool()
        return execute_tool(tool_class, markdown_content)
        
    elif name == "create_horizontal_mindmap":
        tool_class = mind_map_horizontal.get_tool()
        return execute_tool(tool_class, markdown_content)
        
    elif name == "create_free_mindmap":
        tool_class = mind_map_free.get_tool()
        return execute_tool(tool_class, markdown_content)
        
    else:
        raise ValueError(f"Unknown tool: {name}")

def run_stdio():
    """Run the server using stdio transport"""
    async def _run():
        async with stdio_server() as (read, write):
            await server.run(read, write, server.create_initialization_options())
    
    asyncio.run(_run())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mind Map MCP Server (Standalone)")
    parser.add_argument("mode", nargs="?", default="stdio", choices=["stdio"], help="Mode to run the server in")
    
    args = parser.parse_args()
    
    if args.mode == "stdio":
        run_stdio()
    else:
        print("Only stdio mode is supported in standalone version", file=sys.stderr)
        sys.exit(1)

