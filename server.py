import asyncio
import base64
import json
import argparse
import sys
import os
# uvicorn is only needed for HTTP transports, import it lazily

# Set UTF-8 encoding for Windows to avoid Chinese character encoding issues
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
# HTTP transport dependencies are imported lazily when needed

# Import existing tool modules from src package
from src import mind_map_center
from src import mind_map_free
from src import mind_map_horizontal

# Initialize the MCP server
server = Server("mind-map-mcp")

# Helper function to execute the Dify tool logic and convert to MCP response
def execute_tool(tool_class, markdown_content: str) -> List[Any]:
    tool_instance = tool_class()
    
    # Input parameters expected by the tool
    params = {
        "markdown_content": markdown_content,
        "filename": "mindmap"
    }
    
    # The _invoke method is a generator
    generator = tool_instance._invoke(params)
    
    content = []
    
    try:
        for message in generator:
            if message["type"] == "blob":
                # Convert binary blob to base64 encoded image content
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
                # Append JSON metadata as text for visibility
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

# --- Transport Implementation ---
# HTTP transport code is defined inside run_http() to avoid importing dependencies in stdio mode

def _create_starlette_app():
    """Create Starlette app with HTTP routes (lazy import)"""
    from mcp.server.sse import SseServerTransport
    from starlette.applications import Starlette
    from starlette.responses import Response
    from starlette.routing import Route
    
    sse = SseServerTransport("/messages")

    async def handle_sse(request):
        """Handle SSE (Server-Sent Events) transport"""
        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
            await server.run(streams[0], streams[1], server.create_initialization_options())

    async def handle_messages(request):
        """Handle POST messages for SSE transport"""
        await sse.handle_post_message(request.scope, request.receive, request._send)

    async def handle_streamable_http(request):
        """Handle Streamable HTTP transport (recommended for remote connections)"""
        # Streamable HTTP uses the same SSE transport but with a different endpoint
        # This allows clients to connect via HTTP POST to /mcp endpoint
        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
            await server.run(streams[0], streams[1], server.create_initialization_options())

    async def generate_mindmap_http(request):
        """
        Streamable HTTP endpoint to directly generate mind map images.
        Expects JSON body: {"markdown_content": "...", "layout": "center|horizontal|free"}
        Returns: PNG image
        """
        try:
            body = await request.json()
            content = body.get("markdown_content")
            layout = body.get("layout", "free")
            
            if not content:
                return Response("Missing 'markdown_content'", status_code=400)

            if layout == "center":
                tool_cls = mind_map_center.get_tool()
            elif layout == "horizontal":
                tool_cls = mind_map_horizontal.get_tool()
            else:
                tool_cls = mind_map_free.get_tool()
                
            tool_instance = tool_cls()
            params = {"markdown_content": content, "filename": "http_generated"}
            
            generator = tool_instance._invoke(params)
            
            image_data = None
            for msg in generator:
                if msg["type"] == "blob":
                    image_data = msg["blob"]
                    break
            
            if image_data:
                return Response(image_data, media_type="image/png")
            else:
                return Response("Failed to generate image", status_code=500)
                
        except Exception as e:
            return Response(f"Error: {str(e)}", status_code=500)

    return Starlette(
        routes=[
            Route("/sse", endpoint=handle_sse),  # SSE transport endpoint
            Route("/mcp", endpoint=handle_streamable_http),  # Streamable HTTP transport endpoint
            Route("/messages", endpoint=handle_messages, methods=["POST"]),  # SSE messages endpoint
            Route("/generate", endpoint=generate_mindmap_http, methods=["POST"]),  # Direct image generation endpoint
        ]
    )

def run_stdio():
    """Run the server using stdio transport"""
    async def _run():
        async with stdio_server() as (read, write):
            await server.run(read, write, server.create_initialization_options())
    
    asyncio.run(_run())

def run_http(host: str = "0.0.0.0", port: int = 8899, mode: str = "sse"):
    """Run the server using HTTP transport (SSE or Streamable HTTP)"""
    # Lazy import uvicorn and create Starlette app only when HTTP transport is needed
    import uvicorn
    
    starlette_app = _create_starlette_app()
    
    if mode == "sse":
        print(f"Starting SSE server on http://{host}:{port}")
        print(f"SSE Endpoint: http://{host}:{port}/sse")
        print(f"Messages Endpoint: http://{host}:{port}/messages")
    else:  # streamable-http
        print(f"Starting Streamable HTTP server on http://{host}:{port}")
        print(f"Streamable HTTP Endpoint: http://{host}:{port}/mcp")
    uvicorn.run(starlette_app, host=host, port=port)

if __name__ == "__main__":
    import os
    
    parser = argparse.ArgumentParser(description="Mind Map MCP Server")
    parser.add_argument("mode", nargs="?", choices=["stdio", "sse", "streamable-http"], help="Mode to run the server in")
    parser.add_argument("--transport", choices=["stdio", "http"], help="Deprecated: use mode instead")
    parser.add_argument("--host", default="0.0.0.0", help="Host for HTTP server")
    parser.add_argument("--port", type=int, default=None, help="Port for HTTP server")
    
    args = parser.parse_args()
    
    # Determine mode
    mode = args.mode
    if not mode:
        if args.transport == "http":
            mode = "sse"
        else:
            mode = "stdio"
            
    # Determine port
    port = args.port
    if port is None:
        port = int(os.environ.get("FASTMCP_PORT", 8899))
    
    if mode == "stdio":
        run_stdio()
    elif mode == "sse":
        run_http(args.host, port, mode="sse")
    else:  # streamable-http
        run_http(args.host, port, mode="streamable-http")

