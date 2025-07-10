"""Tests for Azure Login Handler."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from azure_cli_mcp.services.azure_login_handler import AzureLoginHandler


class TestAzureLoginHandler:
    """Test cases for Azure Login Handler."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = AzureLoginHandler()
    
    def test_initialization(self):
        """Test handler initialization."""
        assert self.handler.logger is not None
        assert self.handler.current_process is None
    
    @pytest.mark.asyncio
    async def test_handle_az_login_command_device_code(self):
        """Test handling az login command with device code."""
        mock_process = MagicMock()
        mock_process.stdout = AsyncMock()
        mock_process.stderr = AsyncMock()
        mock_process.stdin = MagicMock()
        mock_process.returncode = 0

        with patch('asyncio.create_subprocess_shell', return_value=mock_process) as mock_create:
            with patch.object(self.handler, '_handle_login_background', return_value="Login successful") as mock_background:
                result = await self.handler.handle_az_login_command("az login")

                assert result == "Login successful"
                mock_background.assert_called_once_with(mock_process)
                # Should add device code flag if not present
                mock_create.assert_called_once()
                call_args = mock_create.call_args[0][0]
                assert "--use-device-code" in call_args
    
    @pytest.mark.asyncio
    async def test_handle_az_login_command_already_has_device_code(self):
        """Test handling az login command that already has device code flag."""
        mock_process = MagicMock()
        mock_process.stdout = AsyncMock()
        mock_process.stderr = AsyncMock()
        mock_process.stdin = MagicMock()
        mock_process.returncode = 0

        with patch('asyncio.create_subprocess_shell', return_value=mock_process) as mock_create:
            with patch.object(self.handler, '_handle_login_background', return_value="Login successful") as mock_background:
                result = await self.handler.handle_az_login_command("az login --use-device-code")

                assert result == "Login successful"
                mock_background.assert_called_once_with(mock_process)
                # Should not add duplicate device code flag
                mock_create.assert_called_once()
                call_args = mock_create.call_args[0][0]
                assert call_args.count("--use-device-code") == 1
    
    @pytest.mark.asyncio
    async def test_handle_az_login_command_with_existing_process(self):
        """Test handling login command with existing process."""
        # Set up existing process
        existing_process = MagicMock()
        existing_process.returncode = None  # Still running
        existing_process.terminate = MagicMock()
        existing_process.wait = AsyncMock(return_value=0)
        self.handler.current_process = existing_process

        mock_process = MagicMock()
        mock_process.stdout = AsyncMock()
        mock_process.stderr = AsyncMock()
        mock_process.stdin = MagicMock()
        mock_process.returncode = 0

        with patch('asyncio.create_subprocess_shell', return_value=mock_process) as mock_create:
            with patch.object(self.handler, '_handle_login_background', return_value="Login successful") as mock_background:
                result = await self.handler.handle_az_login_command("az login")

                assert result == "Login successful"
                # Should terminate existing process
                existing_process.terminate.assert_called_once()
                mock_background.assert_called_once_with(mock_process)
    
    @pytest.mark.asyncio
    async def test_handle_az_login_command_process_creation_failure(self):
        """Test handling login command when process creation fails."""
        with patch('asyncio.create_subprocess_shell') as mock_create:
            mock_create.side_effect = Exception("Process creation failed")
    
            result = await self.handler.handle_az_login_command("az login")

            assert result.startswith("Error: Failed to start login process")
    
    @pytest.mark.asyncio
    async def test_handle_login_background_with_device_code(self):
        """Test background login handling with device code."""
        mock_process = MagicMock()
        mock_process.stdout = AsyncMock()
        mock_process.stderr = AsyncMock()
        mock_process.stdin = MagicMock()
        mock_process.returncode = 0

        # Mock the _read_lines method
        mock_stdout_lines = [
            "To sign in, use a web browser to open the page https://microsoft.com/devicelogin",
            "and enter the code ABC123 to authenticate."
        ]
        mock_stderr_lines = ["Warning: some warning"]

        with patch.object(self.handler, '_read_lines') as mock_read:
            mock_read.side_effect = [
                mock_stdout_lines,  # First call for stdout
                mock_stderr_lines   # Second call for stderr
            ]

            # Mock wait as an async method
            mock_process.wait = AsyncMock(return_value=0)
            
            result = await self.handler._handle_login_background(mock_process)

            # Should return device code information
            assert "device" in result.lower() or "code" in result.lower()
            assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_handle_login_background_process_failure(self):
        """Test background login handling when process fails."""
        mock_process = MagicMock()
        mock_process.stdout = AsyncMock()
        mock_process.stderr = AsyncMock()
        mock_process.stdin = MagicMock()
        mock_process.returncode = 1

        mock_stdout_lines = ["Error: Login failed"]
        mock_stderr_lines = ["Authentication error"]

        with patch.object(self.handler, '_read_lines') as mock_read:
            mock_read.side_effect = [mock_stdout_lines, mock_stderr_lines]

            # Mock wait as an async method
            mock_process.wait = AsyncMock(return_value=1)
            
            result = await self.handler._handle_login_background(mock_process)

            assert result == "Error: Login failed"
    
    @pytest.mark.asyncio
    async def test_handle_login_background_exception(self):
        """Test background login handling with exception."""
        mock_process = MagicMock()
        mock_process.stdout = AsyncMock()
        mock_process.stderr = AsyncMock()
        mock_process.stdin = MagicMock()

        with patch.object(self.handler, '_read_lines') as mock_read:
            mock_read.side_effect = Exception("Reading failed")

            result = await self.handler._handle_login_background(mock_process)

            assert result.startswith("Error:")
            assert "Reading failed" in result
    
    @pytest.mark.asyncio
    async def test_read_lines_normal_operation(self):
        """Test reading lines from stream."""
        mock_stream = AsyncMock()
        mock_lines = [b"Line 1\n", b"Line 2\n", b"Line 3\n", b""]  # EOF

        # Create a proper async iterator
        async def mock_readline():
            for line in mock_lines:
                return line

        mock_stream.readline = AsyncMock(side_effect=mock_lines)

        result = await self.handler._read_lines(mock_stream)

        assert len(result) == 3
        assert result[0] == "Line 1"
        assert result[1] == "Line 2"
        assert result[2] == "Line 3"
    
    @pytest.mark.asyncio
    async def test_read_lines_empty_stream(self):
        """Test reading lines from empty stream."""
        mock_stream = AsyncMock()
        mock_stream.readline = AsyncMock(return_value=b"")

        result = await self.handler._read_lines(mock_stream)

        assert result == []
    
    @pytest.mark.asyncio
    async def test_read_lines_with_unicode(self):
        """Test reading lines with Unicode characters."""
        mock_stream = AsyncMock()
        mock_lines = [b"Line with \xc3\xa9 accent\n", b"Another line\n", b""]

        mock_stream.readline = AsyncMock(side_effect=mock_lines)

        result = await self.handler._read_lines(mock_stream)

        assert len(result) == 2
        assert "é" in result[0]  # Should properly decode UTF-8
        assert result[1] == "Another line"
    
    @pytest.mark.asyncio
    async def test_read_lines_decode_error(self):
        """Test reading lines with decode errors."""
        mock_stream = AsyncMock()
        mock_lines = [b"\xff\xfe invalid utf-8\n", b""]

        mock_stream.readline = AsyncMock(side_effect=mock_lines)

        result = await self.handler._read_lines(mock_stream)

        # Should handle decode errors gracefully
        assert len(result) >= 0  # Should not crash
    
    @pytest.mark.asyncio
    async def test_process_cleanup_on_success(self):
        """Test process cleanup after successful login."""
        mock_process = MagicMock()
        mock_process.stdout = AsyncMock()
        mock_process.stderr = AsyncMock()
        mock_process.stdin = MagicMock()
        mock_process.returncode = 0

        with patch('asyncio.create_subprocess_shell', return_value=mock_process):
            with patch.object(self.handler, '_handle_login_background', return_value="Login successful") as mock_background:
                await self.handler.handle_az_login_command("az login")

                # Process should be cleared after completion
                assert self.handler.current_process is None
    
    @pytest.mark.asyncio
    async def test_process_cleanup_on_failure(self):
        """Test process cleanup after failed login."""
        mock_process = MagicMock()
        mock_process.stdout = AsyncMock()
        mock_process.stderr = AsyncMock()
        mock_process.stdin = MagicMock()
        mock_process.returncode = 1

        with patch('asyncio.create_subprocess_shell', return_value=mock_process):
            with patch.object(self.handler, '_handle_login_background', return_value="Error: Login failed") as mock_background:
                await self.handler.handle_az_login_command("az login")

                # Process should be cleared even after failure
                assert self.handler.current_process is None
    
    @pytest.mark.asyncio
    async def test_multiple_concurrent_login_attempts(self):
        """Test handling multiple concurrent login attempts."""
        mock_process1 = MagicMock()
        mock_process1.returncode = None  # Still running
        mock_process1.terminate = MagicMock()
        mock_process1.wait = AsyncMock(return_value=0)

        mock_process2 = MagicMock()
        mock_process2.stdout = AsyncMock()
        mock_process2.stderr = AsyncMock()
        mock_process2.stdin = MagicMock()
        mock_process2.returncode = 0

        with patch('asyncio.create_subprocess_shell', return_value=mock_process2):
            with patch.object(self.handler, '_handle_login_background', return_value="Login successful") as mock_background:
                # Start first login
                self.handler.current_process = mock_process1

                # Start second login (should terminate first)
                result = await self.handler.handle_az_login_command("az login")

                assert result == "Login successful"
                # Should terminate first process
                mock_process1.terminate.assert_called_once()
    
    def test_logger_configuration(self):
        """Test logger is properly configured."""
        assert self.handler.logger.name == "azure_cli_mcp.services.azure_login_handler"
    
    @pytest.mark.asyncio
    async def test_handle_az_login_command_with_additional_flags(self):
        """Test handling login command with additional flags."""
        mock_process = MagicMock()
        mock_process.stdout = AsyncMock()
        mock_process.stderr = AsyncMock()
        mock_process.stdin = MagicMock()
        mock_process.returncode = 0

        with patch('asyncio.create_subprocess_shell', return_value=mock_process) as mock_create:
            with patch.object(self.handler, '_handle_login_background', return_value="Login successful") as mock_background:
                result = await self.handler.handle_az_login_command("az login --tenant test-tenant")

                assert result == "Login successful"
                mock_background.assert_called_once_with(mock_process)
                # Should preserve additional flags
                call_args = mock_create.call_args[0][0]
                assert "--tenant test-tenant" in call_args
                assert "--use-device-code" in call_args
    
    @pytest.mark.asyncio
    async def test_process_termination_timeout(self):
        """Test process termination with timeout."""
        mock_process = MagicMock()
        mock_process.returncode = None  # Still running
        mock_process.terminate = MagicMock()
        mock_process.wait = AsyncMock(side_effect=asyncio.TimeoutError())
        mock_process.kill = MagicMock()

        self.handler.current_process = mock_process

        new_mock_process = MagicMock()
        new_mock_process.stdout = AsyncMock()
        new_mock_process.stderr = AsyncMock()
        new_mock_process.stdin = MagicMock()
        new_mock_process.returncode = 0

        with patch('asyncio.create_subprocess_shell', return_value=new_mock_process):
            with patch.object(self.handler, '_handle_login_background', return_value="Login successful"):
                result = await self.handler.handle_az_login_command("az login")

                # Should attempt to terminate and then kill
                mock_process.terminate.assert_called_once()
                mock_process.kill.assert_called_once()
                assert result == "Login successful" 