"""Plugin marketplace for extending SiriBot functionality."""

import asyncio
import logging
import json
import subprocess
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)


class PluginState(Enum):
    INSTALLED = "installed"
    AVAILABLE = "available"
    UPDATE_AVAILABLE = "update_available"
    DISABLED = "disabled"


@dataclass
class PluginManifest:
    """Plugin metadata."""

    id: str
    name: str
    version: str
    description: str
    author: str
    category: str
    icon: Optional[str] = None
    requirements: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    min_siribot_version: str = "1.0.0"
    repo_url: Optional[str] = None


@dataclass
class Plugin:
    """A loaded plugin."""

    manifest: PluginManifest
    state: PluginState = PluginState.INSTALLED
    enabled: bool = True
    module: Optional[Any] = None
    init_fn: Optional[Callable] = None
    shutdown_fn: Optional[Callable] = None


class PluginMarketplace:
    """Marketplace for plugin discovery and management."""

    MARKETPLACE_URL = "https://siribot.plugins.example.com/api/v1"
    PLUGIN_DIR = Path.home() / ".siribot" / "plugins"

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.plugins: Dict[str, Plugin] = {}
        self._hooks: Dict[str, List[callable]] = {
            "pre_init": [],
            "post_init": [],
            "pre_shutdown": [],
            "post_shutdown": [],
            "chat_hook": [],
            "tool_register": [],
        }
        self._ensure_plugin_dir()
        logger.info("PluginMarketplace initialized")

    def _ensure_plugin_dir(self):
        """Ensure plugin directory exists."""
        self.PLUGIN_DIR.mkdir(parents=True, exist_ok=True)

    def register_plugin(
        self,
        manifest: PluginManifest,
        init_fn: Optional[Callable] = None,
        shutdown_fn: Optional[Callable] = None,
    ):
        """Register a local plugin."""
        plugin = Plugin(manifest=manifest, init_fn=init_fn, shutdown_fn=shutdown_fn)
        self.plugins[manifest.id] = plugin
        logger.info(f"Registered plugin: {manifest.name}")

    def unregister_plugin(self, plugin_id: str):
        """Unregister a plugin."""
        if plugin_id in self.plugins:
            del self.plugins[plugin_id]
            logger.info(f"Unregistered plugin: {plugin_id}")

    def enable_plugin(self, plugin_id: str) -> bool:
        """Enable a plugin."""
        plugin = self.plugins.get(plugin_id)
        if plugin:
            plugin.enabled = True
            logger.info(f"Enabled plugin: {plugin_id}")
            return True
        return False

    def disable_plugin(self, plugin_id: str) -> bool:
        """Disable a plugin."""
        plugin = self.plugins.get(plugin_id)
        if plugin:
            plugin.enabled = False
            logger.info(f"Disabled plugin: {plugin_id}")
            return True
        return False

    async def install_plugin(self, manifest: PluginManifest, source: str) -> bool:
        """Install a plugin from source."""
        try:
            plugin_path = self.PLUGIN_DIR / manifest.id
            plugin_path.mkdir(exist_ok=True)

            manifest_path = plugin_path / "manifest.json"
            with open(manifest_path, "w") as f:
                json.dump(
                    {
                        "id": manifest.id,
                        "name": manifest.name,
                        "version": manifest.version,
                        "description": manifest.description,
                        "author": manifest.author,
                        "category": manifest.category,
                        "requirements": manifest.requirements,
                        "permissions": manifest.permissions,
                    },
                    f,
                    indent=2,
                )

            if manifest.requirements:
                subprocess.run(
                    ["pip", "install"] + manifest.requirements, capture_output=True
                )

            self.register_plugin(manifest)
            logger.info(f"Installed plugin: {manifest.name}")
            return True

        except Exception as e:
            logger.error(f"Plugin install failed: {e}")
            return False

    async def uninstall_plugin(self, plugin_id: str) -> bool:
        """Uninstall a plugin."""
        plugin = self.plugins.get(plugin_id)
        if not plugin:
            return False

        try:
            plugin_path = self.PLUGIN_DIR / plugin_id
            if plugin_path.exists():
                import shutil

                shutil.rmtree(plugin_path)

            self.unregister_plugin(plugin_id)
            logger.info(f"Uninstalled plugin: {plugin_id}")
            return True

        except Exception as e:
            logger.error(f"Plugin uninstall failed: {e}")
            return False

    async def browse_marketplace(
        self, category: Optional[str] = None, search: Optional[str] = None
    ) -> List[PluginManifest]:
        """Browse available plugins."""
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                params = {}
                if category:
                    params["category"] = category
                if search:
                    params["q"] = search

                async with session.get(
                    f"{self.MARKETPLACE_URL}/plugins",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return [PluginManifest(**p) for p in data.get("plugins", [])]
                    return []
        except Exception as e:
            logger.error(f"Marketplace browse failed: {e}")
            return []

    def register_hook(self, hook_name: str, callback: callable):
        """Register a plugin hook."""
        if hook_name in self._hooks:
            self._hooks[hook_name].append(callback)

    async def trigger_hook(self, hook_name: str, *args, **kwargs):
        """Trigger a plugin hook."""
        if hook_name not in self._hooks:
            return

        for callback in self._hooks[hook_name]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(*args, **kwargs)
                else:
                    callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"Hook {hook_name} error: {e}")

    def get_plugin_tools(self) -> List[Dict[str, Any]]:
        """Get tools from all plugins."""
        tools = []
        for plugin in self.plugins.values():
            if plugin.enabled and plugin.module:
                if hasattr(plugin.module, "get_tools"):
                    tools.extend(plugin.module.get_tools())
        return tools

    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all plugins."""
        return [
            {
                "id": p.manifest.id,
                "name": p.manifest.name,
                "version": p.manifest.version,
                "category": p.manifest.category,
                "enabled": p.enabled,
                "state": p.state.value,
            }
            for p in self.plugins.values()
        ]


EXAMPLE_PLUGINS = [
    PluginManifest(
        id="code-helper",
        name="Code Helper",
        version="1.0.0",
        description="Advanced code analysis and suggestions",
        author="SiriBot",
        category="development",
        requirements=["black", "flake8"],
        permissions=["file_read", "shell"],
    ),
    PluginManifest(
        id="web-search",
        name="Web Search",
        version="1.0.0",
        description="Search the web for information",
        author="SiriBot",
        category="utilities",
        requirements=["beautifulsoup4"],
        permissions=["network"],
    ),
    PluginManifest(
        id="image-processor",
        name="Image Processor",
        version="1.0.0",
        description="Process and manipulate images",
        author="SiriBot",
        category="media",
        requirements=["Pillow"],
        permissions=["file_read", "file_write"],
    ),
]


def get_marketplace(config: Optional[Dict] = None) -> PluginMarketplace:
    """Get marketplace instance."""
    return PluginMarketplace(config)
