"""Tests for Azure CLI Service."""

import asyncio
import subprocess
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from azure_cli_mcp.config import Settings
from azure_cli_mcp.services.azure_cli_service import AzureCliService


class TestAzureCliService:
    """Test cases for Azure CLI Service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.settings = Settings()
        self.service = AzureCliService(self.settings)
    
    def test_initialization(self):
        """Test service initialization."""
        assert self.service.settings == self.settings
        assert self.service.logger is not None
        assert self.service.login_handler is not None
    
    def test_initialization_with_credentials(self):
        """Test service initialization with Azure credentials."""
        with patch.dict('os.environ', {
            'AZURE_TENANT_ID': 'test-tenant',
            'AZURE_CLIENT_ID': 'test-client',
            'AZURE_CLIENT_SECRET': 'test-secret'
        }):
            settings = Settings()
            service = AzureCliService(settings)
            
            assert service.settings == settings
            assert service.logger is not None
            assert service.login_handler is not None
    
    @pytest.mark.asyncio
    async def test_execute_azure_cli_valid_command(self):
        """Test executing valid Azure CLI command."""
        with patch.object(self.service, '_run_azure_cli_command') as mock_run:
            mock_run.return_value = "Command output"
            
            result = await self.service.execute_azure_cli("az --version")
            
            assert result == "Command output"
            mock_run.assert_called_once_with("az --version")
    
    @pytest.mark.asyncio
    async def test_execute_azure_cli_invalid_command(self):
        """Test executing invalid command."""
        result = await self.service.execute_azure_cli("invalid command")
        
        assert result.startswith("Error: Invalid command")
    
    @pytest.mark.asyncio
    async def test_execute_azure_cli_empty_command(self):
        """Test executing empty command."""
        result = await self.service.execute_azure_cli("")
        
        assert result.startswith("Error: Invalid command")
    
    @pytest.mark.asyncio
    async def test_execute_azure_cli_command_with_injection(self):
        """Test command injection protection."""
        result = await self.service.execute_azure_cli("az account list; rm -rf /")
        
        assert result.startswith("Error: Invalid command")
    
    @pytest.mark.asyncio
    async def test_execute_azure_cli_login_command(self):
        """Test executing login command delegates to login handler."""
        with patch.object(self.service.login_handler, 'handle_az_login_command') as mock_handler:
            mock_handler.return_value = "Login result"
            
            result = await self.service.execute_azure_cli("az login")
            
            mock_handler.assert_called_once_with("az login")
            assert result == "Login result"
    
    @pytest.mark.asyncio
    async def test_execute_azure_cli_login_device_code(self):
        """Test executing login command with device code."""
        with patch.object(self.service.login_handler, 'handle_az_login_command') as mock_handler:
            mock_handler.return_value = "Login with device code result"
            
            result = await self.service.execute_azure_cli("az login --use-device-code")
            
            mock_handler.assert_called_once_with("az login --use-device-code")
            assert result == "Login with device code result"
    
    @pytest.mark.asyncio
    async def test_run_azure_cli_command_success(self):
        """Test successful command execution."""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"Command output"
        mock_process.stderr = b""

        with patch('asyncio.create_subprocess_shell', return_value=mock_process) as mock_create:
            mock_process.communicate = AsyncMock(return_value=(b"Command output", b""))

            result = await self.service._run_azure_cli_command("az --version")

            assert result == "Command output"
            mock_create.assert_called_once_with(
                "az --version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                shell=True
            )
    
    @pytest.mark.asyncio
    async def test_run_azure_cli_command_failure(self):
        """Test failed command execution."""
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stdout = b""
        mock_process.stderr = b"Command failed"

        with patch('asyncio.create_subprocess_shell', return_value=mock_process) as mock_create:
            mock_process.communicate = AsyncMock(return_value=(b"", b"Command failed"))

            result = await self.service._run_azure_cli_command("az invalid-command")

            assert result.startswith("Error: ")
            assert "Command failed" in result
    
    @pytest.mark.asyncio
    async def test_run_azure_cli_command_with_output_and_error(self):
        """Test command execution with both stdout and stderr."""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"Command output"
        mock_process.stderr = b"Warning message"

        with patch('asyncio.create_subprocess_shell', return_value=mock_process) as mock_create:
            mock_process.communicate = AsyncMock(return_value=(b"Command output", b"Warning message"))

            result = await self.service._run_azure_cli_command("az --version")

            # Should combine stdout and stderr
            assert "Command output" in result
            assert "Warning message" in result
    
    @pytest.mark.asyncio
    async def test_run_azure_cli_command_timeout(self):
        """Test command execution timeout."""
        with patch('asyncio.create_subprocess_shell') as mock_create:
            mock_create.side_effect = asyncio.TimeoutError("Command timed out")

            result = await self.service._run_azure_cli_command("az long-running-command")

            assert result.startswith("Error: Command timed out")
    
    @pytest.mark.asyncio
    async def test_run_azure_cli_command_exception(self):
        """Test command execution with unexpected exception."""
        with patch('asyncio.create_subprocess_shell') as mock_create:
            mock_create.side_effect = Exception("Unexpected error")

            result = await self.service._run_azure_cli_command("az command")

            assert result.startswith("Error: ")
            assert "Unexpected error" in result
    
    @pytest.mark.asyncio
    async def test_authenticate_with_credentials(self):
        """Test authentication with service principal credentials."""
        with patch.dict('os.environ', {
            'AZURE_TENANT_ID': 'test-tenant',
            'AZURE_CLIENT_ID': 'test-client',
            'AZURE_CLIENT_SECRET': 'test-secret'
        }):
            settings = Settings()
            service = AzureCliService(settings)
            
            azure_creds = settings.get_azure_credentials_json()

            with patch.object(service, '_run_azure_cli_command') as mock_run:
                mock_run.return_value = "Login successful"

                result = await service._authenticate(azure_creds)

                assert result == "Login successful"
                mock_run.assert_called_once()
                # Check that the command contains the expected login parameters
                called_command = mock_run.call_args[0][0]
                assert "az login --service-principal" in called_command
                assert "test-tenant" in called_command
                assert "test-client" in called_command
                assert "test-secret" in called_command
    
    @pytest.mark.asyncio
    async def test_authenticate_without_credentials(self):
        """Test authentication without credentials."""
        # Service initialized without credentials
        result = await self.service._authenticate('{}')
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_authenticate_invalid_json(self):
        """Test authentication with invalid JSON."""
        result = await self.service._authenticate('invalid json')
        
        assert result.startswith("Error:")
    
    @pytest.mark.asyncio
    async def test_authenticate_authentication_failure(self):
        """Test authentication failure."""
        with patch.dict('os.environ', {
            'AZURE_TENANT_ID': 'test-tenant',
            'AZURE_CLIENT_ID': 'test-client',
            'AZURE_CLIENT_SECRET': 'test-secret'
        }):
            settings = Settings()
            service = AzureCliService(settings)
            
            azure_creds = settings.get_azure_credentials_json()

            with patch.object(service, '_run_azure_cli_command') as mock_run:
                mock_run.return_value = "Error: Authentication failed"
    
                result = await service._authenticate(azure_creds)
    
                assert result == "Error: Authentication failed"
    
    def test_validate_command_valid_commands(self):
        """Test command validation for valid commands."""
        valid_commands = [
            "az --version",
            "az account list",
            "az login",
            "az group list",
            "az vm list"
        ]

        for command in valid_commands:
            assert self.service._validate_command(command) is True
    
    def test_validate_command_invalid_commands(self):
        """Test command validation for invalid commands."""
        invalid_commands = [
            "invalid command",
            "ls -la",
            "rm -rf /",
            "powershell Get-Process",
            "cmd /c dir",
            "",
            "   ",
            "az; rm -rf /",  # Command injection attempt
            "az && malicious-command"  # Command chaining attempt
        ]

        for command in invalid_commands:
            assert self.service._validate_command(command) is False
    
    def test_sanitize_command_basic(self):
        """Test basic command sanitization."""
        sanitized = self.service._sanitize_command("az --version")
        assert sanitized == "az --version"
    
    def test_sanitize_command_with_quotes(self):
        """Test command sanitization with quotes."""
        sanitized = self.service._sanitize_command('az vm create --name "test vm"')
        assert 'az vm create --name "test vm"' == sanitized
    
    def test_sanitize_command_removes_dangerous_chars(self):
        """Test that dangerous characters are handled."""
        # This depends on implementation - might strip or escape
        command = "az account list; echo 'dangerous'"
        sanitized = self.service._sanitize_command(command)
        
        # Should remove dangerous characters
        assert ";" not in sanitized
        assert sanitized == "az account list echo 'dangerous'"
    
    def test_logger_configuration(self):
        """Test logger is properly configured."""
        assert self.service.logger.name == "azure_cli_mcp.services.azure_cli_service"
        assert self.service.logger.level in [
            10, 20, 30, 40, 50  # DEBUG, INFO, WARNING, ERROR, CRITICAL
        ]
    
    def test_settings_integration(self):
        """Test integration with settings."""
        # Test that settings are properly stored
        assert self.service.settings == self.settings
        
        # Test that settings are read-only (frozen)
        with pytest.raises(Exception):  # Should raise ValidationError for frozen instance
            self.service.settings.command_timeout = 600
    
    @pytest.mark.asyncio
    async def test_execute_azure_cli_exception_handling(self):
        """Test exception handling in execute_azure_cli."""
        with patch.object(self.service, '_run_azure_cli_command') as mock_run:
            mock_run.side_effect = Exception("Unexpected error")

            result = await self.service.execute_azure_cli("az --version")

            assert result.startswith("Error: Command execution failed")
            assert "Unexpected error" in result 