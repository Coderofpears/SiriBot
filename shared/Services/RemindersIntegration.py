"""Reminders integration service for macOS."""

import logging
import subprocess
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class Reminder:
    def __init__(
        self,
        title: str,
        due_date: Optional[datetime] = None,
        priority: int = 0,
        notes: str = "",
    ):
        self.title = title
        self.due_date = due_date
        self.priority = priority
        self.notes = notes
        self.completed = False

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "priority": self.priority,
            "notes": self.notes,
            "completed": self.completed,
        }


class RemindersIntegration:
    """Integrate with macOS Reminders app."""

    def __init__(self):
        self.list_name = "Reminders"
        logger.info("RemindersIntegration initialized")

    def _run_script(self, script: str) -> str:
        """Run AppleScript command."""
        try:
            cmd = f"osascript -e 'tell application \"Reminders\" to {script}'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout.strip()
        except Exception as e:
            logger.error(f"Reminders script failed: {e}")
            return ""

    def list_reminders(self, completed: bool = False) -> List[Dict[str, Any]]:
        """List reminders."""
        reminders = []

        filter_str = "" if completed else "whose completed is false"
        script = f'{filter_str}name of every reminder of list "{self.list_name}" {filter_str}'

        try:
            result = self._run_script(script)
            if result:
                for title in result.split(", "):
                    reminders.append({"title": title.strip(), "completed": False})
        except Exception as e:
            logger.debug(f"No reminders or error: {e}")

        return reminders

    def create_reminder(
        self,
        title: str,
        due_date: Optional[datetime] = None,
        priority: int = 0,
        notes: str = "",
    ) -> bool:
        """Create a new reminder."""
        try:
            script = f'make new reminder at end of reminders of list "{self.list_name}" with properties {{name:"{title}"'

            if due_date:
                date_str = due_date.strftime("%m/%d/%Y %H:%M:%S")
                script += f', due date:date "{date_str}"'

            if priority > 0:
                script += f", priority:{priority}"

            if notes:
                script += f', body:"{notes}"'

            script += "}"

            self._run_script(script)
            logger.info(f"Created reminder: {title}")
            return True
        except Exception as e:
            logger.error(f"Failed to create reminder: {e}")
            return False

    def complete_reminder(self, title: str) -> bool:
        """Mark a reminder as complete."""
        try:
            script = f'set completed of (first reminder of list "{self.list_name}" whose name is "{title}") to true'
            self._run_script(script)

            logger.info(f"Completed reminder: {title}")
            return True
        except Exception as e:
            logger.error(f"Failed to complete reminder: {e}")
            return False

    def delete_reminder(self, title: str) -> bool:
        """Delete a reminder."""
        try:
            script = f'delete (first reminder of list "{self.list_name}" whose name is "{title}")'
            self._run_script(script)

            logger.info(f"Deleted reminder: {title}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete reminder: {e}")
            return False

    def get_due_today(self) -> List[Dict[str, Any]]:
        """Get reminders due today."""
        reminders = []
        today = datetime.now().strftime("%m/%d/%Y")

        script = f'reminders of list "{self.list_name}" whose due date contains date "{today}"'
        result = self._run_script(script)

        if result:
            reminders.append({"title": result, "due_today": True})

        return reminders

    def snooze_reminder(self, title: str, minutes: int = 60) -> bool:
        """Snooze a reminder."""
        try:
            from datetime import timedelta

            new_time = datetime.now() + timedelta(minutes=minutes)
            date_str = new_time.strftime("%m/%d/%Y %H:%M:%S")

            script = f'set due date of (first reminder of list "{self.list_name}" whose name is "{title}") to date "{date_str}"'
            self._run_script(script)

            logger.info(f"Snoozed reminder: {title} for {minutes} minutes")
            return True
        except Exception as e:
            logger.error(f"Failed to snooze reminder: {e}")
            return False

    def get_overdue(self) -> List[Dict[str, Any]]:
        """Get overdue reminders."""
        reminders = []

        script = f'reminders of list "{self.list_name}" whose completed is false and due date < (current date)'
        result = self._run_script(script)

        if result:
            reminders.append({"title": result, "overdue": True})

        return reminders


def get_reminders_integration() -> RemindersIntegration:
    """Get reminders integration instance."""
    return RemindersIntegration()
