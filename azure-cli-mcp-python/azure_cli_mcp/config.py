"""Configuration management for Azure CLI MCP Server."""

import json
import os
from typing import Any, Dict, Optional

from pydantic import Field, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings using Pydantic."""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
        frozen=True,  # Make settings immutable
        # Allow both prefixed and direct environment variables
        env_prefix="",
    )

    # Application settings
    app_name: str = "azure-cli-mcp"

    # Azure credentials (individual fields)
    azure_tenant_id: Optional[str] = Field(default=None, alias="AZURE_TENANT_ID")
    azure_client_id: Optional[str] = Field(default=None, alias="AZURE_CLIENT_ID")
    azure_client_secret: Optional[str] = Field(
        default=None, alias="AZURE_CLIENT_SECRET"
    )
    azure_subscription_id: Optional[str] = Field(
        default=None, alias="AZURE_SUBSCRIPTION_ID"
    )

    # Command execution settings
    command_timeout: int = Field(
        default=300, ge=1, le=3600, alias="COMMAND_TIMEOUT"
    )  # 1 second to 1 hour
    max_concurrent_commands: int = Field(
        default=5, ge=1, le=50, alias="MAX_CONCURRENT_COMMANDS"
    )

    # MCP settings
    mcp_server_enabled: bool = True
    mcp_server_stdio: bool = True
    mcp_server_name: str = "azure-cli-mcp"

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: str = Field(default="azure_cli_mcp.log", alias="LOG_FILE")

    # Web settings
    web_host: str = Field(default="127.0.0.1", alias="WEB_HOST")
    web_port: int = Field(
        default=8000, ge=1024, le=65535, alias="WEB_PORT"
    )  # Valid port range

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            return "INFO"  # Default to INFO for invalid values
        return v.upper()

    @computed_field
    def azure_credentials(self) -> Optional[Dict[str, Optional[str]]]:
        """Get Azure credentials as a dictionary."""
        if self.has_azure_credentials():
            return {
                "tenant_id": self.azure_tenant_id,
                "client_id": self.azure_client_id,
                "client_secret": self.azure_client_secret,
            }
        return None

    def has_azure_credentials(self) -> bool:
        """Check if all required Azure credentials are present."""
        return all(
            [self.azure_tenant_id, self.azure_client_id, self.azure_client_secret]
        )

    def get_azure_credentials_json(self) -> Optional[str]:
        """Get Azure credentials as JSON string for Azure CLI authentication."""
        if self.has_azure_credentials():
            credentials = {
                "tenantId": self.azure_tenant_id,
                "clientId": self.azure_client_id,
                "clientSecret": self.azure_client_secret,
            }
            if self.azure_subscription_id:
                credentials["subscriptionId"] = self.azure_subscription_id
            return json.dumps(credentials)
        return None


# Global settings instance
settings = Settings()
