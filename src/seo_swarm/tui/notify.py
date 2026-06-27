"""
SEO SWARM - Notification & Animation System
=============================================
Toast notifications, notification stacks, and ASCII animations.
Pure stdlib — zero external dependencies.

Components:
  - Toast:             pop-up notification that auto-disappears
  - NotificationStack: scrollable history of notifications
  - Animator:          typewriter, reveal, pulse, countdown, banner
"""

import sys
import time
import threading
from typing import List, Optional

# ── ANSI Escape Codes ─────────────────────────────────────────────────

ANSI = {
    "reset":          "\033[0m",
    "bold":           "\033[1m",
    "dim":            "\033[2m",
    "black":          "\033[30m",  "red":            "\033[31m",
    "green":          "\033[32m",  "yellow":         "\033[33m",
    "blue":           "\033[34m",  "magenta":        "\033[35m",
    "cyan":           "\033[36m",  "white":          "\033[37m",
    "bright_black":   "\033[90m",  "bright_red":     "\033[91m",
    "bright_green":   "\033[92m",  "bright_yellow":  "\033[93m",
    "bright_blue":    "\033[94m",  "bright_magenta": "\033[95m",
    "bright_cyan":    "\033[96m",  "bright_white":   "\033[97m",
    "bg_bright_red":  "\033[101m", "bg_bright_green":"\033[102m",
    "bg_bright_yellow":"\033[103m","bg_bright_blue": "\033[104m",
    "bg_bright_cyan": "\033[106m",
    "hide_cursor":    "\033[?25l",
    "show_cursor":    "\033[?25h",
    "clear_line":     "\033[2K",
    "cursor_up":      "\033[{}A",
    "save_cursor":    "\033[s",
    "restore_cursor": "\033[u",
}

# ── Style Map ─────────────────────────────────────────────────────────

STYLES = {
    "info": {
        "icon":    "ℹ",
        "fg":      ANSI["bright_cyan"],
        "bg":      ANSI["bg_bright_cyan"],
        "border":  ANSI["cyan"],
    },
    "success": {
        "icon":    "✓",
        "fg":      ANSI["bright_green"],
        "bg":      ANSI["bg_bright_green"],
        "border":  ANSI["green"],
    },
    "warning": {
        "icon":    "⚠",
        "fg":      ANSI["bright_yellow"],
        "bg":      ANSI["bg_bright_yellow"],
        "border":  ANSI["yellow"],
    },
    "error": {
        "icon":    "✗",
        "fg":      ANSI["bright_red"],
        "bg":      ANSI["bg_bright_red"],
        "border":  ANSI["red"],
    },
}


def _write(s: str):
    sys.stdout.write(s)
    sys.stdout.flush()


# ── Toast ─────────────────────────────────────────────────────────────

class Toast:
    """Pop-up notification that appears at the bottom of the terminal
    and auto-disappears after a configurable duration.

    Styles: 'info', 'success', 'warning', 'error'.

    Usage:
        Toast.show("Audit complete!", style="success", duration=2.0)
    """

    # Track the active toast thread so we can overlap safely
    _active_thread: Optional[threading.Thread] = None

    @classmethod
    def show(cls, message: str, style: str = "info", duration: float = 2.0):
        """Show a toast notification. Runs in a background thread;
        returns immediately if a toast is already showing (queue skipped).

        On non-TTY, prints a plain line instead.
        """
        if not cls._is_terminal():
            cls._plain_show(message, style)
            return

        s = STYLES.get(style, STYLES["info"])

        def _run():
            cls._render_toast(message, s, duration)

        # Fire-and-forget in a daemon thread
        t = threading.Thread(target=_run, daemon=True)
        t.start()
        # Don't track — allow overlapping toasts

    @staticmethod
    def _is_terminal() -> bool:
        return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

    @staticmethod
    def _plain_show(message: str, style: str):
        """Plain-text fallback for pipes / non-TTY."""
        label = style.upper()
        print(f"[{label}] {message}")

    @staticmethod
    def _render_toast(message: str, s: dict, duration: float):
        """Render the toast in a new line, sleep, then clear."""
        # Save cursor position
        _write(ANSI["save_cursor"])
        # Move to bottom area — just write a new line
        _write("\n")

        icon = s["icon"]
        fg = s["fg"]
        bg = s["bg"]
        border = s["border"]
        r = ANSI["reset"]
        b = ANSI["bold"]

        width = min(len(message) + 12, 80)

        # Border decorations
        top = f"{border}┌{'─' * (width - 2)}┐{r}"
        mid = f"{border}│{r} {fg}{b}{icon} {message}{r} {border}│{r}"
        bot = f"{border}└{'─' * (width - 2)}┘{r}"

        # Animation: type the toast in
        _write(top + "\n")
        time.sleep(0.05)
        _write(mid + "\n")
        _write(bot + "\n")

        time.sleep(duration)

        # Clear lines and restore cursor
        _write(ANSI["cursor_up"].format(3))
        _write(ANSI["clear_line"] + "\n" + ANSI["clear_line"] + "\n" + ANSI["clear_line"])
        _write(ANSI["cursor_up"].format(3))
        _write(ANSI["restore_cursor"])


# ── NotificationStack ─────────────────────────────────────────────────

class NotificationStack:
    """Stack of notifications with history.

    Usage:
        ns = NotificationStack(max_visible=5)
        ns.push("Crawl started", "info")
        ns.push("50 pages found", "success")
        ns.push("Connection refused", "error")
        print(ns.render())
    """

    def __init__(self, max_visible: int = 5):
        self.max_visible = max_visible
        self._stack: List[dict] = []

    def push(self, message: str, style: str = "info"):
        """Add a notification to the stack."""
        self._stack.append({
            "message": message,
            "style": style,
            "time": time.strftime("%H:%M:%S"),
        })

    def render(self) -> str:
        """Return the last N notifications as a string."""
        visible = self._stack[-self.max_visible:]
        if not visible:
            return f"{ANSI['dim']}(no notifications){ANSI['reset']}"

        lines = []
        lines.append(f"  {ANSI['bold']}{ANSI['bright_white']}"
                     f"NOTIFICATIONS{ANSI['reset']}")
        lines.append(f"  {ANSI['dim']}{'─' * 50}{ANSI['reset']}")

        for note in visible:
            s = STYLES.get(note["style"], STYLES["info"])
            fg = s["fg"]
            icon = s["icon"]
            lines.append(
                f"  {fg}{icon}{ANSI['reset']}"
                f" {ANSI['dim']}[{note['time']}]{ANSI['reset']}"
                f" {note['message']}"
            )

        return "\n".join(lines)

    def clear(self):
        """Remove all notifications."""
        self._stack.clear()


# ── Animator ──────────────────────────────────────────────────────────

class Animator:
    """Frame-by-frame ASCII animations for terminal output.

    All methods are static; they write directly to stdout.
    Call from a TTY for best results — non-TTY falls back to
    instant printing without delays.
    """

    _tty: Optional[bool] = None

    @classmethod
    def _is_tty(cls) -> bool:
        if cls._tty is None:
            cls._tty = (hasattr(sys.stdout, "isatty")
                        and sys.stdout.isatty())
        return cls._tty

    # ── typewriter ───────────────────────────────────────────────

    @staticmethod
    def typewriter(text: str, delay: float = 0.03):
        """Print text character by character like a typewriter.

        Usage:
            Animator.typewriter("Welcome to SEO SWARM!")
        """
        for ch in text:
            _write(ch)
            if delay > 0:
                time.sleep(delay)
        _write("\n")

    # ── reveal ───────────────────────────────────────────────────

    @staticmethod
    def reveal(lines: List[str], delay: float = 0.1):
        """Reveal text line by line with a short pause.

        Usage:
            Animator.reveal(["Line 1", "Line 2", "Line 3"])
        """
        for line in lines:
            _write(line + "\n")
            if delay > 0 and Animator._is_tty():
                time.sleep(delay)

    # ── pulse ────────────────────────────────────────────────────

    @staticmethod
    def pulse(text: str, times: int = 3, delay: float = 0.3):
        """Flash text with pulsing effect (bold ↔ dim toggle).

        Usage:
            Animator.pulse("COMPLETE!", times=5, delay=0.2)
        """
        for i in range(times):
            if i % 2 == 0:
                _write(f"\r{ANSI['bold']}{ANSI['bright_green']}"
                       f"  {text}  {ANSI['reset']}")
            else:
                _write(f"\r{ANSI['dim']}  {text}  {ANSI['reset']}")
            if delay > 0 and Animator._is_tty():
                time.sleep(delay)
        # Final bright state
        _write(f"\r{ANSI['bold']}{ANSI['bright_green']}"
               f"  {text}  {ANSI['reset']}")
        _write("\n")

    # ── countdown ────────────────────────────────────────────────

    @staticmethod
    def countdown(seconds: int, message: str = "Starting in"):
        """Display a countdown: 3... 2... 1...

        Usage:
            Animator.countdown(5, "Launching swarm in")
        """
        for i in range(seconds, 0, -1):
            _write(f"\r{message} {ANSI['bold']}{ANSI['bright_yellow']}"
                   f"{i}...{ANSI['reset']}")
            if Animator._is_tty():
                time.sleep(1)
        _write(f"\r{ANSI['bright_green']}{ANSI['bold']}"
               f"GO!{ANSI['reset']}" + " " * 20 + "\n")

    # ── banner_slide ─────────────────────────────────────────────

    @staticmethod
    def banner_slide(banner_lines: List[str], direction: str = "down"):
        """Slide a banner in from the given direction.

        Directions: 'down' (from top), 'up' (from bottom),
        'left', 'right'.

        Usage:
            banner = [
                "╔══════════════════════════╗",
                "║    SEO SWARM v1.0        ║",
                "╚══════════════════════════╝",
            ]
            Animator.banner_slide(banner, "down")
        """
        if not Animator._is_tty():
            for line in banner_lines:
                print(line)
            return

        if direction in ("down", "up"):
            Animator._banner_slide_vertical(banner_lines, direction)
        else:
            Animator._banner_slide_horizontal(banner_lines, direction)

    @staticmethod
    def _banner_slide_vertical(lines: List[str], direction: str):
        """Slide banner vertically."""
        width = max(len(l.rstrip(ANSI["reset"])) if ANSI["reset"] in l
                    else len(l) for l in lines)

        if direction == "down":
            # Reveal from top, line by line
            for i in range(1, len(lines) + 1):
                # Clear previous frame
                for _ in range(i - 1):
                    _write(ANSI["cursor_up"].format(1) + ANSI["clear_line"])
                for j in range(i):
                    _write(lines[j] + "\n")
                time.sleep(0.1)
            # Print remaining blank rows then clear them
            # (just leave the banner visible)
        else:
            # Slide up — print blank rows first, then shift up
            blanks = [" " * width] * (len(lines))
            for i in range(1, len(lines) + 1):
                for _ in range(i):
                    _write(ANSI["cursor_up"].format(1) + ANSI["clear_line"])
                for j in range(i):
                    idx = -(i - j)  # bottom lines first
                    _write(lines[idx] + "\n")
                time.sleep(0.1)

    @staticmethod
    def _banner_slide_horizontal(lines: List[str], direction: str):
        """Slide banner horizontally (simple effect — print progressively)."""
        for line in lines:
            stripped = line.replace(ANSI["reset"],
                                    "").replace(ANSI["bold"],
                                                "").replace(ANSI["bright_cyan"],
                                                            "")
            # Strip ANSI for length calculation
            clean = ""
            skip = False
            for ch in line:
                if ch == "\033":
                    skip = True
                if not skip:
                    clean += ch
                if skip and ch == "m":
                    skip = False

            if direction == "right":
                for i in range(1, len(clean) + 1):
                    _write("\r" + clean[:i])
                    time.sleep(0.005)
                _write("\n")
            else:
                for i in range(len(clean), 0, -1):
                    padding = " " * (len(clean) - i)
                    _write("\r" + padding + clean[len(clean) - i:])
                    time.sleep(0.005)
                _write("\n")

    # ── spinner (reusable generator) ─────────────────────────────

    @staticmethod
    def spin(message: str = "Working"):
        """Return a spinner generator.

        Usage:
            spinner = Animator.spin("Loading")
            for _ in range(20):
                sys.stdout.write(f"\\r{next(spinner)}")
                time.sleep(0.1)
        """
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        i = 0
        while True:
            yield (f"{ANSI['bright_cyan']}{frames[i % len(frames)]}"
                   f" {message}{ANSI['reset']}")
            i += 1


# ── Self-Tests ────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"{ANSI['bold']}═══ Toast Demo ═══{ANSI['reset']}\n")

    Toast.show("Connecting to site...", style="info", duration=1.5)
    time.sleep(2.0)  # wait for toast to finish

    Toast.show("Audit completed successfully!", style="success", duration=1.5)
    time.sleep(2.0)

    Toast.show("Low word count detected", style="warning", duration=1.5)
    time.sleep(2.0)

    Toast.show("Connection refused: timeout", style="error", duration=1.5)
    time.sleep(2.0)

    print(f"\n{ANSI['bold']}═══ NotificationStack Demo ═══{ANSI['reset']}\n")

    ns = NotificationStack(max_visible=5)
    ns.push("Crawl started for example.com", "info")
    ns.push("Found 200 pages", "success")
    ns.push("Missing meta descriptions on 15 pages", "warning")
    ns.push("Failed to fetch /admin (403)", "error")
    ns.push("Report generated", "success")

    print(ns.render())

    print(f"\n{ANSI['bold']}═══ Animator.typewriter Demo ═══{ANSI['reset']}\n")
    Animator.typewriter("🐝 Welcome to SEO SWARM — the autonomous SEO auditing platform!", delay=0.02)
    print()

    print(f"{ANSI['bold']}═══ Animator.reveal Demo ═══{ANSI['reset']}\n")
    Animator.reveal([
        f"{ANSI['bright_cyan']}› Initializing crawler engine...{ANSI['reset']}",
        f"{ANSI['bright_cyan']}› Loading SEO ruleset...{ANSI['reset']}",
        f"{ANSI['bright_green']}› Ready.{ANSI['reset']}",
    ], delay=0.15)
    print()

    print(f"{ANSI['bold']}═══ Animator.pulse Demo ═══{ANSI['reset']}")
    Animator.pulse("AUDIT COMPLETE!", times=5, delay=0.2)
    print()

    print(f"{ANSI['bold']}═══ Animator.countdown Demo ═══{ANSI['reset']}")
    Animator.countdown(3, "Starting swarm in")
    print()

    print(f"{ANSI['bold']}═══ Animator.banner_slide Demo ═══{ANSI['reset']}")
    banner = [
        f"  {ANSI['bold']}{ANSI['bright_cyan']}╔══════════════════════════════╗{ANSI['reset']}",
        f"  {ANSI['bold']}{ANSI['bright_cyan']}║{ANSI['reset']}     {ANSI['bright_yellow']}SEO SWARM v1.0{ANSI['reset']}         {ANSI['bold']}{ANSI['bright_cyan']}║{ANSI['reset']}",
        f"  {ANSI['bold']}{ANSI['bright_cyan']}║{ANSI['reset']}   {ANSI['dim']}Autonomous SEO Audit{ANSI['reset']}   {ANSI['bold']}{ANSI['bright_cyan']}║{ANSI['reset']}",
        f"  {ANSI['bold']}{ANSI['bright_cyan']}╚══════════════════════════════╝{ANSI['reset']}",
    ]
    Animator.banner_slide(banner, "down")
    print()

    print(f"{ANSI['bold']}═══ Animator.spin Demo ═══{ANSI['reset']}")
    spinner = Animator.spin("Finalizing audit...")
    for _ in range(30):
        _write("\r" + next(spinner))
        time.sleep(0.05)
    _write(f"\r{ANSI['bright_green']}✓ Done!{ANSI['reset']}" + " " * 30 + "\n")
    print()
