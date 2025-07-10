# Azure CLI MCP Server

This is an [MCP Server](https://modelcontextprotocol.io) that wraps the [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/), adds a nice prompt to improve how it works, and exposes it.

[![smithery badge](https://smithery.ai/badge/@jdubois/azure-cli-mcp)](https://smithery.ai/server/@jdubois/azure-cli-mcp)

## Demos

### Short 2-minute demo with Claude Desktop

[![Short Demo](https://img.youtube.com/vi/y_OexCcfhW0/0.jpg)](https://www.youtube.com/watch?v=y_OexCcfhW0)

### Complete 18-minute demo with VS Code

[![Complete Demo](https://img.youtube.com/vi/NZxTr32A9lY/0.jpg)](https://www.youtube.com/watch?v=NZxTr32A9lY)

## What can it do?

It has access to the full Azure CLI, so it can do anything the Azure CLI can do. Here are a few scenarios:

- Listing your resources and checking their configuration. For example, you can get the rate limits of a model deployed
  to Azure OpenAI.
- Fixing some configuration or security issues. For example, you can ask it to secure a Blob Storage account.
- Creating resources. For example, you can ask it to create an Azure Container Apps instance, an Azure Container Registry, and connect them using managed identity.

## Is it safe to use?

As the MCP server is driven by an LLM, we would recommend to be careful and validate the commands it generates. Then, if
you're using a good LLM like Claude 3.7 or GPT-4o, which has
excellent training data on Azure, our experience has been very good.

Please read our [License](LICENSE) which states that "THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND",
so you use this MCP server at your own risk.

## Is it secured, and should I run this on a remote server?

Short answer: **NO**.

This MCP server runs `az` commands for you, and could be hacked by an attacker to run any other command. The current
implementation, as with most MCP servers at the moment, only works with the `stdio` transport:
it's supposed to run locally on your machine, using your Azure CLI credentials, as you would do by yourself.

In the future, it's totally possible to have this MCP server support the `http` transport, and an Azure token
authentication, so that it could be used remotely by different persons. It's a second step, that will be done once the
MCP specification and SDK are more stable.

## How do I install it?

_This server runs as a Docker container (recommended) or as a Python application._

For both options, only the `stdio` transport is available. The `http` transport will be available later.

### Prerequisites

- **Docker Desktop** - Install from [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
- **Azure CLI** (optional) - Install by following the instructions [here](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
- **Azure account** - You'll need an Azure subscription and appropriate permissions

### Install and configure the server with Docker (Recommended)

#### Quick Start with PowerShell

1. **Clone the repository:**
   ```powershell
   git clone https://github.com/jdubois/azure-cli-mcp.git
   cd azure-cli-mcp/azure-cli-mcp-python
   ```

2. **Run the deployment script:**
   ```powershell
   .\scripts\deploy.ps1 docker
   ```

3. **Start the server:**
   ```powershell
   .\start_docker.ps1
   ```
   
   The server will automatically prompt you to authenticate via browser using Azure device code flow - no credentials setup needed!

### Install and configure the server with Python (Advanced)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jdubois/azure-cli-mcp.git
   cd azure-cli-mcp/azure-cli-mcp-python
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Azure authentication:**
   
   **Option A: Use your existing Azure CLI login (easiest)**
   ```bash
   az login
   ```
   
   **Option B: Use a Service Principal (more secure)**
   ```bash
   az ad sp create-for-rbac --name "azure-cli-mcp" --role contributor --scopes /subscriptions/<your-subscription-id>/resourceGroups/<your-resource-group> --json-auth
   ```
   
   Then set the `AZURE_CREDENTIALS` environment variable:
   ```bash
   export AZURE_CREDENTIALS='{"clientId":"....","clientSecret":"....","subscriptionId":"....","tenantId":"....","resourceManagerEndpointUrl":"https://management.azure.com/"}'
   ```

4. **Run the server:**
   ```bash
   python -m azure_cli_mcp.main
   ```

#### Using VS Code

To use the server from VS Code:

- Install GitHub Copilot
- Install this MCP Server using the command palette: `MCP: Add Server...`
- Add the following configuration to your MCP settings:

```json
{
  "servers": {
    "azure-cli": {
      "command": "python",
      "args": [
        "-m",
        "azure_cli_mcp.main"
      ],
      "cwd": "/path/to/azure-cli-mcp/azure-cli-mcp-python"
    }
  }
}
```

- Configure GitHub Copilot to run in `Agent` mode, by clicking on the arrow at the bottom of the chat window
- On top of the chat window, you should see the `azure-cli-mcp` server configured as a tool

#### Using Claude Desktop

To use the server from Claude Desktop, add the server to your `claude_desktop_config.json` file.

```json
{
  "mcpServers": {
    "azure-cli": {
      "command": "python",
      "args": [
        "-m",
        "azure_cli_mcp.main"
      ],
      "cwd": "/path/to/azure-cli-mcp/azure-cli-mcp-python"
    }
  }
}
```

The server will automatically prompt for authentication via browser when needed.

### Install and configure the server with Docker (Alternative)

You can run the server using Docker:

```bash
docker run --rm -i ghcr.io/jdubois/azure-cli-mcp:latest
```

The server will prompt you to authenticate via browser using device code flow when needed.

#### Using VS Code with Docker

To use the server from VS Code with Docker:

- Install GitHub Copilot
- Install this MCP Server using the command palette: `MCP: Add Server...`
- Configure GitHub Copilot to run in `Agent` mode, by clicking on the arrow at the bottom of the chat window
- On top of the chat window, you should see the `azure-cli-mcp` server configured as a tool

Configuration example:

```json
{
  "servers": {
    "azure-cli": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "ghcr.io/jdubois/azure-cli-mcp:latest"
      ]
    }
  }
}
```

The server will automatically prompt for authentication via browser when needed.

#### Using Claude Desktop with Docker

To use the server from Claude Desktop with Docker, add the server to your `claude_desktop_config.json` file:

```json
{
  "mcpServers": {
    "azure-cli": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "ghcr.io/jdubois/azure-cli-mcp:latest"
      ]
    }
  }
}
```

The server will automatically prompt for authentication via browser when needed.

### Installation with Smithery.ai

You can install the MCP server through Smithery.ai:

[![smithery badge](https://smithery.ai/badge/@jdubois/azure-cli-mcp)](https://smithery.ai/server/@jdubois/azure-cli-mcp)

This is similar to our Docker container installation above, but runs on Smithery.ai's servers. The server will use device code flow for authentication (no credentials required). Please note that:

- Smithery.ai is a third-party service, and you need to trust them to build this MCP server for you (it uses the same
  Dockerfile as our Docker image, but isn't built by us).
- This is still an early preview service, so we can't guarantee how it will evolve.

## Configuration

The server supports various configuration options through environment variables:

- `AZURE_CREDENTIALS`: (Optional) JSON string with Azure Service Principal credentials. If not provided, the server will use device code flow for authentication.
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `MCP_SERVER_NAME`: Name of the MCP server (default: "azure-cli-mcp")
- `MCP_SERVER_VERSION`: Version of the MCP server

See `env.example` for a complete configuration template.

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/test_azure_cli_service.py

# Run with coverage
pytest --cov=azure_cli_mcp
```

### Project Structure

```
azure-cli-mcp-python/
├── azure_cli_mcp/
│   ├── __init__.py
│   ├── main.py           # MCP server entry point
│   ├── config.py         # Configuration management
│   └── services/
│       ├── __init__.py
│       ├── azure_cli_service.py    # Azure CLI command execution
│       └── azure_login_handler.py  # Azure login handling
├── tests/                # Comprehensive test suite
├── requirements.txt      # Python dependencies
├── pyproject.toml       # Project configuration
└── env.example          # Environment configuration template
```

## Troubleshooting

### Common Issues

1. **ImportError: No module named 'azure_cli_mcp'**
   - Make sure you're running from the correct directory
   - Ensure all dependencies are installed: `pip install -r requirements.txt`

2. **Azure CLI not found**
   - Install Azure CLI: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli
   - Verify installation: `az --version`

3. **Authentication errors**
   - For device code flow: Follow the browser authentication prompts
   - For service principal: Verify `AZURE_CREDENTIALS` if using credentials
   - Check your Azure login: `az account show`

4. **Permission errors**
   - Ensure your Azure account has appropriate permissions
   - Check resource group and subscription access

### Debug Mode

Run the server with debug logging:

```bash
LOG_LEVEL=DEBUG python -m azure_cli_mcp.main
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
