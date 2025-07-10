"""Azure CLI MCP Server - Main entry point."""

import asyncio
import logging
import sys
from typing import Any, Dict, List, Optional, Union

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    TextContent,
    Tool,
)

from azure_cli_mcp.config import Settings
from azure_cli_mcp.services.azure_cli_service import AzureCliService

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global service instance
azure_cli_service: Optional[AzureCliService] = None


def create_azure_cli_tool() -> Tool:
    """Create the Azure CLI command execution tool definition."""
    return Tool(
        name="execute_azure_cli_command",
        description=(
            "Execute Azure CLI commands. This tool allows you to run any Azure CLI command "
            "and get the output. Commands must start with 'az'. For authentication, you can "
            "use 'az login' for device code flow or configure service principal credentials "
            "in environment variables."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": (
                        "The Azure CLI command to execute. Must start with 'az'. "
                        "Examples: 'az account list', 'az login', 'az group list'"
                    ),
                }
            },
            "required": ["command"],
        },
    )


async def handle_azure_cli_tool(request: CallToolRequest) -> CallToolResult:
    """Handle Azure CLI command execution tool calls."""
    if not azure_cli_service:
        return CallToolResult(
            content=[
                TextContent(
                    type="text", text="Error: Azure CLI service not initialized"
                )
            ],
            isError=True,
        )

    try:
        # Extract command from arguments
        if not request.params or not request.params.arguments:
            return CallToolResult(
                content=[
                    TextContent(type="text", text="Error: Missing command argument")
                ],
                isError=True,
            )

        arguments = request.params.arguments
        if not isinstance(arguments, dict) or "command" not in arguments:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text", text="Error: Missing 'command' in arguments"
                    )
                ],
                isError=True,
            )

        command = arguments["command"]
        if not isinstance(command, str):
            return CallToolResult(
                content=[
                    TextContent(type="text", text="Error: Command must be a string")
                ],
                isError=True,
            )

        logger.info(f"Executing Azure CLI command via MCP: {command}")

        # Execute the Azure CLI command
        result = await azure_cli_service.execute_azure_cli(command)

        return CallToolResult(content=[TextContent(type="text", text=result)])

    except Exception as e:
        logger.error(f"Error executing Azure CLI command: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")], isError=True
        )


async def main() -> None:
    """Main MCP server entry point."""
    global azure_cli_service

    try:
        # Initialize settings and service
        settings = Settings()
        azure_cli_service = AzureCliService(settings)

        # Create MCP server
        server: Server = Server("azure-cli-mcp")

        # Register tools
        azure_cli_tool = create_azure_cli_tool()

        @server.list_tools()  # type: ignore
        async def handle_list_tools() -> List[Tool]:
            """List available tools."""
            return [azure_cli_tool]

        @server.call_tool()  # type: ignore
        async def handle_call_tool(
            name: str, arguments: Dict[str, Any]
        ) -> CallToolResult:
            """Handle tool execution requests."""
            if name == "execute_azure_cli_command":
                # Create a fake request object for compatibility
                class FakeRequest:
                    def __init__(self, name: str, arguments: Dict[str, Any]):
                        self.params = self
                        self.name = name
                        self.arguments = arguments

                fake_request = FakeRequest(name, arguments)
                return await handle_azure_cli_tool(fake_request)  # type: ignore
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Unknown tool: {name}")],
                    isError=True,
                )

        logger.info("Starting Azure CLI MCP Server...")
        logger.info(f"Available tools: {azure_cli_tool.name}")
        logger.info(f"Log level: {settings.log_level}")
        logger.info(f"Log file: {settings.log_file}")

        # Run the server with stdio transport
        async with stdio_server() as streams:
            await server.run(
                streams[0],  # read stream
                streams[1],  # write stream
                server.create_initialization_options(),
            )

    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Error in MCP server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
