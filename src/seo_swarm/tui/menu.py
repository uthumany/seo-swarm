"""
SEO SWARM - Interactive Terminal Menus
=======================================
Keyboard-navigable menus using raw terminal input.
Pure stdlib — zero external dependencies.

Components:
  - Menu:          arrow-key navigable single-select menu
  - SelectMenu:    multi-select checklist with space-toggle
  - Prompt:        styled input prompts (ask, confirm, select)
"""

import sys
import os
import platform
import time
from typing import List, Optional, Tuple, Union

_IS_WINDOWS = platform.system() == "Windows"

if _IS_WINDOWS:
    import msvcrt
else:
    import tty
    import termios
    import select

# ── ANSI Escape Codes ─────────────────────────────────────────────────

ANSI = {
    "reset":          "\033[0m",
    "bold":           "\033[1m",
    "dim":            "\033[2m",
    "underline":      "\033[4m",
    "black":          "\033[30m",  "red":            "\033[31m",
    "green":          "\033[32m",  "yellow":         "\033[33m",
    "blue":           "\033[34m",  "magenta":        "\033[35m",
    "cyan":           "\033[36m",  "white":          "\033[37m",
    "bright_black":   "\033[90m",  "bright_red":     "\033[91m",
    "bright_green":   "\033[92m",  "bright_yellow":  "\033[93m",
    "bright_blue":    "\033[94m",  "bright_magenta": "\033[95m",
    "bright_cyan":    "\033[96m",  "bright_white":   "\033[97m",
    "bg_bright_cyan": "\033[106m",
    "hide_cursor":    "\033[?25l",
    "show_cursor":    "\033[?25h",
    "clear_line":     "\033[2K",
    "cursor_up":      "\033[{}A",
}

# ── Terminal Detection ────────────────────────────────────────────────

def _is_terminal() -> bool:
    """Check if stdout is a real terminal."""
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _get_term_size() -> Tuple[int, int]:
    """Return (cols, rows) of the terminal, or a safe fallback."""
    try:
        return os.get_terminal_size()
    except (ValueError, OSError):
        return 80, 24


_ARROW_UP    = "\x1b[A"
_ARROW_DOWN  = "\x1b[B"
_ARROW_RIGHT = "\x1b[C"
_ARROW_LEFT  = "\x1b[D"
_ALT_UP      = "\x1b\x1b[A"
_ALT_DOWN    = "\x1b\x1b[B"

_ENTER       = "\r"
_ESC         = "\x1b"
_SPACE       = " "
_TAB         = "\t"


# ── Raw Terminal Input Helper ─────────────────────────────────────────

class _RawInput:
    """Context manager for reading single keystrokes in raw mode.
    Supports both Unix (termios/tty) and Windows (msvcrt)."""

    def __enter__(self):
        if not _is_terminal():
            raise RuntimeError("Not a terminal — menus require a TTY")
        self.fd = sys.stdin.fileno()
        if not _IS_WINDOWS:
            self.old = termios.tcgetattr(self.fd)
            tty.setraw(self.fd)
        sys.stdout.write(ANSI["hide_cursor"])
        sys.stdout.flush()
        return self

    def __exit__(self, *args):
        if not _IS_WINDOWS:
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old)
        sys.stdout.write(ANSI["show_cursor"])
        sys.stdout.flush()

    def read_key(self) -> str:
        """Read a single keypress. Returns string like '\x1b[A' on Unix,
        or the decoded key on Windows."""
        if _IS_WINDOWS:
            return self._read_key_windows()
        return self._read_key_unix()

    def _read_key_windows(self) -> str:
        """Read key using msvcrt on Windows."""
        ch = msvcrt.getwch()
        if ch == '\x00' or ch == '\xe0':
            # Extended key: read the scancode
            sc = msvcrt.getwch()
            mapping = {
                'H': _ARROW_UP,
                'P': _ARROW_DOWN,
                'M': _ARROW_RIGHT,
                'K': _ARROW_LEFT,
            }
            return mapping.get(sc, f'\x00{sc}')
        if ch == '\x1b':
            # Escape — check for escape sequences
            if msvcrt.kbhit():
                nxt = msvcrt.getwch()
                if nxt == '[':
                    if msvcrt.kbhit():
                        code = msvcrt.getwch()
                        seq_map = {
                            'A': _ARROW_UP, 'B': _ARROW_DOWN,
                            'C': _ARROW_RIGHT, 'D': _ARROW_LEFT,
                        }
                        return seq_map.get(code, f'\x1b[{code}')
                    return '\x1b['
                return '\x1b' + nxt
            return _ESC
        return ch

    def _read_key_unix(self) -> str:
        """Read key using termios on Unix."""
        ch = os.read(self.fd, 1)
        if ch == b"\x1b":
            seq = ch
            while True:
                r, _, _ = select.select([self.fd], [], [], 0.0)
                if not r:
                    break
                more = os.read(self.fd, 1)
                if not more:
                    break
                seq += more
                if len(seq) >= 6:
                    break
            return seq.decode("utf-8", errors="replace")
        return ch.decode("utf-8", errors="replace")


# ── Rendering Helpers ─────────────────────────────────────────────────

def _clear_lines(n: int):
    """Move cursor up N lines and clear them."""
    for _ in range(n):
        sys.stdout.write(ANSI["cursor_up"].format(1))
        sys.stdout.write(ANSI["clear_line"])


def _write(s: str):
    sys.stdout.write(s)
    sys.stdout.flush()


def _divider(width: int = 60) -> str:
    return f"{ANSI['dim']}{'─' * width}{ANSI['reset']}"


# ── Menu ──────────────────────────────────────────────────────────────

class Menu:
    """Arrow-key navigable single-select menu.

    Returns the *index* of the selected item, or -1 if cancelled.

    Usage:
        menu = Menu("Choose action", ["Audit", "Swarm", "Report"])
        choice = menu.show()
        if choice >= 0:
            print(f"Selected: {items[choice]}")
    """

    def __init__(self, title: str, items: List[str]):
        self.title = title
        self.items = items
        self._selected = 0

    def show(self) -> int:
        """Display the menu and return the selected index (-1 = cancelled)."""
        if not _is_terminal():
            return self._fallback()

        with _RawInput() as raw:
            self._selected = 0
            self._draw()
            while True:
                key = raw.read_key()
                if key == _ARROW_UP or key == "k":
                    self._move(-1)
                elif key == _ARROW_DOWN or key == "j":
                    self._move(1)
                elif key in (_ENTER, " "):
                    self._done()
                    return self._selected
                elif key in (_ESC, "q"):
                    self._done()
                    return -1

    def _fallback(self) -> int:
        """Numbered fallback when not a TTY."""
        print(f"\n{ANSI['bold']}{self.title}{ANSI['reset']}")
        print(_divider())
        for i, item in enumerate(self.items):
            print(f"  {ANSI['bright_cyan']}[{i + 1}]{ANSI['reset']} {item}")
        print()
        try:
            choice = int(input(f"{ANSI['bright_yellow']}▸ Choose [1-{len(self.items)}]: {ANSI['reset']}").strip())
            if 1 <= choice <= len(self.items):
                return choice - 1
        except (ValueError, KeyboardInterrupt):
            pass
        return -1

    def _move(self, delta: int):
        self._selected = (self._selected + delta) % len(self.items)
        self._draw()

    def _draw(self):
        _clear_lines(len(self.items) + 3)
        _write(f"\n  {ANSI['bold']}{ANSI['bright_cyan']}{self.title}{ANSI['reset']}\n")
        _write(f"  {_divider()}\n")
        for i, item in enumerate(self.items):
            if i == self._selected:
                _write(f"  {ANSI['bg_bright_cyan']}{ANSI['black']}"
                       f" {ANSI['bold']}▸ {item}{ANSI['reset']}\n")
            else:
                _write(f"  {ANSI['dim']}  {item}{ANSI['reset']}\n")
        _write(f"  {ANSI['dim']}↑↓ move  ↵ select  q/esc cancel{ANSI['reset']}\n")

    def _done(self):
        _clear_lines(len(self.items) + 3)
        _write("\n")


# ── SelectMenu ────────────────────────────────────────────────────────

class SelectMenu:
    """Multi-select checklist menu.

    Returns a list of selected indices.

    Usage:
        sm = SelectMenu("Choose agents", [("Crawler", True), ("Scorer", False)])
        selected = sm.show()
    """

    def __init__(self, title: str, options: List[Tuple[str, bool]]):
        self.title = title
        self.options = list(options)  # [(label, checked), ...]
        self._cursor = 0

    def show(self) -> List[int]:
        """Display and return list of selected indices."""
        if not _is_terminal():
            return self._fallback()

        with _RawInput() as raw:
            self._cursor = 0
            self._draw()
            while True:
                key = raw.read_key()
                if key == _ARROW_UP or key == "k":
                    self._cursor = (self._cursor - 1) % len(self.options)
                    self._draw()
                elif key == _ARROW_DOWN or key == "j":
                    self._cursor = (self._cursor + 1) % len(self.options)
                    self._draw()
                elif key == _SPACE:
                    label, checked = self.options[self._cursor]
                    self.options[self._cursor] = (label, not checked)
                    self._draw()
                elif key in (_ENTER,):
                    self._done()
                    return [i for i, (_, c) in enumerate(self.options) if c]
                elif key in (_ESC, "q"):
                    self._done()
                    return []

    def _fallback(self) -> List[int]:
        """Fallback for non-TTY — interactive numbered prompt."""
        print(f"\n{ANSI['bold']}{self.title}{ANSI['reset']}")
        print(_divider())
        for i, (label, checked) in enumerate(self.options):
            mark = "✓" if checked else " "
            print(f"  {ANSI['bright_cyan']}[{i + 1}]{ANSI['reset']} [{mark}] {label}")
        print()
        try:
            raw = input(f"{ANSI['bright_yellow']}▸ Indices (comma-separated, e.g. 1,3): {ANSI['reset']}")
            return [int(x.strip()) - 1 for x in raw.split(",") if x.strip().isdigit()]
        except (ValueError, KeyboardInterrupt):
            return []

    def _draw(self):
        _clear_lines(len(self.options) + 4)
        _write(f"\n  {ANSI['bold']}{ANSI['bright_cyan']}{self.title}{ANSI['reset']}\n")
        _write(f"  {_divider()}\n")
        for i, (label, checked) in enumerate(self.options):
            cursor_mark = "▸" if i == self._cursor else " "
            check_mark = f"{ANSI['bright_green']}✓{ANSI['reset']}" if checked else f"{ANSI['dim']}○{ANSI['reset']}"
            if i == self._cursor:
                _write(f"  {ANSI['bg_bright_cyan']}{ANSI['black']}"
                       f" {cursor_mark} {check_mark} {label}{ANSI['reset']}\n")
            else:
                _write(f"  {ANSI['dim']}  {check_mark} {label}{ANSI['reset']}\n")
        _write(f"  {ANSI['dim']}space toggle  ↑↓ move  ↵ confirm  q/esc cancel{ANSI['reset']}\n")

    def _done(self):
        _clear_lines(len(self.options) + 4)
        _write("\n")


# ── Prompt ────────────────────────────────────────────────────────────

class Prompt:
    """Styled input prompts with a ▸ indicator and colored output."""

    @staticmethod
    def ask(question: str, default: str = "") -> str:
        """Ask for text input.

        Usage:
            url = Prompt.ask("Enter URL", "https://")
        """
        hint = f" [{default}]" if default else ""
        prompt = (f"{ANSI['bright_cyan']}{ANSI['bold']}▸{ANSI['reset']}"
                  f" {ANSI['bright_white']}{question}{ANSI['dim']}{hint}"
                  f"{ANSI['reset']}: ")
        try:
            answer = input(prompt).strip()
            return answer if answer else default
        except (KeyboardInterrupt, EOFError):
            print()
            return default

    @staticmethod
    def confirm(question: str, default: bool = True) -> bool:
        """Ask for y/n confirmation.

        Usage:
            if Prompt.confirm("Proceed with audit?"):
                ...
        """
        yn = "Y/n" if default else "y/N"
        prompt = (f"{ANSI['bright_cyan']}{ANSI['bold']}▸{ANSI['reset']}"
                  f" {ANSI['bright_white']}{question}{ANSI['reset']}"
                  f" {ANSI['dim']}[{yn}]{ANSI['reset']}: ")
        try:
            answer = input(prompt).strip().lower()
            if not answer:
                return default
            return answer in ("y", "yes")
        except (KeyboardInterrupt, EOFError):
            print()
            return False

    @staticmethod
    def select(question: str, choices: List[str]) -> str:
        """Ask user to pick from a list of string choices.

        Falls back to numbered list when not a TTY.

        Usage:
            agent = Prompt.select("Select agent", ["Crawler", "Scorer", "Reporter"])
        """
        if _is_terminal():
            menu = Menu(question, choices)
            idx = menu.show()
            if idx >= 0:
                return choices[idx]
            return ""
        # Non-TTY fallback
        print(f"\n{ANSI['bold']}{question}{ANSI['reset']}")
        for i, c in enumerate(choices):
            print(f"  {ANSI['bright_cyan']}[{i + 1}]{ANSI['reset']} {c}")
        try:
            choice = int(input(f"{ANSI['bright_yellow']}▸ Choose [1-{len(choices)}]: {ANSI['reset']}"))
            if 1 <= choice <= len(choices):
                return choices[choice - 1]
        except (ValueError, KeyboardInterrupt, EOFError):
            pass
        return ""


# ── Self-Tests ────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\n{ANSI['bold']}═══ Menu Demo ═══{ANSI['reset']}\n")

    menu = Menu("Choose Action", [
        "🔍  Run SEO Audit",
        "🐝  Launch Swarm Mode",
        "📊  Generate Report",
        "📋  List Agents",
        "❌  Exit",
    ])
    choice = menu.show()
    if choice >= 0:
        print(f"{ANSI['bright_green']}✓ Selected index: {choice}{ANSI['reset']}")
    else:
        print(f"{ANSI['bright_red']}✗ Cancelled{ANSI['reset']}")

    print(f"\n{ANSI['bold']}═══ SelectMenu Demo ═══{ANSI['reset']}\n")

    sm = SelectMenu("Select Agents", [
        ("🔧  Technical SEO", True),
        ("✍️  Content SEO", False),
        ("📍  Local SEO", True),
        ("🔗  Off-Page SEO", False),
        ("📊  Data Analyst", False),
    ])
    selected = sm.show()
    if selected:
        print(f"{ANSI['bright_green']}✓ Selected indices: {selected}{ANSI['reset']}")
    else:
        print(f"{ANSI['bright_red']}✗ None selected (cancelled){ANSI['reset']}")

    print(f"\n{ANSI['bold']}═══ Prompt Demo ═══{ANSI['reset']}\n")

    url = Prompt.ask("Enter site URL", "https://example.com")
    print(f"  URL: {url}")

    proceed = Prompt.confirm("Run full audit?", default=True)
    print(f"  Proceed: {proceed}")

    agent = Prompt.select("Choose primary agent",
                          ["Technical SEO", "Content SEO", "Local SEO", "Data Analyst"])
    print(f"  Agent: {agent}")
