"""Memory agent - handles persistence and context memory."""

import logging
import json
import sqlite3
from pathlib import Path
from typing import Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
from .conversation_agent import Message

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """A memory entry."""

    id: Optional[int] = None
    key: str = ""
    value: Any = ""
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)


class MemoryAgent:
    """Manages memory and context storage."""

    def __init__(self, config):
        self.config = config
        self.db_path = config.memory.db_path
        self.short_term_memory: list[Message] = []
        self.long_term_memory: list[MemoryEntry] = []
        self._init_db()

    def _init_db(self):
        """Initialize the database."""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                metadata TEXT,
                created_at TEXT,
                accessed_at TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_input TEXT,
                response TEXT,
                intent TEXT,
                timestamp TEXT
            )
        """)

        conn.commit()
        conn.close()

        logger.info(f"Memory database initialized at {self.db_path}")

    async def add_interaction(self, user_input: str, response: str, intent: str):
        """Add a conversation interaction to memory."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO interactions (user_input, response, intent, timestamp) VALUES (?, ?, ?, ?)",
                (user_input, response, intent, datetime.now().isoformat()),
            )

            conn.commit()
            conn.close()

            self.short_term_memory.append(Message(role="user", content=user_input))
            self.short_term_memory.append(Message(role="assistant", content=response))

            if len(self.short_term_memory) > 100:
                self.short_term_memory = self.short_term_memory[-100:]
        except Exception as e:
            logger.error(f"Failed to add interaction: {e}")

    async def store(self, key: str, value: Any, metadata: dict = None):
        """Store a value in long-term memory."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()

            cursor.execute(
                "INSERT OR REPLACE INTO memory (key, value, metadata, created_at, accessed_at) VALUES (?, ?, ?, ?, ?)",
                (
                    key,
                    json.dumps(value),
                    json.dumps(metadata or {}),
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                ),
            )

            conn.commit()
            conn.close()

            logger.debug(f"Stored in memory: {key}")
        except Exception as e:
            logger.error(f"Memory store failed: {e}")

    async def recall(self, key: str) -> Optional[Any]:
        """Recall a value from long-term memory."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()

            cursor.execute("SELECT value FROM memory WHERE key = ?", (key,))
            row = cursor.fetchone()

            if row:
                cursor.execute(
                    "UPDATE memory SET accessed_at = ? WHERE key = ?",
                    (datetime.now().isoformat(), key),
                )
                conn.commit()
                conn.close()
                return json.loads(row[0])

            conn.close()
        except Exception as e:
            logger.error(f"Memory recall failed: {e}")
        return None

    async def search(self, query: str, limit: int = 10) -> list[dict]:
        """Search memory for relevant entries."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM interactions WHERE user_input LIKE ? OR response LIKE ? ORDER BY timestamp DESC LIMIT ?",
                (f"%{query}%", f"%{query}%", limit),
            )

            rows = cursor.fetchall()
            conn.close()

            return [
                {
                    "id": r[0],
                    "user_input": r[1],
                    "response": r[2],
                    "intent": r[3],
                    "timestamp": r[4],
                }
                for r in rows
            ]
        except Exception as e:
            logger.error(f"Memory search failed: {e}")
            return []

    def get_recent_context(self, limit: int = 20) -> list[Message]:
        """Get recent conversation context."""
        return self.short_term_memory[-limit:]

    async def get_stats(self) -> dict:
        """Get memory statistics."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM memory")
            memory_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM interactions")
            interaction_count = cursor.fetchone()[0]

            conn.close()

            return {
                "memory_entries": memory_count,
                "interactions": interaction_count,
                "short_term_size": len(self.short_term_memory),
            }
        except Exception as e:
            logger.error(f"Memory stats failed: {e}")
            return {
                "memory_entries": 0,
                "interactions": 0,
                "short_term_size": len(self.short_term_memory),
            }
