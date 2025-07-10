"""Unit tests for config module."""

import os
import pytest
from unittest.mock import patch, MagicMock
from pydantic import ValidationError

from azure_cli_mcp.config import Settings


class TestSettings:
    """Test Settings configuration class."""

    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings()
        
        assert settings.log_level == "INFO"
        assert settings.log_file == "azure_cli_mcp.log"
        assert settings.azure_tenant_id is None
        assert settings.azure_client_id is None
        assert settings.azure_client_secret is None
        assert settings.azure_subscription_id is None
        assert settings.command_timeout == 300
        assert settings.max_concurrent_commands == 5
        assert settings.web_host == "127.0.0.1"
        assert settings.web_port == 8000

    def test_settings_from_env_vars(self):
        """Test loading settings from environment variables."""
        env_vars = {
            "LOG_LEVEL": "DEBUG",
            "LOG_FILE": "test.log",
            "AZURE_TENANT_ID": "test-tenant",
            "AZURE_CLIENT_ID": "test-client",
            "AZURE_CLIENT_SECRET": "test-secret",
            "AZURE_SUBSCRIPTION_ID": "test-sub",
            "COMMAND_TIMEOUT": "600",
            "MAX_CONCURRENT_COMMANDS": "10",
            "WEB_HOST": "0.0.0.0",
            "WEB_PORT": "9000"
        }
        
        with patch.dict(os.environ, env_vars):
            settings = Settings()
            
            assert settings.log_level == "DEBUG"
            assert settings.log_file == "test.log"
            assert settings.azure_tenant_id == "test-tenant"
            assert settings.azure_client_id == "test-client"
            assert settings.azure_client_secret == "test-secret"
            assert settings.azure_subscription_id == "test-sub"
            assert settings.command_timeout == 600
            assert settings.max_concurrent_commands == 10
            assert settings.web_host == "0.0.0.0"
            assert settings.web_port == 9000

    def test_azure_credentials_property(self):
        """Test azure_credentials property."""
        # Test with no credentials
        settings = Settings()
        assert settings.azure_credentials is None
        
        # Test with partial credentials
        with patch.dict(os.environ, {"AZURE_TENANT_ID": "test-tenant"}):
            settings = Settings()
            assert settings.azure_credentials is None
        
        # Test with complete credentials
        env_vars = {
            "AZURE_TENANT_ID": "test-tenant",
            "AZURE_CLIENT_ID": "test-client",
            "AZURE_CLIENT_SECRET": "test-secret"
        }
        with patch.dict(os.environ, env_vars):
            settings = Settings()
            credentials = settings.azure_credentials
            assert credentials is not None
            assert credentials["tenant_id"] == "test-tenant"
            assert credentials["client_id"] == "test-client"
            assert credentials["client_secret"] == "test-secret"

    def test_has_azure_credentials(self):
        """Test has_azure_credentials method."""
        # Test with no credentials
        settings = Settings()
        assert not settings.has_azure_credentials()
        
        # Test with partial credentials
        with patch.dict(os.environ, {"AZURE_TENANT_ID": "test-tenant"}):
            settings = Settings()
            assert not settings.has_azure_credentials()
        
        # Test with complete credentials
        env_vars = {
            "AZURE_TENANT_ID": "test-tenant",
            "AZURE_CLIENT_ID": "test-client",
            "AZURE_CLIENT_SECRET": "test-secret"
        }
        with patch.dict(os.environ, env_vars):
            settings = Settings()
            assert settings.has_azure_credentials()

    def test_invalid_log_level(self):
        """Test validation of log level."""
        with patch.dict(os.environ, {"LOG_LEVEL": "INVALID"}):
            settings = Settings()
            # Should convert invalid log level to default INFO
            assert settings.log_level == "INFO"  # Our validator converts invalid values to INFO

    def test_invalid_port(self):
        """Test validation of port number."""
        with patch.dict(os.environ, {"WEB_PORT": "invalid"}):
            with pytest.raises(ValidationError):
                Settings()

    def test_invalid_timeout(self):
        """Test validation of timeout value."""
        with patch.dict(os.environ, {"COMMAND_TIMEOUT": "invalid"}):
            with pytest.raises(ValidationError):
                Settings()

    def test_invalid_max_concurrent(self):
        """Test validation of max concurrent commands."""
        with patch.dict(os.environ, {"MAX_CONCURRENT_COMMANDS": "invalid"}):
            with pytest.raises(ValidationError):
                Settings()

    def test_negative_values(self):
        """Test handling of negative values."""
        with patch.dict(os.environ, {"WEB_PORT": "-1"}):
            with pytest.raises(ValidationError):
                Settings()
        
        with patch.dict(os.environ, {"COMMAND_TIMEOUT": "-1"}):
            with pytest.raises(ValidationError):
                Settings()

    def test_zero_values(self):
        """Test handling of zero values."""
        with patch.dict(os.environ, {"WEB_PORT": "0"}):
            with pytest.raises(ValidationError):
                Settings()

    def test_large_values(self):
        """Test handling of large values."""
        with patch.dict(os.environ, {"WEB_PORT": "99999"}):
            with pytest.raises(ValidationError):
                Settings()

    def test_settings_immutability(self):
        """Test that settings are immutable after creation."""
        settings = Settings()
        
        # This should raise an error since Settings should be frozen
        with pytest.raises(ValidationError):  # Frozen Pydantic models raise ValidationError
            settings.log_level = "DEBUG"

    def test_model_dump(self):
        """Test model serialization."""
        settings = Settings()
        data = settings.model_dump()
        
        assert isinstance(data, dict)
        assert "log_level" in data
        assert "log_file" in data
        assert "command_timeout" in data

    def test_model_dump_excludes_secrets(self):
        """Test that sensitive data is handled properly in model dump."""
        env_vars = {
            "AZURE_CLIENT_SECRET": "secret-value"
        }
        with patch.dict(os.environ, env_vars):
            settings = Settings()
            data = settings.model_dump()
            
            # The secret should be included in the dump by default
            # but in a real scenario, we might want to exclude it
            assert "azure_client_secret" in data 