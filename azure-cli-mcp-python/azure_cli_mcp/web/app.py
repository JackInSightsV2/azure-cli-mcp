"""FastAPI web application for Azure CLI MCP Server."""

import logging
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from azure_cli_mcp.config import Settings
from azure_cli_mcp.services.azure_cli_service import AzureCliService

logger = logging.getLogger(__name__)

# Get the path to static files
STATIC_DIR = Path(__file__).parent / "static"
TEMPLATES_DIR = Path(__file__).parent / "templates"

# Create directories if they don't exist
STATIC_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)


def create_app(settings: Settings, azure_cli_service: AzureCliService) -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title="Azure CLI MCP Server",
        description="A Python-based Azure CLI MCP server with web interface",
        version="1.0.0",
    )
    
    # Mount static files
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    
    # Templates (if we need them later)
    templates = Jinja2Templates(directory=TEMPLATES_DIR)
    
    @app.get("/", response_class=HTMLResponse)
    async def root():
        """Serve the main page."""
        try:
            # Try to serve the static index.html file
            index_file = STATIC_DIR / "index.html"
            if index_file.exists():
                return HTMLResponse(content=index_file.read_text(), status_code=200)
            else:
                # Fallback HTML if static file doesn't exist
                return HTMLResponse(content="""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Azure CLI MCP Server</title>
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
                </head>
                <body>
                    <div class="container my-5">
                        <h1>Azure CLI MCP Server - Python Version</h1>
                        <p>The web interface is running, but static files are not yet configured.</p>
                        <p>Check the <a href="/health">health endpoint</a> to verify the service is running.</p>
                    </div>
                </body>
                </html>
                """, status_code=200)
        except Exception as e:
            logger.error(f"Error serving root page: {e}")
            return HTMLResponse(content=f"<h1>Error</h1><p>{str(e)}</p>", status_code=500)
    
    @app.get("/health")
    async def health_check() -> Dict[str, Any]:
        """Health check endpoint."""
        try:
            # Test Azure CLI service
            result = await azure_cli_service.execute_azure_cli("az --version")
            azure_cli_available = True
            azure_cli_version = result.split('\n')[1] if '\n' in result else result[:50]
        except Exception as e:
            azure_cli_available = False
            azure_cli_version = f"Error: {str(e)}"
        
        return {
            "status": "healthy",
            "service": "Azure CLI MCP Server",
            "version": "1.0.0",
            "azure_cli_available": azure_cli_available,
            "azure_cli_version": azure_cli_version,
            "log_level": settings.log_level,
            "log_file": settings.log_file
        }
    
    @app.get("/api/info")
    async def get_info() -> Dict[str, Any]:
        """Get server information."""
        return {
            "name": "Azure CLI MCP Server",
            "version": "1.0.0",
            "description": "Python-based Azure CLI MCP server",
            "mcp_tools": ["execute_azure_cli_command"],
            "endpoints": [
                {"path": "/", "method": "GET", "description": "Main page"},
                {"path": "/health", "method": "GET", "description": "Health check"},
                {"path": "/api/info", "method": "GET", "description": "Server information"}
            ]
        }
    
    return app


# For development/testing
if __name__ == "__main__":
    import uvicorn
    
    settings = Settings()
    azure_cli_service = AzureCliService(settings)
    app = create_app(settings, azure_cli_service)
    
    uvicorn.run(app, host="0.0.0.0", port=8000) 