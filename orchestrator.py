"""SiriBot Orchestrator - coordinates all agents and components."""

import asyncio
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

VERSION = "1.0.0"


class SiriBot:
    """Main SiriBot orchestrator."""

    def __init__(self, config_path: Optional[str] = None):
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get()

        logger.info("Initializing SiriBot...")

        self.model_manager = ModelManager(self.config)
        self.tool_registry = ToolRegistry()
        self._register_tools()

        self.safety_manager = SafetyManager(self.config)

        self.memory_agent = MemoryAgent(self.config)
        self.reasoning_agent = ReasoningAgent(self.model_manager)
        self.tool_agent = ToolAgent(self.tool_registry, self.safety_manager)

        self.conversation_agent = ConversationAgent(
            self.model_manager, self.memory_agent, self.tool_agent, self.reasoning_agent
        )

        self._init_advanced_services()

        logger.info("SiriBot initialized successfully")

    def _init_advanced_services(self):
        """Initialize advanced services."""
        try:
            from shared.Services.SyncService import get_sync_service

            self.sync_service = get_sync_service(self.config)
        except Exception as e:
            logger.warning(f"Sync service not available: {e}")
            self.sync_service = None

        try:
            from shared.Services.WorkflowEngine import WorkflowEngine

            self.workflow_engine = WorkflowEngine(self)
        except Exception as e:
            logger.warning(f"Workflow engine not available: {e}")
            self.workflow_engine = None

        try:
            from shared.Services.PluginMarketplace import get_marketplace

            self.plugin_marketplace = get_marketplace(self.config)
        except Exception as e:
            logger.warning(f"Plugin marketplace not available: {e}")
            self.plugin_marketplace = None

        try:
            from shared.Services.PersonalModelManager import get_model_manager

            self.model_manager_service = get_model_manager(self.config)
        except Exception as e:
            logger.warning(f"Model manager not available: {e}")
            self.model_manager_service = None

        try:
            from shared.Services.CalendarIntegration import get_calendar_integration

            self.calendar = get_calendar_integration()
        except Exception as e:
            logger.warning(f"Calendar integration not available: {e}")
            self.calendar = None

        try:
            from shared.Services.NotesIntegration import get_notes_integration

            self.notes = get_notes_integration()
        except Exception as e:
            logger.warning(f"Notes integration not available: {e}")
            self.notes = None

        try:
            from shared.Services.RemindersIntegration import get_reminders_integration

            self.reminders = get_reminders_integration()
        except Exception as e:
            logger.warning(f"Reminders integration not available: {e}")
            self.reminders = None

    def _register_tools(self):
        """Register all available tools."""
        self.tool_registry.register(get_shell_tool())

        for tool in get_file_tools():
            self.tool_registry.register(tool)

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

    async def execute_workflow(self, workflow_id: str, context: Optional[dict] = None) -> dict:
        """Execute an autonomous workflow."""
        if self.workflow_engine:
            return await self.workflow_engine.execute_workflow(workflow_id, context)
        return {"success": False, "error": "Workflow engine not available"}

    def list_workflows(self) -> list:
        """List all workflows."""
        if self.workflow_engine:
            return self.workflow_engine.list_workflows()
        return []

    def get_sync_status(self) -> dict:
        """Get sync status."""
        if self.sync_service:
            return self.sync_service.get_status()
        return {"enabled": False}

    def list_plugins(self) -> list:
        """List all plugins."""
        if self.plugin_marketplace:
            return self.plugin_marketplace.list_plugins()
        return []

    def list_models(self) -> list:
        """List all personal models."""
        if self.model_manager_service:
            return self.model_manager_service.list_models()
        return []

    def get_integrations(self) -> dict:
        """Get available integrations status."""
        return {
            "calendar": self.calendar is not None,
            "notes": self.notes is not None,
            "reminders": self.reminders is not None,
        }

    def get_version(self) -> str:
        """Get SiriBot version."""
        return VERSION

    def health_check(self) -> dict:
        """Perform health check on all services."""
        health = {"status": "healthy", "version": VERSION, "services": {}, "memory_entries": 0}

        # Check model availability
        health["services"]["model"] = self.model_manager.current_adapter is not None

        try:
            import threading

            loop = asyncio.get_event_loop()
            if loop.is_running():
                # In async context - create a task
                def check_in_thread():
                    inner_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(inner_loop)
                    try:
                        stats = inner_loop.run_until_complete(self.get_memory_stats())
                        health["services"]["memory"] = True
                        health["memory_entries"] = stats.get("memory_entries", 0)
                    except:
                        health["services"]["memory"] = False
                    finally:
                        inner_loop.close()

                thread = threading.Thread(target=check_in_thread, daemon=True)
                thread.start()
                thread.join(timeout=2)
            else:
                stats = loop.run_until_complete(self.get_memory_stats())
                health["services"]["memory"] = True
                health["memory_entries"] = stats.get("memory_entries", 0)
        except Exception:
            health["services"]["memory"] = False

        health["services"]["sync"] = self.sync_service is not None
        health["services"]["workflow"] = self.workflow_engine is not None
        health["services"]["plugins"] = self.plugin_marketplace is not None
        health["services"]["calendar"] = self.calendar is not None
        health["services"]["notes"] = self.notes is not None
        health["services"]["reminders"] = self.reminders is not None

        # Check critical services
        critical_services = ["model", "memory"]
        if not all(health["services"].get(s, False) for s in critical_services):
            health["status"] = "degraded"

        return health

    async def _health_check_memory(self, health: dict):
        """Async helper for memory health check."""
        try:
            stats = await self.get_memory_stats()
            health["services"]["memory"] = True
            health["services"]["memory_entries"] = stats.get("memory_entries", 0)
        except Exception:
            health["services"]["memory"] = False
            health["services"]["memory_entries"] = 0
