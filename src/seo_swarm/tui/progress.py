"""
SEO SWARM - Progress Tracker & Live Display
==========================================
Multi-step progress tracker with live terminal updates.
Uses pure ANSI escape codes — zero external dependencies.

Components:
  - ProgressTracker: track multiple named steps with progress bars
  - LiveDisplay: auto-refreshing terminal display for live updates
"""

import sys
import time
import threading
from typing import List, Optional, Tuple

# ── ANSI Escape Codes ─────────────────────────────────────────────────

ANSI = {
    "reset":     "\033[0m",
    "bold":      "\033[1m",
    "dim":       "\033[2m",
    "italic":    "\033[3m",
    "underline": "\033[4m",
    "black":     "\033[30m",  "red":         "\033[31m",
    "green":     "\033[32m",  "yellow":      "\033[33m",
    "blue":      "\033[34m",  "magenta":     "\033[35m",
    "cyan":      "\033[36m",  "white":       "\033[37m",
    "bright_black":  "\033[90m", "bright_red":    "\033[91m",
    "bright_green":  "\033[92m", "bright_yellow": "\033[93m",
    "bright_blue":   "\033[94m", "bright_magenta":"\033[95m",
    "bright_cyan":   "\033[96m", "bright_white":  "\033[97m",
    # Cursor control
    "hide_cursor":   "\033[?25l",
    "show_cursor":   "\033[?25h",
    "clear_screen":  "\033[2J\033[H",
    "clear_line":    "\033[2K",
    "clear_down":    "\033[J",
    "cursor_up":     "\033[{}A",
    "cursor_down":   "\033[{}B",
    "save_cursor":   "\033[s",
    "restore_cursor":"\033[u",
}

# ── Constants ─────────────────────────────────────────────────────────

BAR_WIDTH = 30

STATUS_GLYPHS = {
    "pending":   ("  ", ANSI["dim"]),
    "running":   ("◉ ", ANSI["bright_cyan"]),
    "complete":  ("✓ ", ANSI["bright_green"]),
    "error":     ("✗ ", ANSI["bright_red"]),
}

# ── Helpers ───────────────────────────────────────────────────────────

def _make_bar(fraction: float, width: int = BAR_WIDTH) -> str:
    """Build a progress bar string: ██████░░░░░"""
    filled = max(0, min(width, int(round(fraction * width))))
    empty = width - filled
    return (ANSI["bright_green"] + "█" * filled +
            ANSI["dim"] + "░" * empty +
            ANSI["reset"])


def _pct(fraction: float) -> str:
    """Format fraction as a right-aligned percentage."""
    return f"{fraction * 100:5.0f}%"


# ── ProgressTracker ───────────────────────────────────────────────────

class ProgressTracker:
    """Track multiple steps with progress bars.

    Usage:
        pt = ProgressTracker(3, "SEO Audit")
        pt.start_step("Crawling")
        pt.update_step(0.5, "Found 50 pages...")
        pt.complete_step(success=True, detail="200 pages crawled")
        print(pt.render())
    """

    def __init__(self, total_steps: int, title: str = ""):
        self.total_steps = total_steps
        self.title = title
        self.steps: List[dict] = []          # filled as steps start
        self._current_step: Optional[int] = None

    # ── public API ────────────────────────────────────────────────

    def start_step(self, name: str):
        """Begin a new named step."""
        if len(self.steps) >= self.total_steps:
            raise IndexError(
                f"All {self.total_steps} steps already started"
            )
        self.steps.append({
            "name": name,
            "status": "running",
            "progress": 0.0,
            "message": "",
            "detail": "",
        })
        self._current_step = len(self.steps) - 1

    def update_step(self, progress: float, message: str = ""):
        """Set the progress (0.0 – 1.0) and optional message for the
        currently running step."""
        if self._current_step is None:
            return
        step = self.steps[self._current_step]
        step["progress"] = max(0.0, min(1.0, progress))
        step["message"] = message

    def complete_step(self, success: bool = True, detail: str = ""):
        """Mark the current step as complete (or error)."""
        if self._current_step is None:
            return
        step = self.steps[self._current_step]
        step["status"] = "complete" if success else "error"
        step["progress"] = 1.0
        step["detail"] = detail
        # Prepare for a possible next step
        self._current_step = None

    def render(self) -> str:
        """Return the full current view as a string."""
        lines: List[str] = []

        # ── title bar ──────────────────────────────────────────
        if self.title:
            bar = "═" * max(2, 60 - len(self.title) // 2)
            lines.append(f"{ANSI['bright_cyan']}{ANSI['bold']}"
                         f"{bar} {self.title} {bar}"
                         f"{ANSI['reset']}")

        # ── step rows ─────────────────────────────────────────
        for i in range(self.total_steps):
            lines.append(self._render_step_row(i))

        return "\n".join(lines)

    def render_live(self):
        """Print the tracker to the terminal (overwrites previous
        render when called repeatedly)."""
        sys.stdout.write(
            ANSI["cursor_up"] * (3 + self.total_steps)
            + ANSI["clear_down"]
            + self.render()
            + "\n"
        )
        sys.stdout.flush()

    # ── internals ───────────────────────────────────────────────

    def _render_step_row(self, idx: int) -> str:
        """Render a single step row."""
        if idx < len(self.steps):
            return self._render_started_step(idx)
        # future / pending step
        glyph, color = STATUS_GLYPHS["pending"]
        placeholder = f"Step {idx + 1} Pending"
        return (f"  {color}{glyph}{placeholder:<25}{ANSI['reset']}"
                f"  {ANSI['dim']}░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░"
                f"{ANSI['reset']}    0%")

    def _render_started_step(self, idx: int) -> str:
        step = self.steps[idx]
        status = step["status"]
        glyph, color = STATUS_GLYPHS[status]

        # name column
        name_col = f"{glyph}{step['name']:<23}"

        # bar
        bar = _make_bar(step["progress"])

        # percentage
        pct_str = _pct(step["progress"])

        # detail / message
        if status == "complete" and step["detail"]:
            tail = f" {ANSI['dim']}{step['detail']}{ANSI['reset']}"
        elif step["message"]:
            tail = f" {ANSI['dim']}{step['message']}{ANSI['reset']}"
        else:
            tail = ""

        return f"  {color}{name_col}{ANSI['reset']}  {bar}  {pct_str}{tail}"


# ── LiveDisplay ───────────────────────────────────────────────────────

class LiveDisplay:
    """Auto-refreshing live terminal display.

    Manages a region of the terminal, re-rendering on a timer.
    The content is set via `set_content()` and the refresh loop
    handles cursor hiding, line clearing, and restoration.

    Usage:
        ld = LiveDisplay(refresh_rate=0.1)
        ld.start()
        for i in range(100):
            ld.set_content([f"Progress: {i}%", f"[{'#'*i}{' '*(100-i)}]"])
            time.sleep(0.05)
        ld.stop()
    """

    def __init__(self, refresh_rate: float = 0.1):
        self.refresh_rate = refresh_rate
        self._lines: List[str] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._dirty = True
        self._line_count = 0

    # ── public API ────────────────────────────────────────────────

    def set_content(self, lines: List[str]):
        """Update the content to be displayed."""
        with self._lock:
            self._lines = list(lines)
            self._line_count = len(self._lines)
            self._dirty = True

    def start(self):
        """Begin the auto-refresh loop (runs in a background thread)."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._refresh_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the refresh loop and restore the cursor."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=self.refresh_rate * 3)
        self._clear_display()
        sys.stdout.write(ANSI["show_cursor"])
        sys.stdout.flush()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()

    # ── internals ───────────────────────────────────────────────

    def _refresh_loop(self):
        sys.stdout.write(ANSI["hide_cursor"])
        sys.stdout.flush()
        while self._running:
            with self._lock:
                if self._dirty:
                    self._render()
                    self._dirty = False
            time.sleep(self.refresh_rate)

    def _render(self):
        self._clear_display()
        for line in self._lines:
            sys.stdout.write(line + "\n")
        sys.stdout.flush()

    def _clear_display(self):
        """Clear the area previously occupied by the display."""
        if self._line_count:
            # Move up to the start of our area + clear down
            sys.stdout.write(ANSI["cursor_up"].format(self._line_count or 1))
            sys.stdout.write(ANSI["clear_down"])
        self._line_count = len(self._lines)


# ── Convenience Functions ─────────────────────────────────────────────

def progress_range(items, title: str = "", label_fn=None):
    """Iterate with a live progress tracker.

    Usage:
        for item in progress_range(agents, "Running Agents"):
            process(item)
    """
    total = len(items)
    tracker = ProgressTracker(total, title)
    for i, item in enumerate(items):
        name = label_fn(item) if label_fn else f"Item {i + 1}"
        tracker.start_step(name)
        tracker.render_live()
        yield item, tracker
        tracker.complete_step(success=True)
        tracker.render_live()


def spinner(message: str = "Working", delay: float = 0.1):
    """Generator that yields spinner frames.
    Usage:
        spin = spinner("Loading")
        for _ in range(20):
            sys.stdout.write(f"\\r{next(spin)}")
            time.sleep(0.1)
    """
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    i = 0
    while True:
        yield f"{ANSI['bright_cyan']}{frames[i % len(frames)]}"
        f" {message}{ANSI['reset']}"
        i += 1


# ── Self-Tests ────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"{ANSI['bold']}═══ ProgressTracker Demo ═══{ANSI['reset']}\n")

    pt = ProgressTracker(4, "SEO AUDIT")
    print(pt.render())
    print()

    # Step 1 — crawling
    pt.start_step("Crawl Site")
    pt.update_step(0.3, "Connecting...")
    print(pt.render())
    time.sleep(0.3)

    pt.update_step(0.7, "Found 150 pages")
    print(pt.render())
    time.sleep(0.3)

    pt.complete_step(success=True, detail="200 pages crawled")
    print(pt.render())
    time.sleep(0.3)

    # Step 2 — scoring
    pt.start_step("Score Pages")
    pt.update_step(0.5, "Analyzing content...")
    print(pt.render())
    time.sleep(0.3)

    pt.complete_step(success=True, detail="Avg score 78/100")
    print(pt.render())
    time.sleep(0.3)

    # Step 3 — reporting (error)
    pt.start_step("Generate Report")
    pt.update_step(0.4, "Rendering PDF...")
    print(pt.render())
    time.sleep(0.3)

    pt.complete_step(success=False, detail="PDF render failed")
    print(pt.render())
    time.sleep(0.3)

    # Step 4 — still pending
    print(pt.render())

    print(f"\n{ANSI['bold']}═══ LiveDisplay Demo ═══{ANSI['reset']}\n")

    ld = LiveDisplay(refresh_rate=0.08)
    ld.start()
    try:
        for i in range(101):
            bar = "█" * (i // 2) + "░" * (50 - i // 2)
            ld.set_content([
                f"{ANSI['bright_cyan']}Live Progress{ANSI['reset']}",
                f"[{ANSI['bright_green']}{bar}{ANSI['reset']}]  {i}%",
                f"{ANSI['dim']}Processing item {i // 10 + 1} of 10{ANSI['reset']}",
            ])
            time.sleep(0.03)
    finally:
        ld.stop()

    print(f"\n{ANSI['bold']}═══ Spinner Demo ═══{ANSI['reset']}\n")
    spin = spinner("Auditing site...")
    for _ in range(30):
        sys.stdout.write("\r" + next(spin))
        sys.stdout.flush()
        time.sleep(0.05)
    print(f"\r{ANSI['bright_green']}✓ Done!{ANSI['reset']}" + " " * 20)

    print(f"\n{ANSI['bold']}═══ progress_range Demo ═══{ANSI['reset']}\n")
    tasks = ["Crawl", "Score", "Report", "Deploy"]
    for task, t in progress_range(tasks, "TASK RUNNER"):
        time.sleep(0.2)
