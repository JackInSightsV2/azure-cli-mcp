# Azure CLI MCP Server

An MCP (Model Context Protocol) server that provides AI assistants with secure access to Azure CLI commands. All you need is docker to run it locally. There are no cloud options at the moment. When you first run it allow it a little longer to download the docker image from github container registry. 

## Quick Setup

Add this to your MCP configuration file:

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "azure-cli": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "ghcr.io/jackinsightsv2/azure-cli-mcp:latest"
      ]
    }
  }
}
```

### Cursor

Add to your `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "azure-cli": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "ghcr.io/jackinsightsv2/azure-cli-mcp:latest"
      ]
    }
  }
}
```

### Other MCP Clients (Like Warp AI)

```json
{
  "azure-cli": {
    "command": "docker",
    "args": [
      "run",
      "-i",
      "--rm",
      "ghcr.io/jackinsightsv2/azure-cli-mcp:latest"
    ],
    "env": {},
    "working_directory": null,
    "start_on_launch": true
  }
}
```

## What It Does

- **Execute Azure CLI commands** - Run any `az` command through your AI assistant
- **Secure authentication** - Uses device code flow (opens browser for login)
- **Resource management** - Create, update, delete, and monitor Azure resources
- **Cost optimization** - Analyze spending and optimize resources
- **Security auditing** - Check configurations and fix security issues

## Authentication

The server will automatically prompt for Azure authentication when needed. It opens your browser for secure device code flow authentication - no credentials are stored.

## Checking Logs and Status

### View container logs:
```bash
# See running containers
docker ps

# View logs for the MCP server
docker logs <container_id>

# Follow logs in real-time
docker logs -f <container_id>
```

### Check server status:
```bash
# Test if server is responding
docker run --rm ghcr.io/jackinsightsv2/azure-cli-mcp:latest az account show
```

### Debug mode:
```json
{
  "mcpServers": {
    "azure-cli": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "LOG_LEVEL=DEBUG",
        "ghcr.io/jackinsightsv2/azure-cli-mcp:latest"
      ]
    }
  }
}
```

## Common Issues

| Problem | Solution |
|---------|----------|
| Docker not found | Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) |
| Authentication failed | Run `az login` manually or follow device code prompts |
| Permission denied | Check your Azure account has proper permissions |
| Container won't start | Check Docker is running: `docker ps` |

## Local Development

Only needed if you want to modify the server:

```bash
git clone https://github.com/JackInSightsV2/azure-cli-mcp.git
cd azure-cli-mcp/azure-cli-mcp-python
docker-compose up --build
```

## License

MIT License - see [LICENSE](LICENSE) file for details.
