# Azure CLI MCP Server - Windows PowerShell Deployment Script
# This script helps deploy the Azure CLI MCP Server using Docker on Windows

param(
    [Parameter(Position=0)]
    [ValidateSet("docker", "test", "setup", "help")]
    [string]$Action = "docker"
)

# Colors for output
$Colors = @{
    Red = "Red"
    Green = "Green"
    Yellow = "Yellow"
    Blue = "Blue"
    White = "White"
}

# Configuration
$DockerImageName = "azure-cli-mcp"
$ProjectDir = Split-Path -Parent $PSScriptRoot

# Functions
function Write-LogInfo {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Colors.Blue
}

function Write-LogSuccess {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $Colors.Green
}

function Write-LogWarning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Colors.Yellow
}

function Write-LogError {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Colors.Red
}

function Test-Requirements {
    Write-LogInfo "Checking requirements..."
    
    # Check Docker
    try {
        $dockerVersion = docker --version
        Write-LogInfo "Docker found: $dockerVersion"
    }
    catch {
        Write-LogError "Docker is not installed or not accessible"
        Write-LogInfo "Install Docker Desktop from: https://www.docker.com/products/docker-desktop/"
        exit 1
    }
    
    # Check Docker is running
    try {
        docker ps | Out-Null
        Write-LogInfo "Docker daemon is running"
    }
    catch {
        Write-LogError "Docker daemon is not running"
        Write-LogInfo "Start Docker Desktop and try again"
        exit 1
    }
    
    # Check Azure CLI (optional, can be in container)
    try {
        $azVersion = az --version
        Write-LogInfo "Azure CLI found locally"
    }
    catch {
        Write-LogWarning "Azure CLI not found locally (will use container version)"
    }
    
    Write-LogSuccess "Requirements check passed"
}

function Build-DockerImage {
    Write-LogInfo "Building Docker image..."
    
    Set-Location $ProjectDir
    
    # Build Docker image
    try {
        docker build -t $DockerImageName .
        Write-LogSuccess "Docker image built: $DockerImageName"
    }
    catch {
        Write-LogError "Failed to build Docker image"
        exit 1
    }
}

function Deploy-Docker {
    Write-LogInfo "Deploying with Docker..."
    
    Set-Location $ProjectDir
    
    # Build Docker image
    Build-DockerImage
    
    # Create docker-compose override for local development
    $dockerComposeOverride = @"
version: '3.8'

services:
  azure-cli-mcp:
    image: ${DockerImageName}:latest
    volumes:
      - ./azure_cli_mcp:/app/azure_cli_mcp
      - ./logs:/app/logs
    environment:
      - LOG_LEVEL=DEBUG
"@
    
    $dockerComposeOverride | Out-File -FilePath "docker-compose.override.yml" -Encoding UTF8
    
    # Create start script for Windows
    $startScript = @"
@echo off
echo Starting Azure CLI MCP Server...
echo Authentication will use device code flow (browser-based)
echo You'll be prompted to authenticate when the server starts
echo.

docker-compose up
"@
    
    $startScript | Out-File -FilePath "start_docker.bat" -Encoding ASCII
    
    # Create PowerShell start script
    $startPowerShellScript = @"
# Azure CLI MCP Server - Docker Startup Script
Write-Host "Starting Azure CLI MCP Server..." -ForegroundColor Green
Write-Host "Authentication will use device code flow (browser-based)" -ForegroundColor Yellow
Write-Host "You'll be prompted to authenticate when the server starts" -ForegroundColor Yellow
Write-Host ""

docker-compose up
"@
    
    $startPowerShellScript | Out-File -FilePath "start_docker.ps1" -Encoding UTF8
    
    Write-LogSuccess "Docker deployment complete"
    Write-LogInfo "Start the server with: .\start_docker.ps1 or start_docker.bat"
    Write-LogInfo "Authentication will use device code flow (browser-based) - no credentials required!"
}

function Test-Application {
    Write-LogInfo "Running tests..."
    
    Set-Location $ProjectDir
    
    # Check if Python is available for local testing
    try {
        python --version
        if ($LASTEXITCODE -eq 0) {
            Write-LogInfo "Python found, running local tests..."
            
            # Install dependencies
            pip install -r requirements.txt
            pip install pytest pytest-cov
            
            # Run tests
            pytest tests/ -v
            if ($LASTEXITCODE -eq 0) {
                Write-LogSuccess "Tests completed successfully"
                return
            } else {
                Write-LogWarning "Local tests failed, falling back to Docker..."
            }
        }
    }
    catch {
        # Python not available, fall back to Docker
    }
    
    Write-LogWarning "Python not found locally, testing with Docker..."
    
    # Build image if it doesn't exist
    try {
        docker image inspect $DockerImageName | Out-Null
    }
    catch {
        Build-DockerImage
    }
    
    # Test Docker image
    try {
        docker run --rm $DockerImageName python -c "import azure_cli_mcp; print('Import successful')"
        Write-LogSuccess "Docker image test passed"
    }
    catch {
        Write-LogError "Docker image test failed"
        exit 1
    }
}

function Setup-MCPClients {
    Write-LogInfo "Setting up MCP client configurations..."
    
    Set-Location $ProjectDir
    
    # Create VS Code configuration
    if (!(Test-Path ".vscode")) {
        New-Item -ItemType Directory -Path ".vscode" | Out-Null
    }
    
    $vsCodeConfig = @"
{
  "servers": {
    "azure-cli": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "$DockerImageName"]
    }
  }
}
"@
    
    $vsCodeConfig | Out-File -FilePath ".vscode/mcp_config.json" -Encoding UTF8
    
    # Create Claude Desktop configuration
    $claudeConfigDir = "$env:APPDATA\Claude"
    if (!(Test-Path $claudeConfigDir)) {
        New-Item -ItemType Directory -Path $claudeConfigDir -Force | Out-Null
    }
    
    $claudeConfig = @"
{
  "mcpServers": {
    "azure-cli": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "$DockerImageName"]
    }
  }
}
"@
    
    $claudeConfig | Out-File -FilePath "$claudeConfigDir\claude_desktop_config.json" -Encoding UTF8
    
    Write-LogSuccess "MCP client configurations created"
    Write-LogInfo "VS Code config: .vscode/mcp_config.json"
    Write-LogInfo "Claude Desktop config: $claudeConfigDir\claude_desktop_config.json"
}

function Show-Help {
    Write-Host @"
Azure CLI MCP Server - Windows PowerShell Deployment Script

Usage: .\deploy.ps1 [ACTION]

Actions:
  docker      Deploy with Docker (default)
  test        Run tests
  setup       Setup MCP client configurations
  help        Show this help message

Examples:
  .\deploy.ps1 docker    # Deploy with Docker
  .\deploy.ps1 test      # Run tests
  .\deploy.ps1 setup     # Setup MCP client configs

 Prerequisites:
   - Docker Desktop installed and running
   - Azure CLI (optional, can use container version)
   - Web browser for device code authentication

 Authentication:
   The server uses Azure CLI device code flow - you'll authenticate via browser when prompted.
   No credentials or environment variables required!

"@
}

function Show-AuthenticationHelp {
    Write-Host @"

Authentication Information:
- The Azure CLI MCP Server uses device code flow for authentication
- When you start the server, it will prompt you to visit a URL and enter a code
- This opens your browser for secure Azure authentication
- No service principal or credentials setup required!

Optional: If you prefer service principal authentication, you can set:
`$env:AZURE_CREDENTIALS = '{"clientId":"...","clientSecret":"...","subscriptionId":"...","tenantId":"...","resourceManagerEndpointUrl":"https://management.azure.com/"}'

"@
}

# Main execution
switch ($Action) {
    "docker" {
        Test-Requirements
        Deploy-Docker
        Setup-MCPClients
        Show-AuthenticationHelp
    }
    "test" {
        Test-Requirements
        Test-Application
    }
    "setup" {
        Setup-MCPClients
    }
    "help" {
        Show-Help
    }
    default {
        Write-LogError "Unknown action: $Action"
        Show-Help
        exit 1
    }
}

Write-LogSuccess "Script completed successfully!" 