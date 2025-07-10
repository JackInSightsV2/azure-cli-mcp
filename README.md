# Azure CLI MCP Server

A Python-based [MCP Server](https://modelcontextprotocol.io) that wraps the [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/), providing AI assistants with secure access to Azure resources and services.

## Features

🚀 **Complete Azure CLI Integration** - Execute any Azure CLI command through AI assistants  
🔐 **Secure Authentication** - Device code flow authentication with no credential storage  
🐳 **Docker Support** - Containerized deployment for easy setup and isolation  
🧪 **Comprehensive Testing** - Full test suite with security and integration tests  
⚡ **Modern Python** - Built with FastAPI, pytest, and modern Python practices  
🌐 **Web Interface** - Optional web UI for monitoring and debugging  

## What can it do?

It has access to the full Azure CLI, so it can do anything the Azure CLI can do. Here are a few scenarios:

- **Resource Management**: List, create, update, and delete Azure resources
- **Security Auditing**: Check configurations and fix security issues
- **Monitoring**: Get insights into resource performance and health
- **Deployment**: Deploy applications to Azure Container Apps, App Service, etc.
- **Cost Management**: Analyze and optimize Azure spending

## Quick Start

### Prerequisites

- **Docker Desktop** (recommended) - [Download here](https://www.docker.com/products/docker-desktop/)
- **Python 3.11+** (for native installation)
- **Azure CLI** (optional) - [Installation guide](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
- **Azure account** with appropriate permissions

### Option 1: Docker (Recommended)

1. **Clone and navigate to the repository:**
   ```powershell
   git clone https://github.com/JackInSightsV2/azure-cli-mcp.git
   cd azure-cli-mcp/azure-cli-mcp-python
   ```

2. **Run the deployment script:**
   ```powershell
   .\scripts\deploy.ps1 docker
   ```

3. **Start the server:**
   ```powershell
   docker-compose up
   ```

The server will automatically prompt for Azure authentication via browser using device code flow.

### Option 2: Python (Native)

1. **Clone and navigate to the repository:**
   ```bash
   git clone https://github.com/JackInSightsV2/azure-cli-mcp.git
   cd azure-cli-mcp/azure-cli-mcp-python
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server:**
   ```bash
   python -m azure_cli_mcp.main
   ```

## Configuration

### Environment Variables

Create a `.env` file based on `env.example`:

```bash
# Authentication (optional - uses device code flow if not provided)
AZURE_CREDENTIALS={"clientId":"...","clientSecret":"...","subscriptionId":"...","tenantId":"..."}

# Logging
LOG_LEVEL=INFO

# Server Configuration
MCP_SERVER_NAME=azure-cli-mcp
MCP_SERVER_VERSION=1.0.0
```

### MCP Client Configuration

#### Claude Desktop

Add to your `claude_desktop_config.json`:

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

#### VS Code with GitHub Copilot

Add to your MCP settings:

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

#### Docker Configuration

For Docker-based setup:

```json
{
  "mcpServers": {
    "azure-cli": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "azure-cli-mcp:latest"
      ]
    }
  }
}
```

## Project Structure

```
azure-cli-mcp-python/
├── azure_cli_mcp/              # Main package
│   ├── __init__.py
│   ├── main.py                 # MCP server entry point
│   ├── config.py               # Configuration management
│   ├── services/               # Core services
│   │   ├── __init__.py
│   │   ├── azure_cli_service.py    # Azure CLI execution
│   │   └── azure_login_handler.py  # Authentication handling
│   └── web/                    # Optional web interface
│       ├── __init__.py
│       ├── app.py              # FastAPI web app
│       └── static/             # Web assets
├── tests/                      # Comprehensive test suite
│   ├── test_azure_cli_service.py
│   ├── test_azure_login_handler.py
│   ├── test_config.py
│   ├── test_integration.py
│   └── test_security.py
├── scripts/                    # Deployment scripts
│   └── deploy.ps1             # PowerShell deployment script
├── requirements.txt            # Python dependencies
├── pyproject.toml             # Project configuration
├── Dockerfile                 # Container configuration
├── docker-compose.yml         # Multi-container setup
├── env.example               # Environment template
└── INSTALLATION.md           # Detailed installation guide
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=azure_cli_mcp --cov-report=html

# Run specific test categories
pytest tests/test_security.py
pytest tests/test_integration.py
```

### Code Quality

```bash
# Format code
black azure_cli_mcp/

# Lint code
flake8 azure_cli_mcp/

# Type checking
mypy azure_cli_mcp/
```

### Docker Development

```bash
# Build image
docker build -t azure-cli-mcp .

# Run tests in container
docker run --rm azure-cli-mcp pytest

# Interactive development
docker-compose up --build
```

## Security Considerations

⚠️ **Important Security Notes:**

- **Local Use Only**: This MCP server is designed for local development use with `stdio` transport
- **Credential Security**: Uses device code flow - no credentials stored locally
- **Command Validation**: All Azure CLI commands are validated before execution
- **Audit Logging**: All commands and results are logged for security auditing
- **Least Privilege**: Run with minimal required Azure permissions

### Authentication Methods

1. **Device Code Flow** (Recommended): Browser-based authentication with no stored credentials
2. **Service Principal**: For automated scenarios, stored in environment variables
3. **Azure CLI Login**: Uses existing `az login` session

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **Module not found** | Verify you're in correct directory: `cd azure-cli-mcp-python` |
| **Azure CLI not found** | Install Azure CLI: [Installation guide](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) |
| **Authentication failed** | Run `az login` or follow device code prompts |
| **Permission denied** | Check Azure RBAC permissions for your account |
| **Port conflicts** | Stop other services on port 8000 or configure different port |

### Debug Mode

Enable detailed logging:

```bash
LOG_LEVEL=DEBUG python -m azure_cli_mcp.main
```

### Health Checks

Test the server:

```bash
# Test Azure CLI connectivity
az account show

# Test MCP server
python -c "from azure_cli_mcp.main import main; main()"
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run the test suite: `pytest`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Disclaimer**: THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND. Use this MCP server at your own risk and always validate commands before execution in production environments.

## Support

- 📖 **Documentation**: Check [INSTALLATION.md](azure-cli-mcp-python/INSTALLATION.md) for detailed setup instructions
- 🐛 **Issues**: Report bugs on [GitHub Issues](https://github.com/JackInSightsV2/azure-cli-mcp/issues)
- 💬 **Discussions**: Join the conversation in [GitHub Discussions](https://github.com/JackInSightsV2/azure-cli-mcp/discussions)
