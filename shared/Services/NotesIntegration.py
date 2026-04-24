"""Notes integration service for macOS."""

import logging
import subprocess
import json
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class Note:
    def __init__(self, title: str, content: str, folder: str = "Notes"):
        self.title = title
        self.content = content
        self.folder = folder
        self.modified = None

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "content": self.content,
            "folder": self.folder,
            "modified": self.modified,
        }


class NotesIntegration:
    """Integrate with macOS Notes app."""

    def __init__(self):
        self.account_name = "iCloud"
        self.folder_name = "Notes"
        logger.info("NotesIntegration initialized")

    def _run_script(self, script: str) -> str:
        """Run AppleScript command."""
        try:
            cmd = f"osascript -e 'tell application \"Notes\" to {script}'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout.strip()
        except Exception as e:
            logger.error(f"Notes script failed: {e}")
            return ""

    def list_notes(self, folder: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all notes."""
        notes = []
        target_folder = folder or self.folder_name

        script = f'name of every note of folder "{target_folder}"'
        result = self._run_script(script)

        if result:
            for title in result.split(", "):
                notes.append({"title": title.strip(), "folder": target_folder})

        return notes

    def get_note(
        self, title: str, folder: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get a specific note."""
        target_folder = folder or self.folder_name

        script = (
            f'body of (first note of folder "{target_folder}" whose name is "{title}")'
        )
        content = self._run_script(script)

        if content:
            return {"title": title, "content": content, "folder": target_folder}
        return None

    def create_note(
        self, title: str, content: str, folder: Optional[str] = None
    ) -> bool:
        """Create a new note."""
        try:
            target_folder = folder or self.folder_name

            script = f'''make new note at folder "{target_folder}" with properties {{name:"{title}", body:"{content}"}}'''
            self._run_script(script)

            logger.info(f"Created note: {title}")
            return True
        except Exception as e:
            logger.error(f"Failed to create note: {e}")
            return False

    def update_note(
        self, title: str, content: str, folder: Optional[str] = None
    ) -> bool:
        """Update an existing note."""
        try:
            target_folder = folder or self.folder_name

            script = f'set body of (first note of folder "{target_folder}" whose name is "{title}") to "{content}"'
            self._run_script(script)

            logger.info(f"Updated note: {title}")
            return True
        except Exception as e:
            logger.error(f"Failed to update note: {e}")
            return False

    def delete_note(self, title: str, folder: Optional[str] = None) -> bool:
        """Delete a note."""
        try:
            target_folder = folder or self.folder_name

            script = f'delete (first note of folder "{target_folder}" whose name is "{title}")'
            self._run_script(script)

            logger.info(f"Deleted note: {title}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete note: {e}")
            return False

    def search_notes(self, query: str) -> List[Dict[str, Any]]:
        """Search notes by content."""
        results = []

        script = f'notes whose body contains "{query}"'
        result = self._run_script(script)

        if result:
            for note in result.split(", "):
                results.append({"title": note.strip()})

        return results

    def append_to_note(
        self, title: str, text: str, folder: Optional[str] = None
    ) -> bool:
        """Append text to an existing note."""
        try:
            note = self.get_note(title, folder)
            if note:
                new_content = note["content"] + "\n" + text
                return self.update_note(title, new_content, folder)
            return False
        except Exception as e:
            logger.error(f"Failed to append to note: {e}")
            return False


def get_notes_integration() -> NotesIntegration:
    """Get notes integration instance."""
    return NotesIntegration()
