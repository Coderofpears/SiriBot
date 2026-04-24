"""Calendar integration service for macOS."""

import logging
import subprocess
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CalendarEvent:
    def __init__(
        self,
        title: str,
        start: datetime,
        end: datetime,
        location: str = "",
        notes: str = "",
    ):
        self.title = title
        self.start = start
        self.end = end
        self.location = location
        self.notes = notes

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "location": self.location,
            "notes": self.notes,
        }


class CalendarIntegration:
    """Integrate with macOS Calendar app."""

    CALENDAR_CMD = "osascript -e 'tell application \"Calendar\" to {script}'"

    def __init__(self):
        self.calendar_name = "Home"
        logger.info("CalendarIntegration initialized")

    def _run_script(self, script: str) -> str:
        """Run AppleScript command."""
        try:
            cmd = f"osascript -e 'tell application \"Calendar\" to {script}'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout.strip()
        except Exception as e:
            logger.error(f"Calendar script failed: {e}")
            return ""

    def list_events(self, days: int = 7) -> List[Dict[str, Any]]:
        """List upcoming events."""
        events = []
        today = datetime.now()

        script = f'''get events of calendar "{self.calendar_name}" whose date of start >= (current date)'''
        result = self._run_script(script)

        if result:
            events.append(
                {
                    "title": result,
                    "start": today.isoformat(),
                    "end": (today + timedelta(hours=1)).isoformat(),
                }
            )

        return events

    def create_event(
        self,
        title: str,
        start: datetime,
        duration_minutes: int = 60,
        location: str = "",
        notes: str = "",
    ) -> bool:
        """Create a new calendar event."""
        try:
            start_str = start.strftime("%m/%d/%Y %H:%M")
            end_str = (start + timedelta(minutes=duration_minutes)).strftime(
                "%m/%d/%Y %H:%M"
            )

            script = f'''make new event at end of events of calendar "{self.calendar_name}" with properties {{summary:"{title}", start date:date "{start_str}", end date:date "{end_str}"'''
            if location:
                script += f', location:"{location}"'
            if notes:
                script += f', description:"{notes}"'
            script += "}"

            self._run_script(script)
            logger.info(f"Created event: {title}")
            return True
        except Exception as e:
            logger.error(f"Failed to create event: {e}")
            return False

    def delete_event(self, title: str, date: Optional[datetime] = None) -> bool:
        """Delete a calendar event."""
        try:
            if date:
                script = f'''delete (first event of calendar "{self.calendar_name}" whose summary is "{title}" and start date >= date "{date.strftime("%m/%d/%Y")}")'''
            else:
                script = f'''delete (first event of calendar "{self.calendar_name}" whose summary is "{title}")'''

            self._run_script(script)
            logger.info(f"Deleted event: {title}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete event: {e}")
            return False

    def get_today_events(self) -> List[Dict[str, Any]]:
        """Get today's events."""
        return self.list_events(days=1)

    def get_upcoming_events(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get events in the next N hours."""
        events = []
        now = datetime.now()
        end_time = now + timedelta(hours=hours)

        script = f'''get events of calendar "{self.calendar_name}" whose start date >= (current date) and start date <= (current date + ({hours} * hours))'''
        result = self._run_script(script)

        if result:
            events.append(
                {"title": result, "start": now.isoformat(), "end": end_time.isoformat()}
            )

        return events


def get_calendar_integration() -> CalendarIntegration:
    """Get calendar integration instance."""
    return CalendarIntegration()
