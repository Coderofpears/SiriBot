"""SiriBot Orchestrator - coordinates all agents and components."""
import logging
from typing import Optional
from core.config import ConfigManager
from core.model_manager import ModelManager
from core.logger import logger
from agents.conversation_agent import ConversationAgent
from agents.reasoning_agent import ReasoningAgent
from agents.tool_agent import ToolAgent, SafetyManager
from agents.memory_agent import MemoryAgent
from tools.registry import ToolRegistry
from tools.basic.shell_tool import get_shell_tool
from tools.basic.file_tool import get_file_tools
from tools.basic.app_tool import get_app_tools

logger = logger


class SiriBot:
    """Main SiriBot orchestrator."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get()
        
        logger.info("Initializing SiriBot...")
        
        # Initialize model manager
        self.model_manager = ModelManager(self.config)
        
        # Initialize tool registry
        self.tool_registry = ToolRegistry()
        self._register_tools()
        
        # Initialize safety manager
        self.safety_manager = SafetyManager(self.config)
        
        # Initialize agents
        self.memory_agent = MemoryAgent(self.config)
        self.reasoning_agent = ReasoningAgent(self.model_manager)
        self.tool_agent = ToolAgent(self.tool_registry, self.safety_manager)
        
        self.conversation_agent = ConversationAgent(
            self.model_manager,
            self.memory_agent,
            self.tool_agent,
            self.reasoning_agent
        )
        
        logger.info("SiriBot initialized successfully")
    
    def _register_tools(self):
        """Register all available tools."""
        # Shell tool
        self.tool_registry.register(get_shell_tool())
        
        # File tools
        for tool in get_file_tools():
            self.tool_registry.register(tool)
        
        # App tools
        for tool in get_app_tools():
            self.tool_registry.register(tool)
        
        logger.info(f"Registered {len(self.tool_registry.list_tools())} tools")
    
    async def chat(self, message: str) -> str:
        """Process a chat message and return response."""
        return await self.conversation_agent.chat(message)
    
    async def chat_stream(self, message: str):
        """Process a chat message with streaming response."""
        async for chunk in self.conversation_agent.chat_stream(message):
            yield chunk
    
    def get_available_tools(self) -> dict[str, str]:
        """Get all available tools."""
        return self.tool_registry.get_tool_summaries()
    
    def get_conversation_history(self, limit: int = 50):
        """Get conversation history."""
        return self.conversation_agent.get_history(limit)
    
    async def get_memory_stats(self) -> dict:
        """Get memory statistics."""
        return await self.memory_agent.get_stats()
    
    def switch_model(self, provider: str):
        """Switch the model provider."""
        self.model_manager.switch_provider(provider)
        logger.info(f"Switched to {provider}")
    
    def reload_config(self):
        """Reload configuration from file."""
        self.config_manager._load()
        self.config = self.config_manager.get()
        logger.info("Configuration reloaded")
