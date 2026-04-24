"""Tool registry for managing available tools."""
import logging
from typing import Callable, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ToolCategory(Enum):
    """Categories of tools."""
    SYSTEM = "system"
    FILE = "file"
    APP = "app"
    NETWORK = "network"
    CUSTOM = "custom"


@dataclass
class Tool:
    """A callable tool."""
    name: str
    description: str
    category: ToolCategory
    function: Callable
    parameters: dict = field(default_factory=dict)
    examples: list[str] = field(default_factory=list)


class ToolRegistry:
    """Registry for all available tools."""
    
    def __init__(self):
        self._tools: dict[str, Tool] = {}
    
    def register(self, tool: Tool):
        """Register a new tool."""
        self._tools[tool.name] = tool
        logger.debug(f"Registered tool: {tool.name}")
    
    def get_tool(self, name: str) -> Optional[Callable]:
        """Get a tool by name."""
        tool = self._tools.get(name)
        return tool.function if tool else None
    
    def get_tool_info(self, name: str) -> Optional[Tool]:
        """Get tool information."""
        return self._tools.get(name)
    
    def list_tools(self, category: Optional[ToolCategory] = None) -> list[Tool]:
        """List all tools, optionally filtered by category."""
        if category:
            return [t for t in self._tools.values() if t.category == category]
        return list(self._tools.values())
    
    def unregister(self, name: str):
        """Unregister a tool."""
        if name in self._tools:
            del self._tools[name]
            logger.debug(f"Unregistered tool: {name}")
    
    def get_tool_summaries(self) -> dict[str, str]:
        """Get summaries of all tools for prompt injection."""
        return {name: f"{t.name}: {t.description}" for name, t in self._tools.items()}
