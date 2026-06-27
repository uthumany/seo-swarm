"""
SEO SWARM - Animated Terminal Spinner Engine

Context-manager spinners with success/fail markers and multi-spinner support
for parallel swarm operations. Uses ANSI escape codes for animation.
Zero external dependencies — pure stdlib.
"""

import sys
import time
import threading
from typing import Dict, Optional, List
from seo_swarm.tui.dashboard import COLORS

# ══════════════════════════════════════════════════════════════════════════════
# Spinner frame sequences
# ══════════════════════════════════════════════════════════════════════════════

SPINNER_FRAMES: Dict[str, List[str]] = {
    "dots": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
    "line": ["|", "/", "─", "\\"],
    "grow": ["▁", "▃", "▄", "▅", "▆", "▇", "▆", "▅", "▄", "▃"],
    "bounce": ["⠁", "⠂", "⠄", "⠂"],
    "arrow": ["←", "↖", "↑", "↗", "→", "↘", "↓", "↙"],
    "pulse": ["█", "▓", "▒", "░"],
    "moon": ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"],
    "clock": ["🕛", "🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚"],
    "braille": ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"],
    "simple": [".  ", ".. ", "...", " ..", "  .", "   "],
}
SPINNER_FRAMES["default"] = SPINNER_FRAMES["dots"]


# ══════════════════════════════════════════════════════════════════════════════
# Spinner
# ══════════════════════════════════════════════════════════════════════════════

class Spinner:
    """Context-manager spinner for long-running operations.

    Can be used as a context manager or manually with start()/stop().
    No threading required — call update() in a loop or let the
    context manager auto-animate.

    Example:
        with Spinner("Crawling pages...") as sp:
            result = do_work()
            if result.ok:
                sp.succeed("Crawled 150 pages")
            else:
                sp.fail("Crawl failed")

        # Manual loop mode:
        sp = Spinner("Processing...")
        sp.start()
        for item in items:
            process(item)
        sp.succeed("Done")
    """

    def __init__(
        self,
        message: str = "",
        style: str = "dots",
        color: str = "cyan",
        success_color: str = "bright_green",
        fail_color: str = "bright_red",
        interval: float = 0.1,
    ):
        """Initialize a Spinner.

        Args:
            message: Initial message to display next to the spinner.
            style: Spinner frame style (dots, line, grow, bounce, arrow, pulse, braille, simple).
            color: ANSI color name for the spinner and message.
            success_color: ANSI color name for the success marker (✓).
            fail_color: ANSI color name for the failure marker (✗).
            interval: Seconds between frame updates.
        """
        self.message = message
        self.style = style
        self.color = color
        self.success_color = success_color
        self.fail_color = fail_color
        self.interval = interval
        self._frames = SPINNER_FRAMES.get(style, SPINNER_FRAMES["dots"])
        self._frame_idx = 0
        self._active = False
        self._finished = False
        self._result: Optional[str] = None  # 'success' or 'fail'
        self._result_text: Optional[str] = None
        self._thread: Optional[threading.Thread] = None

    def __enter__(self) -> "Spinner":
        """Start the spinner when entering a context manager block."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop the spinner when exiting a context manager block.

        If an exception occurred, mark as failed; otherwise mark as success
        if not already marked.
        """
        if exc_type is not None:
            if not self._finished:
                self.fail(str(exc_val) if exc_val else "Error")
        else:
            if not self._finished:
                self.succeed()
        self.stop()
        return False  # Don't suppress exceptions

    def start(self):
        """Start the spinner animation. Non-blocking — returns immediately."""
        if self._active:
            return
        self._active = True
        self._finished = False
        self._result = None
        self._result_text = None
        self._frame_idx = 0
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the spinner animation and clear the line."""
        self._active = False
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None
        # Print final result line
        self._print_result()

    def succeed(self, text: Optional[str] = None):
        """Mark the spinner as successful.

        Args:
            text: Optional success message. If None, uses the current message.
        """
        self._finished = True
        self._result = "success"
        self._result_text = text

    def fail(self, text: Optional[str] = None):
        """Mark the spinner as failed.

        Args:
            text: Optional failure message. If None, uses the current message.
        """
        self._finished = True
        self._result = "fail"
        self._result_text = text

    def update(self, text: str):
        """Change the spinner message while it's running.

        Args:
            text: New message to display.
        """
        self.message = text

    def _animate(self):
        """Internal animation loop running in a daemon thread."""
        while self._active:
            if self._finished:
                break
            frame = self._frames[self._frame_idx % len(self._frames)]
            self._frame_idx += 1
            self._draw(frame)
            time.sleep(self.interval)
        self._active = False

    def _draw(self, frame: str):
        """Draw one frame of the spinner."""
        cc = COLORS.get(self.color, "")
        reset = COLORS["reset"]
        # Clear line (\r) and draw
        sys.stderr.write(f"\r{cc}{frame}{reset} {self.message}  ")
        sys.stderr.flush()

    def _print_result(self):
        """Print the final result line (success ✓ or fail ✗)."""
        reset = COLORS["reset"]
        text = self._result_text if self._result_text else self.message
        if self._result == "success":
            sc = COLORS.get(self.success_color, COLORS["bright_green"])
            sys.stderr.write(f"\r{sc}✓{reset} {text}  \n")
        elif self._result == "fail":
            fc = COLORS.get(self.fail_color, COLORS["bright_red"])
            sys.stderr.write(f"\r{fc}✗{reset} {text}  \n")
        else:
            # Stopped without explicit succeed/fail
            sys.stderr.write(f"\r  {text}  \n")
        sys.stderr.flush()


# ══════════════════════════════════════════════════════════════════════════════
# MultiSpinner
# ══════════════════════════════════════════════════════════════════════════════

class MultiSpinner:
    """Multiple concurrent spinners for swarm-mode parallel operations.

    Each spinner has a name and shows its own status line.
    Updates are rendered as a group, clearing previous output.

    Example:
        ms = MultiSpinner()
        ms.add("crawler", "Crawling pages...")
        ms.add("analyzer", "Analyzing content...")
        ms.add("reporter", "Generating report...")
        ms.render()

        # ... after some work ...

        ms.succeed("crawler", "Crawled 150 pages")
        ms.update("analyzer", "Analyzing meta tags...")
        ms.fail("reporter", "Report failed")
        ms.render()
    """

    def __init__(self, style: str = "dots", interval: float = 0.1):
        """Initialize a MultiSpinner.

        Args:
            style: Spinner frame style for active items.
            interval: Seconds between frame updates.
        """
        self.style = style
        self.interval = interval
        self._frames = SPINNER_FRAMES.get(style, SPINNER_FRAMES["dots"])
        self._items: Dict[str, Dict] = {}  # name -> {message, status, result_text}
        self._frame_idx = 0
        self._active = False
        self._thread: Optional[threading.Thread] = None
        self._order: List[str] = []  # Maintain insertion order

    def add(self, name: str, message: str):
        """Add a new spinner to the group.

        Args:
            name: Unique identifier for this spinner.
            message: Initial message to display.
        """
        if name not in self._items:
            self._order.append(name)
        self._items[name] = {
            "message": message,
            "status": "active",  # active, success, fail
            "result_text": None,
        }

    def update(self, name: str, message: str):
        """Update the message of an existing spinner.

        Args:
            name: The spinner to update.
            message: New message text.
        """
        if name in self._items:
            self._items[name]["message"] = message

    def succeed(self, name: str, text: Optional[str] = None):
        """Mark a spinner as successfully completed.

        Args:
            name: The spinner to mark.
            text: Optional success message override.
        """
        if name in self._items:
            self._items[name]["status"] = "success"
            self._items[name]["result_text"] = text

    def fail(self, name: str, text: Optional[str] = None):
        """Mark a spinner as failed.

        Args:
            name: The spinner to mark.
            text: Optional failure message override.
        """
        if name in self._items:
            self._items[name]["status"] = "fail"
            self._items[name]["result_text"] = text

    def start(self):
        """Start the auto-refresh animation thread."""
        if self._active:
            return
        self._active = True
        self._thread = threading.Thread(target=self._auto_refresh, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop auto-refresh and render final state."""
        self._active = False
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None
        self.render()

    def render(self) -> str:
        """Render the current state of all spinners and return the formatted string.

        Returns:
            A string containing the rendered multi-spinner view.
        """
        reset = COLORS["reset"]
        frame = self._frames[self._frame_idx % len(self._frames)]

        lines: List[str] = []
        for name in self._order:
            item = self._items.get(name, {"message": name, "status": "active"})
            status = item.get("status", "active")
            text = item.get("result_text") or item.get("message", name)

            if status == "active":
                cc = COLORS.get("cyan", "")
                line = f"  {cc}{frame}{reset} {text}"
            elif status == "success":
                sc = COLORS.get("bright_green", "")
                line = f"  {sc}✓{reset} {text}"
            elif status == "fail":
                fc = COLORS.get("bright_red", "")
                line = f"  {fc}✗{reset} {text}"
            else:
                line = f"    {text}"

            lines.append(line)

        return "\n".join(lines)

    def render_live(self):
        """Render the current state to stderr with cursor control.

        Moves cursor up to overwrite the previous render block.
        Call this repeatedly in a loop for live updates.
        """
        reset = COLORS["reset"]
        # Build output
        output = self.render()

        # Move cursor up to previous render position
        prev_lines = getattr(self, "_prev_line_count", 0)
        if prev_lines > 0:
            sys.stderr.write(f"\033[{prev_lines}A")  # Move up

        sys.stderr.write(output + "\n")
        sys.stderr.flush()

        # Track line count for next update
        self._prev_line_count = output.count("\n") + 1

    def _auto_refresh(self):
        """Internal auto-refresh loop."""
        while self._active:
            self._frame_idx += 1
            self.render_live()
            time.sleep(self.interval)


# ══════════════════════════════════════════════════════════════════════════════
# Demonstration / Smoke Tests
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print(COLORS["bold"] + "═══ Spinner Styles ═══" + COLORS["reset"])
    for style in ["dots", "line", "grow", "bounce", "arrow", "braille"]:
        sp = Spinner(f"Style: {style}", style=style, interval=0.15)
        sp.start()
        time.sleep(0.6)
        sp.succeed(f"Style '{style}' works!")
        sp.stop()
    print()

    print(COLORS["bold"] + "═══ Context Manager Spinner ═══" + COLORS["reset"])
    with Spinner("Simulating SEO audit...", style="dots", color="bright_cyan") as sp:
        time.sleep(0.5)
        sp.update("Checking meta tags...")
        time.sleep(0.5)
        sp.update("Analyzing content...")
        time.sleep(0.5)
        sp.succeed("Audit complete — score: 92/100")
    print()

    print(COLORS["bold"] + "═══ Spinner Failure ═══" + COLORS["reset"])
    with Spinner("Attempting crawl...", style="line", color="bright_yellow") as sp:
        time.sleep(0.5)
        sp.fail("Connection refused")
    print()

    print(COLORS["bold"] + "═══ MultiSpinner ═══" + COLORS["reset"])
    ms = MultiSpinner(style="dots")

    # Phase 1: All starting
    ms.add("crawler", "Crawling pages...")
    ms.add("analyzer", "Analyzing content...")
    ms.add("reporter", "Generating report...")
    ms.add("backlinks", "Checking backlinks...")
    print("Starting swarm...")
    ms.render_live()
    time.sleep(0.4)

    # Phase 2: Some updates
    ms.update("crawler", "Crawling page 42/150...")
    ms.update("analyzer", "Checking meta tags...")
    ms.render_live()
    time.sleep(0.4)

    # Phase 3: Completing
    ms.succeed("crawler", "Crawled 150 pages")
    ms.update("analyzer", "Analyzing headings...")
    ms.update("reporter", "Building PDF...")
    ms.update("backlinks", "Checking 25 backlinks...")
    ms.render_live()
    time.sleep(0.4)

    # Phase 4: More complete
    ms.succeed("analyzer", "Analysis complete")
    ms.succeed("reporter", "Report generated")
    ms.fail("backlinks", "Timeout — 3 links failed")
    ms.render_live()
    time.sleep(0.3)

    # Phase 5: Final state
    ms.stop()
    print()

    print(COLORS["bright_green"] + "All spinner tests passed!" + COLORS["reset"])
