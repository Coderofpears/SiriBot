"""Multi-device synchronization service."""

import asyncio
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)


class SyncState:
    PENDING = "pending"
    SYNCED = "synced"
    CONFLICT = "conflict"


class SyncEntry:
    def __init__(
        self, key: str, value: Any, device_id: str, timestamp: float, checksum: str
    ):
        self.key = key
        self.value = value
        self.device_id = device_id
        self.timestamp = timestamp
        self.checksum = checksum
        self.state = SyncState.PENDING


class MultiDeviceSync:
    """Synchronize data across multiple devices."""

def __init__(self, config, device_id: Optional[str] = None):
        self.config = config
        self.device_id = device_id or self._generate_device_id()
        self.sync_interval = 30
        self.enabled = getattr(config, 'sync_enabled', False)
        sync_config = getattr(config, 'sync', {}) or {}
        if isinstance(sync_config, dict):
            self.cloud_endpoint = sync_config.get("endpoint", "http://localhost:8080")
            self.sync_interval = sync_config.get("interval", 30)
        else:
            self.cloud_endpoint = "http://localhost:8080"
        self._sync_queue: List[SyncEntry] = []
        self._local_cache: Dict[str, Any] = {}
        self._sync_task: Optional[asyncio.Task] = None
        self._listeners: List[callable] = []
        logger.info(f"MultiDeviceSync initialized for device: {self.device_id}")

    def _generate_device_id(self) -> str:
        import uuid

        return str(uuid.uuid4())[:8]

    def _compute_checksum(self, data: Any) -> str:
        return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()

    async def start(self):
        """Start the sync service."""
        if not self.enabled:
            logger.info("Sync disabled, skipping start")
            return

        self._sync_task = asyncio.create_task(self._sync_loop())
        logger.info("Sync service started")

    async def stop(self):
        """Stop the sync service."""
        if self._sync_task:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass
        logger.info("Sync service stopped")

    async def _sync_loop(self):
        """Background sync loop."""
        while True:
            try:
                await asyncio.sleep(self.sync_interval)
                await self.sync()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Sync error: {e}")

    async def sync(self) -> bool:
        """Perform synchronization."""
        if not self.enabled:
            return False

        try:
            remote_data = await self._fetch_remote()
            local_changes = self._get_pending_changes()

            merged = self._merge_data(remote_data, local_changes)
            await self._push_changes(merged)
            await self._notify_listeners()

            logger.info("Sync completed successfully")
            return True
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            return False

    async def _fetch_remote(self) -> Dict[str, Any]:
        """Fetch data from remote."""
        import aiohttp

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.cloud_endpoint}/sync/{self.device_id}",
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    return {}
        except Exception:
            return {}

    async def _push_changes(self, data: Dict[str, Any]) -> bool:
        """Push changes to remote."""
        import aiohttp

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.cloud_endpoint}/sync/{self.device_id}",
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    return resp.status == 200
        except Exception as e:
            logger.error(f"Push failed: {e}")
            return False

    def _merge_data(self, remote: Dict, local: List[SyncEntry]) -> Dict[str, Any]:
        """Merge remote and local data."""
        merged = remote.copy()

        for entry in local:
            if entry.state == SyncState.PENDING:
                merged[entry.key] = {
                    "value": entry.value,
                    "device_id": entry.device_id,
                    "timestamp": entry.timestamp,
                    "checksum": entry.checksum,
                }
                entry.state = SyncState.SYNCED

        return merged

    def _get_pending_changes(self) -> List[SyncEntry]:
        """Get pending local changes."""
        return [e for e in self._sync_queue if e.state == SyncState.PENDING]

    def push(self, key: str, value: Any):
        """Queue a value for sync."""
        entry = SyncEntry(
            key=key,
            value=value,
            device_id=self.device_id,
            timestamp=datetime.now().timestamp(),
            checksum=self._compute_checksum(value),
        )
        self._sync_queue.append(entry)
        self._local_cache[key] = value
        logger.debug(f"Queued for sync: {key}")

    def pull(self, key: str, default: Any = None) -> Any:
        """Get value from local cache."""
        return self._local_cache.get(key, default)

    def register_listener(self, callback: callable):
        """Register a sync listener."""
        self._listeners.append(callback)

    async def _notify_listeners(self):
        """Notify all listeners of sync completion."""
        for listener in self._listeners:
            try:
                await listener(self._local_cache)
            except Exception as e:
                logger.error(f"Listener error: {e}")

    def get_device_id(self) -> str:
        """Get this device's ID."""
        return self.device_id

    def get_status(self) -> Dict[str, Any]:
        """Get sync status."""
        return {
            "device_id": self.device_id,
            "enabled": self.enabled,
            "pending_changes": len(self._get_pending_changes()),
            "cached_entries": len(self._local_cache),
            "sync_interval": self.sync_interval,
        }


def get_sync_service(config, device_id: Optional[str] = None) -> MultiDeviceSync:
    """Get sync service instance."""
    return MultiDeviceSync(config, device_id)
