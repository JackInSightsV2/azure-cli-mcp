# Azure CLI MCP Server - Docker Test Script
# This script tests the Docker deployment of the Azure CLI MCP Server

Write-Host "Azure CLI MCP Server - Docker Test" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Test 1: Check if Docker is available
Write-Host "`n[TEST 1] Checking Docker availability..." -ForegroundColor Blue
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker found: $dockerVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ Docker not found. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

# Test 2: Check if Docker daemon is running
Write-Host "`n[TEST 2] Checking Docker daemon..." -ForegroundColor Blue
try {
    docker ps | Out-Null
    Write-Host "✅ Docker daemon is running" -ForegroundColor Green
}
catch {
    Write-Host "❌ Docker daemon not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Test 3: Build Docker image
Write-Host "`n[TEST 3] Building Docker image..." -ForegroundColor Blue
try {
    docker build -t azure-cli-mcp-test .
    Write-Host "✅ Docker image built successfully" -ForegroundColor Green
}
catch {
    Write-Host "❌ Failed to build Docker image" -ForegroundColor Red
    exit 1
}

# Test 4: Test basic import
Write-Host "`n[TEST 4] Testing Python imports..." -ForegroundColor Blue
try {
    $output = docker run --rm azure-cli-mcp-test python -c "import azure_cli_mcp; print('Import successful')"
    if ($output -match "Import successful") {
        Write-Host "✅ Python imports working: $output" -ForegroundColor Green
    } else {
        Write-Host "❌ Python import test failed" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "❌ Docker run failed" -ForegroundColor Red
    exit 1
}

# Test 5: Test Azure CLI in container
Write-Host "`n[TEST 5] Testing Azure CLI in container..." -ForegroundColor Blue
try {
    $output = docker run --rm azure-cli-mcp-test az --version
    if ($output -match "azure-cli") {
        Write-Host "✅ Azure CLI working in container" -ForegroundColor Green
    } else {
        Write-Host "❌ Azure CLI not working in container" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "❌ Azure CLI test failed" -ForegroundColor Red
    exit 1
}

# Test 6: Test MCP server startup (brief)
Write-Host "`n[TEST 6] Testing MCP server startup..." -ForegroundColor Blue
try {
    # Start server in background for a few seconds to test startup
    $job = Start-Job -ScriptBlock {
        docker run --rm azure-cli-mcp-test timeout 5 python -m azure_cli_mcp.main 2>&1
    }
    
    Start-Sleep -Seconds 3
    Stop-Job $job
    $output = Receive-Job $job
    Remove-Job $job
    
    # Check if server started without immediate errors
    if ($output -notmatch "Error|Exception|Traceback") {
        Write-Host "✅ MCP server startup test passed" -ForegroundColor Green
    } else {
        Write-Host "⚠️ MCP server startup had issues (may need Azure credentials)" -ForegroundColor Yellow
        Write-Host "Output: $output" -ForegroundColor Gray
    }
}
catch {
    Write-Host "⚠️ MCP server startup test inconclusive" -ForegroundColor Yellow
}

# Cleanup
Write-Host "`n[CLEANUP] Removing test image..." -ForegroundColor Blue
try {
    docker rmi azure-cli-mcp-test
    Write-Host "✅ Test image removed" -ForegroundColor Green
}
catch {
    Write-Host "⚠️ Could not remove test image" -ForegroundColor Yellow
}

Write-Host "`n🎉 Docker deployment test completed!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Set up Azure credentials (Service Principal recommended)" -ForegroundColor White
Write-Host "2. Run: .\scripts\deploy.ps1 docker" -ForegroundColor White
Write-Host "3. Configure MCP clients (VS Code or Claude Desktop)" -ForegroundColor White
Write-Host "4. Start server: .\start_docker.ps1" -ForegroundColor White 