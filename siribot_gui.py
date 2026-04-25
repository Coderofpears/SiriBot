"""Cross-platform SiriBot UI using Tkinter."""

import tkinter as tk
from tkinter import ttk, scrolledtext
import asyncio
import threading
import queue
from pathlib import Path


class SiriBotUI:
    """Cross-platform GUI for SiriBot."""

    PLATFORM_COLORS = {
        "macos": {
            "bg": "#1e1e1e",
            "fg": "#ffffff",
            "accent": "#007AFF",
            "border": "#333333",
        },
        "windows": {
            "bg": "#1e1e1e",
            "fg": "#ffffff",
            "accent": "#0078D4",
            "border": "#333333",
        },
        "linux": {
            "bg": "#1e1e1e",
            "fg": "#ffffff",
            "accent": "#E95420",
            "border": "#333333",
        },
    }

    def __init__(self, platform="auto"):
        self.root = tk.Tk()
        self.root.title("SiriBot")
        self.root.geometry("600x450")
        self.root.minsize(400, 300)

        self.platform = self._detect_platform(platform)
        self.colors = self.PLATFORM_COLORS.get(
            self.platform, self.PLATFORM_COLORS["macos"]
        )
        self.bot = None
        self.response_queue = queue.Queue()

        self._setup_style()
        self._create_widgets()
        self._start_async_loop()

    def _detect_platform(self, platform):
        """Detect the current platform."""
        if platform != "auto":
            return platform

        import sys

        if sys.platform == "darwin":
            return "macos"
        elif sys.platform == "win32":
            return "windows"
        else:
            return "linux"

    def _setup_style(self):
        """Configure ttk styles."""
        style = ttk.Style()
        style.theme_use("clam")

        self.root.configure(bg=self.colors["bg"])

        style.configure("TFrame", background=self.colors["bg"])
        style.configure(
            "TLabel", background=self.colors["bg"], foreground=self.colors["fg"]
        )
        style.configure(
            "TButton",
            background=self.colors["accent"],
            foreground="white",
            borderwidth=0,
            focuscolor="none",
        )
        style.map("TButton", background=[("active", self.colors["accent"])])

    def _create_widgets(self):
        """Create UI widgets."""
        # Header
        header = tk.Frame(self.root, bg=self.colors["bg"], height=50)
        header.pack(fill=tk.X, padx=10, pady=5)

        title = tk.Label(
            header,
            text="🤖 SiriBot",
            font=("SF Pro", 18, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["fg"],
        )
        title.pack(side=tk.LEFT)

        # Platform badge
        platform_badge = tk.Label(
            header,
            text=self.platform.upper(),
            font=("SF Pro", 9),
            bg=self.colors["accent"],
            fg="white",
            padx=8,
            pady=2,
        )
        platform_badge.pack(side=tk.RIGHT)

        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            self.root,
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("SF Pro", 11),
            insertbackground=self.colors["fg"],
            relief=tk.FLAT,
            state=tk.DISABLED,
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Configure text tags
        self.chat_display.tag_config("user", foreground="#8E8E93")
        self.chat_display.tag_config("bot", foreground=self.colors["fg"])
        self.chat_display.tag_config("error", foreground="#FF3B30")

        # Input area
        input_frame = tk.Frame(self.root, bg=self.colors["bg"])
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        self.input_field = tk.Entry(
            input_frame,
            bg="#2C2C2E",
            fg=self.colors["fg"],
            font=("SF Pro", 12),
            relief=tk.FLAT,
            insertbackground=self.colors["fg"],
        )
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_field.bind("<Return>", self._send_message)

        send_btn = tk.Button(
            input_frame,
            text="Send",
            command=self._send_message,
            bg=self.colors["accent"],
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=5,
        )
        send_btn.pack(side=tk.RIGHT, padx=(10, 0))

        # Status bar
        self.status = tk.Label(
            self.root,
            text="● Ready",
            font=("SF Pro", 9),
            bg=self.colors["bg"],
            fg="#30D158",
        )
        self.status.pack(side=tk.BOTTOM, anchor=tk.W, padx=10, pady=2)

        # Initial message
        self._append_message("bot", f"🤖 SiriBot v1.0.0-beta.1 ({self.platform})")
        self._append_message("bot", "Hello! How can I help you today?")

    def _start_async_loop(self):
        """Start the asyncio event loop in a separate thread."""

        def run_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_forever()

        self.loop_thread = threading.Thread(target=run_loop, daemon=True)
        self.loop_thread.start()

    def _send_message(self, event=None):
        """Handle send button or Enter key."""
        message = self.input_field.get().strip()
        if not message:
            return

        self.input_field.delete(0, tk.END)
        self._append_message("user", f"You: {message}")
        self._update_status("● Thinking...")

        # Process in background
        def process():
            try:
                from orchestrator import SiriBot

                if not self.bot:
                    self.bot = SiriBot()

                loop = asyncio.get_event_loop()
                response = loop.run_until_complete(self.bot.chat(message))
                self.response_queue.put(("success", response))
            except Exception as e:
                self.response_queue.put(("error", str(e)))

        threading.Thread(target=process, daemon=True).start()
        self.root.after(100, self._check_response)

    def _check_response(self):
        """Check for responses in queue."""
        try:
            while True:
                result_type, content = self.response_queue.get_nowait()
                if result_type == "success":
                    self._append_message("bot", f"🤖 {content}")
                    self._update_status("● Ready")
                else:
                    self._append_message("error", f"Error: {content}")
                    self._update_status("● Error")
        except queue.Empty:
            self.root.after(100, self._check_response)

    def _append_message(self, tag, message):
        """Append a message to the chat display."""
        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.insert(tk.END, message + "\n\n", tag)
        self.chat_display.see(tk.END)
        self.chat_display.configure(state=tk.DISABLED)

    def _update_status(self, text):
        """Update status bar."""
        self.status.configure(text=text)

    def run(self):
        """Start the UI."""
        self.root.mainloop()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="SiriBot UI")
    parser.add_argument(
        "--platform",
        default="auto",
        choices=["auto", "macos", "windows", "linux"],
        help="Platform to use",
    )
    args = parser.parse_args()

    app = SiriBotUI(platform=args.platform)
    app.run()


if __name__ == "__main__":
    main()
