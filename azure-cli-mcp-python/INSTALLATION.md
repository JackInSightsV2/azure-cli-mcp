# Azure CLI MCP Server - Installation Guide

This guide provides detailed installation instructions for the Azure CLI MCP Server Python version.

## Prerequisites

Before installing the Azure CLI MCP Server, ensure you have the following prerequisites:

### Required Software

1. **Python 3.11 or higher**
   - Check your Python version: `python --version`
   - Download from: https://www.python.org/downloads/

2. **Azure CLI**
   - Install following the official guide: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli
   - Verify installation: `az --version`

3. **Git** (for cloning the repository)
   - Download from: https://git-scm.com/downloads

### Azure Account Requirements

- Active Azure subscription
- Appropriate permissions to create and manage resources
- Either:
  - Personal Azure account with sufficient permissions, OR
  - Service Principal with contributor access to target resources

## Installation Methods

### Method 1: Python Installation (Recommended)

This method runs the server as a Python application using your local environment.

#### Step 1: Clone the Repository

```bash
git clone https://github.com/jdubois/azure-cli-mcp.git
cd azure-cli-mcp/azure-cli-mcp-python
```

#### Step 2: Install Dependencies

**Option A: Using pip (recommended)**
```bash
pip install -r requirements.txt
```

**Option B: Using pip with virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Step 3: Configure Authentication

Choose one of the following authentication methods:

**Option A: Azure CLI Login (Easiest)**
```bash
az login
```

**Option B: Service Principal (More Secure)**

1. Create a Service Principal:
```bash
az ad sp create-for-rbac --name "azure-cli-mcp" --role contributor --scopes /subscriptions/<your-subscription-id> --json-auth
```

2. Set the environment variable:
```bash
# Linux/macOS
export AZURE_CREDENTIALS='{"clientId":"...","clientSecret":"...","subscriptionId":"...","tenantId":"...","resourceManagerEndpointUrl":"https://management.azure.com/"}'

# Windows PowerShell
$env:AZURE_CREDENTIALS='{"clientId":"...","clientSecret":"...","subscriptionId":"...","tenantId":"...","resourceManagerEndpointUrl":"https://management.azure.com/"}'

# Windows Command Prompt
set AZURE_CREDENTIALS={"clientId":"...","clientSecret":"...","subscriptionId":"...","tenantId":"...","resourceManagerEndpointUrl":"https://management.azure.com/"}
```

#### Step 4: Test the Installation

Run the server to verify it works:
```bash
python -m azure_cli_mcp.main
```

You should see output indicating the MCP server has started successfully.

### Method 2: Docker Installation

This method uses Docker to run the server in a containerized environment.

#### Step 1: Build the Docker Image

```bash
git clone https://github.com/jdubois/azure-cli-mcp.git
cd azure-cli-mcp/azure-cli-mcp-python
docker build -t azure-cli-mcp .
```

#### Step 2: Configure Authentication

Create a Service Principal (required for Docker):
```bash
az ad sp create-for-rbac --name "azure-cli-mcp" --role contributor --scopes /subscriptions/<your-subscription-id> --json-auth
```

#### Step 3: Run the Container

```bash
docker run -e AZURE_CREDENTIALS='{"clientId":"...","clientSecret":"...","subscriptionId":"...","tenantId":"...","resourceManagerEndpointUrl":"https://management.azure.com/"}' -i azure-cli-mcp
```

## Configuration

### Environment Variables

The server supports the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `AZURE_CREDENTIALS` | JSON string with Service Principal credentials | None |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | INFO |
| `MCP_SERVER_NAME` | Name of the MCP server | azure-cli-mcp |
| `MCP_SERVER_VERSION` | Version of the MCP server | 1.0.0 |

### Configuration File

You can also use a `.env` file for configuration:

1. Copy the example file:
```bash
cp env.example .env
```

2. Edit the `.env` file with your configuration:
```env
AZURE_CREDENTIALS={"clientId":"...","clientSecret":"...","subscriptionId":"...","tenantId":"...","resourceManagerEndpointUrl":"https://management.azure.com/"}
LOG_LEVEL=INFO
MCP_SERVER_NAME=azure-cli-mcp
MCP_SERVER_VERSION=1.0.0
```

## MCP Client Setup

### VS Code with GitHub Copilot

1. Install GitHub Copilot extension
2. Open Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
3. Run: `MCP: Add Server...`
4. Add the following configuration:

**For Python installation:**
```json
{
  "servers": {
    "azure-cli": {
      "command": "python",
      "args": ["-m", "azure_cli_mcp.main"],
      "cwd": "/path/to/azure-cli-mcp/azure-cli-mcp-python"
    }
  }
}
```

**For Docker installation:**
```json
{
  "servers": {
    "azure-cli": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "AZURE_CREDENTIALS", "azure-cli-mcp"],
      "env": {
        "AZURE_CREDENTIALS": "..."
      }
    }
  }
}
```

### Claude Desktop

1. Locate your `claude_desktop_config.json` file:
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. Add the server configuration:

**For Python installation:**
```json
{
  "mcpServers": {
    "azure-cli": {
      "command": "python",
      "args": ["-m", "azure_cli_mcp.main"],
      "cwd": "/path/to/azure-cli-mcp/azure-cli-mcp-python"
    }
  }
}
```

**For Docker installation:**
```json
{
  "mcpServers": {
    "azure-cli": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "AZURE_CREDENTIALS", "azure-cli-mcp"],
      "env": {
        "AZURE_CREDENTIALS": "..."
      }
    }
  }
}
```

3. Restart Claude Desktop

## Verification

### Test the Server

Run the test script to verify everything works:

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/test_azure_cli_service.py  # Azure CLI functionality
pytest tests/test_integration.py       # MCP integration
pytest tests/test_security.py         # Security features
```

### Test with MCP Client

1. Start your MCP client (VS Code or Claude Desktop)
2. Look for the "azure-cli-mcp" server in the available tools
3. Try a simple command like asking to check Azure CLI version
4. Verify the server responds with Azure CLI information

## Troubleshooting

### Common Issues

#### 1. Python Module Not Found

**Error**: `ImportError: No module named 'azure_cli_mcp'`

**Solutions**:
- Ensure you're in the correct directory: `cd azure-cli-mcp/azure-cli-mcp-python`
- Install dependencies: `pip install -r requirements.txt`
- Use the correct Python version: `python3 -m azure_cli_mcp.main`

#### 2. Azure CLI Not Found

**Error**: `Azure CLI not found` or `'az' is not recognized`

**Solutions**:
- Install Azure CLI: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli
- Verify installation: `az --version`
- Check PATH environment variable includes Azure CLI location

#### 3. Authentication Errors

**Error**: `Authentication failed` or `No valid credentials`

**Solutions**:
- For Azure CLI login: Run `az login` and verify with `az account show`
- For Service Principal: Verify `AZURE_CREDENTIALS` environment variable is set correctly
- Check Service Principal permissions: Ensure it has appropriate roles

#### 4. Permission Errors

**Error**: `Insufficient permissions` or `Access denied`

**Solutions**:
- Verify your Azure account has required permissions
- Check resource group and subscription access
- For Service Principal: Ensure it has contributor role or appropriate permissions

#### 5. MCP Client Connection Issues

**Error**: Server not appearing in MCP client

**Solutions**:
- Verify the server starts successfully when run manually
- Check the MCP client configuration file syntax
- Ensure the path to the Python executable and project directory are correct
- Restart the MCP client after configuration changes

### Debug Mode

Run the server with debug logging for detailed troubleshooting:

```bash
LOG_LEVEL=DEBUG python -m azure_cli_mcp.main
```

This will provide detailed logs about:
- Server startup process
- Azure CLI command execution
- Authentication attempts
- Error details

### Getting Help

If you encounter issues not covered in this guide:

1. Check the server logs for detailed error messages
2. Verify all prerequisites are installed and configured
3. Test Azure CLI functionality independently: `az --version`
4. Review the GitHub issues for similar problems
5. Create a new issue with detailed error information and system details

## Security Considerations

### Local Development

- Use Azure CLI login (`az login`) for local development
- Avoid hardcoding credentials in configuration files
- Use `.env` files for environment-specific configuration (ensure they're in `.gitignore`)

### Production/Shared Environments

- Always use Service Principal authentication
- Store credentials securely (environment variables, key vaults)
- Use least-privilege access principles
- Regularly rotate Service Principal secrets
- Monitor and audit Azure CLI command usage

### Network Security

- The MCP server only supports `stdio` transport (local communication)
- No network ports are exposed by default
- Server runs with the same permissions as the user account
- All Azure CLI commands are executed with user/Service Principal permissions

## Next Steps

After successful installation:

1. **Test basic functionality**: Try simple Azure CLI commands through your MCP client
2. **Explore capabilities**: Ask your AI assistant to help with Azure resource management
3. **Set up monitoring**: Configure logging and monitoring for production use
4. **Customize configuration**: Adjust settings based on your specific needs
5. **Review security**: Ensure authentication and permissions are appropriate for your environment

## Support

For additional support and resources:

- **Documentation**: See the main README.md for usage examples
- **Issues**: Report bugs and request features on GitHub
- **Community**: Join discussions about MCP and Azure CLI automation
- **Updates**: Watch the repository for new releases and improvements 