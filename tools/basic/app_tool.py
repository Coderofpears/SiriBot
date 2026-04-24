"""Application control tool."""
import subprocess
import logging
import platform
from typing import Optional
from ..registry import Tool, ToolCategory

logger = logging.getLogger(__name__)


class AppTool:
    """Application control operations."""
    
    name = "app"
    description = "Open and close applications"
    category = ToolCategory.APP
    
    @staticmethod
    async def open(app_name: str, url: Optional[str] = None) -> dict:
        """Open an application or URL."""
        logger.info(f"Opening: {app_name or url}")
        
        try:
            system = platform.system()
            
            if url:
                # Open URL with default browser
                if system == "Darwin":
                    subprocess.run(["open", url])
                elif system == "Linux":
                    subprocess.run(["xdg-open", url])
                else:
                    subprocess.run(["start", url], shell=True)
            
            elif app_name:
                if system == "Darwin":
                    subprocess.run(["open", "-a", app_name])
                elif system == "Linux":
                    subprocess.run([app_name])
                else:
                    subprocess.run(["start", app_name], shell=True)
            else:
                return {"success": False, "error": "Must provide app_name or url"}
            
            return {"success": True, "opened": app_name or url}
        
        except Exception as e:
            logger.error(f"App open failed: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def close(app_name: str) -> dict:
        """Close an application."""
        logger.info(f"Closing: {app_name}")
        
        try:
            system = platform.system()
            
            if system == "Darwin":
                subprocess.run(["osascript", "-e", f'tell application "{app_name}" to quit'])
            elif system == "Linux":
                subprocess.run(["killall", app_name])
            else:
                subprocess.run(["taskkill", "/IM", f"{app_name}.exe"], shell=True)
            
            return {"success": True, "closed": app_name}
        
        except Exception as e:
            logger.error(f"App close failed: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def list_running() -> dict:
        """List running applications."""
        logger.info("Listing running apps")
        
        try:
            system = platform.system()
            
            if system == "Darwin":
                result = subprocess.run(
                    ["osascript", "-e", 'tell application "System Events" to name of every process'],
                    capture_output=True,
                    text=True
                )
                apps = [a.strip() for a in result.stdout.split(", ")]
            elif system == "Linux":
                result = subprocess.run(["ps", "-eo", "comm"], capture_output=True, text=True)
                apps = list(set(result.stdout.strip().split("\n")))
            else:
                result = subprocess.run(["tasklist"], capture_output=True, text=True)
                apps = result.stdout.strip().split("\n")[3:]
            
            return {"success": True, "apps": apps}
        
        except Exception as e:
            logger.error(f"App list failed: {e}")
            return {"success": False, "error": str(e)}


def get_app_tools() -> list[Tool]:
    """Get app tool definitions."""
    return [
        Tool(
            name="app_open",
            description="Open an application or URL. Args: app_name (str, optional), url (str, optional)",
            category=ToolCategory.APP,
            function=AppTool.open
        ),
        Tool(
            name="app_close",
            description="Close an application. Args: app_name (str)",
            category=ToolCategory.APP,
            function=AppTool.close
        ),
        Tool(
            name="app_list",
            description="List running applications. No args required",
            category=ToolCategory.APP,
            function=AppTool.list_running
        ),
    ]
