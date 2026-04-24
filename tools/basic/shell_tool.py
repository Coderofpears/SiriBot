"""Shell command execution tool."""
import subprocess
import logging
from typing import Optional
from ..registry import Tool, ToolCategory

logger = logging.getLogger(__name__)


class ShellTool:
    """Execute shell commands."""
    
    name = "shell"
    description = "Execute shell commands on the system"
    category = ToolCategory.SYSTEM
    
    @staticmethod
    async def execute(command: str, timeout: int = 30, cwd: Optional[str] = None) -> dict:
        """Execute a shell command."""
        logger.info(f"Executing shell: {command}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Command timed out after {timeout}s",
                "returncode": -1
            }
        
        except Exception as e:
            logger.error(f"Shell execution failed: {e}")
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }


def get_shell_tool() -> Tool:
    """Get the shell tool definition."""
    return Tool(
        name="shell",
        description="Execute shell commands. Args: command (str), timeout (int, optional), cwd (str, optional)",
        category=ToolCategory.SYSTEM,
        function=ShellTool.execute,
        examples=[
            "List files in directory",
            "Check system info",
            "Run a script"
        ]
    )
