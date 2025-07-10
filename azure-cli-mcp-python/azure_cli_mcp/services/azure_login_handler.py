"""Azure Login Handler for device code authentication."""

import asyncio
import logging
import re
from typing import List, Optional


class AzureLoginHandler:
    """Handler for Azure CLI login with device code authentication."""

    def __init__(self) -> None:
        """Initialize Azure login handler."""
        self.logger = logging.getLogger(__name__)
        self.current_process: Optional[asyncio.subprocess.Process] = None
        self.logger.info("AzureLoginHandler initialized")

    async def handle_az_login_command(self, command: str) -> str:
        """Handle Azure CLI login with device code authentication."""
        self.logger.info(f"Handling 'az login' command: {command}")

        # Ensure --use-device-code flag is present
        if "--use-device-code" not in command:
            command += " --use-device-code"

        try:
            # Cancel previous login process if running
            if self.current_process and not self.current_process.returncode:
                self.logger.info("Cancelling previous 'az login' process")
                self.current_process.terminate()
                try:
                    await asyncio.wait_for(self.current_process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    self.logger.warning(
                        "Previous login process did not terminate gracefully"
                    )
                    self.current_process.kill()

            # Start new login process
            self.current_process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE,
                shell=True,
            )

            # Handle login process in background and get result
            result = await self._handle_login_background(self.current_process)

            # Clean up process reference
            self.current_process = None

            return result

        except Exception as e:
            self.logger.error(f"Error running 'az login' command: {e}")
            # Clean up process reference on error
            self.current_process = None
            return f"Error: Failed to start login process - {str(e)}"

    async def _handle_login_background(
        self, process: asyncio.subprocess.Process
    ) -> str:
        """Handle login process in background."""
        try:
            self.logger.info("Handling 'az login' process in the background")

            # Read stdout and stderr
            stdout_lines = (
                await self._read_lines(process.stdout) if process.stdout else []
            )
            stderr_lines = (
                await self._read_lines(process.stderr) if process.stderr else []
            )

            # Wait for process completion
            return_code = await process.wait()

            # Combine output
            all_output = []
            all_output.extend(stdout_lines)
            all_output.extend(stderr_lines)

            if return_code != 0:
                self.logger.error(
                    f"Login process failed with return code: {return_code}"
                )
                return f"Error: Login failed"

            # Look for device code information in output
            device_code_info = []
            for line in all_output:
                if any(
                    keyword in line.lower()
                    for keyword in ["device", "code", "browser", "authenticate"]
                ):
                    device_code_info.append(line)

            if device_code_info:
                return "\n".join(device_code_info)

            # Return full output if no device code found
            return "\n".join(all_output) if all_output else "Login successful"

        except Exception as e:
            self.logger.error(f"Error in background login handling: {e}")
            return f"Error: {str(e)}"

    async def _read_lines(self, stream: asyncio.StreamReader) -> List[str]:
        """Asynchronously read lines from stream."""
        if not stream:
            return []

        lines = []
        try:
            while True:
                line = await stream.readline()
                if not line:
                    break
                try:
                    decoded_line = line.decode("utf-8").strip()
                    if decoded_line:  # Skip empty lines
                        lines.append(decoded_line)
                        self.logger.debug(f"Read line: {decoded_line}")
                except UnicodeDecodeError as e:
                    self.logger.warning(f"Could not decode line: {e}")
                    # Try with error handling
                    try:
                        decoded_line = line.decode("utf-8", errors="replace").strip()
                        if decoded_line:
                            lines.append(decoded_line)
                    except Exception:
                        pass  # Skip lines that can't be decoded
        except Exception as e:
            self.logger.error(f"Error reading stream: {e}")

        return lines
