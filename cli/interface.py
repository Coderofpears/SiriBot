"""Interactive SiriBot interface."""

import asyncio
import sys
from typing import Optional
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.live import Live
from rich.style import Style
from core.logger import logger
from orchestrator import SiriBot


console = Console()


RAINBOW_STYLES = [
    "red",
    "orange1",
    "yellow1",
    "green1",
    "cyan1",
    "blue1",
    "magenta1",
]


class SiriBotInterface:
    """Interactive SiriBot interface."""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.bot: Optional[SiriBot] = None
        self.voice_mode = False
        self.running = False

    async def _init_bot(self):
        """Initialize the bot."""
        if not self.bot:
            self.bot = SiriBot(self.config_path)

    async def run(self):
        """Run the interactive interface."""
        await self._init_bot()
        self.running = True

        self._print_welcome()

        while self.running:
            try:
                user_input = await self._get_input()

                if not user_input:
                    continue

                if user_input.lower() in ["exit", "quit", "bye"]:
                    self.running = False
                    console.print("\n[dim]Goodbye![/dim]")
                    break

                if user_input.lower() == "/voice":
                    self.voice_mode = not self.voice_mode
                    mode = "enabled" if self.voice_mode else "disabled"
                    console.print(f"[dim]Voice mode {mode}[/dim]")
                    continue

                if user_input.lower() == "/clear":
                    console.clear()
                    self._print_welcome()
                    continue

                if user_input.lower() == "/tools":
                    await self._list_tools()
                    continue

                if user_input.lower() == "/stats":
                    await self._show_stats()
                    continue

                await self._process_message(user_input)

            except KeyboardInterrupt:
                self.running = False
                console.print("\n[dim]Goodbye![/dim]")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                console.print(f"[red]Error: {e}[/red]")

    def _print_welcome(self):
        """Print welcome message."""
        welcome = """# 🤖 SiriBot

Welcome! I'm your local AI assistant. 

**Commands:**
- `/voice` - Toggle voice mode
- `/tools` - List available tools
- `/stats` - Show memory stats
- `/clear` - Clear screen
- `exit` - Quit

"""
        console.print(
            Panel.fit(Markdown(welcome), title="SiriBot", border_style="cyan")
        )

    async def _get_input(self) -> str:
        """Get user input."""
        if self.voice_mode:
            console.print("[dim]Listening... (Ctrl+C to type)[/dim]")
            # Voice input would go here
            await asyncio.sleep(1)
            return Prompt.ask("\n[cyan]You[/cyan]")
        else:
            return await asyncio.get_event_loop().run_in_executor(
                None, lambda: Prompt.ask("\n[cyan]You[/cyan]")
            )

async def _process_message(self, message: str):
        """Process a user message."""
        console.print("[dim]Thinking...[/dim]", end="\r")
        
        try:
            response = await asyncio.wait_for(
                self.bot.chat(message),
                timeout=120
            )
            console.print("\r" + " " * 50 + "\r")
            
            if response:
                response_text = self._get_rainbow_response(response)
                console.print(Panel.fit(
                    Markdown(response_text),
                    title="[bold cyan]SiriBot[/bold cyan]",
                    border_style="green"
                ))
            else:
                console.print("[yellow]No response received[/yellow]")
        except asyncio.TimeoutError:
            console.print("\r[red]Request timed out. Please try again.[/red]")
        except Exception as e:
            console.print(f"\r[red]Error: {e}[/red]")
    
    def _get_rainbow_response(self, response: str) -> str:
        """Convert response to rainbow colors line by line."""
        lines = response.split("\n")
        result = []
        for i, line in enumerate(lines):
            style = RAINBOW_STYLES[i % len(RAINBOW_STYLES)]
            if line.startswith("#"):
                result.append(f"[bold {style}]{line}[/bold {style}]")
            elif line.startswith("-"):
                result.append(f"[{style}]{line}[/{style}]")
            elif line.startswith("**"):
                result.append(f"[bold {style}]{line}[/bold {style}]")
            else:
                result.append(f"[{style}]{line}[/{style}]" if line.strip() else line)
        return "\n".join(result)

async def _list_tools(self):
        """List available tools."""
        tools = self.bot.get_available_tools()
        
        console.print("\n[bold cyan]Available Tools:[/bold cyan]\n")
        for i, (name, desc) in enumerate(tools.items()):
            style = RAINBOW_STYLES[i % len(RAINBOW_STYLES)]
            console.print(f"  [{style}]{name}[/{style}]: {desc}")
        console.print()
    
    async def _show_stats(self):
        """Show memory statistics."""
        stats = await self.bot.get_memory_stats()
        
        stats_text = self._get_rainbow_response(f"""**Memory Stats:**
- Memory entries: {stats['memory_entries']}
- Interactions: {stats['interactions']}
- Short-term size: {stats['short_term_size']}""")
        
        console.print(Panel.fit(
            Markdown(stats_text),
            title="[bold cyan]Statistics[/bold cyan]",
            border_style="yellow"
        ))
