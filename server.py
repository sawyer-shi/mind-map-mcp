import asyncio
import base64
import json
import argparse
import sys
import uvicorn
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.sse import SseServerTransport
from mcp.types import (
    Tool, 
    TextContent, 
    ImageContent, 
    EmbeddedResource, 
    CallToolResult,
    CallToolRequest
)
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.routing import Route

# Import existing tool modules
import mind_map_center
import mind_map_free
import mind_map_horizontal

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

sse = SseServerTransport("/messages")

async def handle_sse(request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
        await server.run(streams[0], streams[1], server.create_initialization_options())

async def handle_messages(request):
    await sse.handle_post_message(request.scope, request.receive, request._send)

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

starlette_app = Starlette(
    routes=[
        Route("/sse", endpoint=handle_sse),
        Route("/messages", endpoint=handle_messages, methods=["POST"]),
        Route("/generate", endpoint=generate_mindmap_http, methods=["POST"]),
    ]
)

def run_stdio():
    """Run the server using stdio transport"""
    async def _run():
        async with stdio_server() as (read, write):
            await server.run(read, write, server.create_initialization_options())
    
    asyncio.run(_run())

def run_http(host: str = "0.0.0.0", port: int = 8899):
    """Run the server using HTTP/SSE transport"""
    print(f"Starting SSE/HTTP server on http://{host}:{port}")
    print(f"SSE Endpoint: http://{host}:{port}/sse")
    print(f"Messages Endpoint: http://{host}:{port}/messages")
    uvicorn.run(starlette_app, host=host, port=port)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mind Map MCP Server")
    parser.add_argument("--transport", choices=["stdio", "http"], default="stdio", help="Transport protocol to use")
    parser.add_argument("--host", default="0.0.0.0", help="Host for HTTP server")
    parser.add_argument("--port", type=int, default=8899, help="Port for HTTP server")
    
    args = parser.parse_args()
    
    if args.transport == "stdio":
        run_stdio()
    else:
        run_http(args.host, args.port)

