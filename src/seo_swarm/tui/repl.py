"""
SEO SWARM — Interactive REPL Engine
====================================
Persistent chat-like command panel inspired by Hermes Agent's interactive CLI.
Opens when seo-swarm is invoked without subcommands, providing a colorful,
theme-aware read-eval-print loop with slash-commands, shortcuts, and history.

Zero external dependencies — pure Python 3.8+ stdlib.
"""

import sys
import os
import shutil
import traceback
from typing import Dict, Optional, Tuple, Callable, Any

# ── Try readline for history on non-Windows; fallback on Windows ──
try:
    import readline
    _HAS_READLINE = True
except ImportError:
    try:
        import pyreadline as readline
        _HAS_READLINE = True
    except ImportError:
        _HAS_READLINE = False

from seo_swarm.tui.dashboard import COLORS
from seo_swarm.tui.themes import ThemeManager, THEMES
from seo_swarm.agents.registry import AgentRegistry
from seo_swarm.ascii.banners import ASCIIBanners


# ══════════════════════════════════════════════════════════════════════════════
# Lightweight fake argparse namespace for routing to existing CLI handlers
# ══════════════════════════════════════════════════════════════════════════════

class Args:
    """Minimal attribute-bag that mimics argparse.Namespace for CLI handlers.

    Supports both attribute access (args.url) and dict-style access (args["url"]).
    """
    __slots__ = ("__dict__",)

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __contains__(self, key):
        return key in self.__dict__

    def __repr__(self):
        return f"Args({', '.join(f'{k}={v!r}' for k, v in self.__dict__.items())})"


# ══════════════════════════════════════════════════════════════════════════════
# Slash-command registry — each entry maps a trigger to (description, handler_key)
# ══════════════════════════════════════════════════════════════════════════════

SLASH_COMMANDS: Dict[str, Tuple[str, Optional[str]]] = {
    "/audit":        ("Run SEO audit on URL",            "audit"),
    "/swarm":        ("Run all 10 agents in parallel",    "swarm"),
    "/dashboard":    ("Open interactive dashboard",        "dashboard"),
    "/agents":       ("List all SEO agents",              "agents"),
    "/scorecard":    ("Calculate SEO scorecard (0-100)",   "scorecard"),
    "/crawl":        ("Crawl website for SEO data",       "crawl"),
    "/report":       ("Generate audit report",             "report"),
    "/competitor":   ("Compare against competitors",       "competitor"),
    "/sitemap":      ("Generate XML sitemap",              "sitemap"),
    "/schema":       ("Generate JSON-LD schema",           "schema"),
    "/track":        ("Track keyword rankings",            "track"),
    "/backlinks":    ("Analyze backlink profile",          "backlinks"),
    "/content":      ("Analyze content quality",           "content-analyze"),
    "/monitor":      ("SEO health monitoring",             "monitor"),
    "/theme":        ("Switch color theme",                "theme"),
    "/pixel":        ("Show pixel art gallery",            "pixel-gallery"),
    "/portrait":     ("Show agent portrait",                "portrait"),
    "/help":         ("Show this help",                    None),
    "/exit":         ("Exit SEO SWARM",                    None),
    "/quit":         ("Exit SEO SWARM",                    None),
    "/clear":        ("Clear screen",                      None),
    "/stats":        ("Show SWARM statistics",             None),
    "/banner":       ("Reprint welcome banner",            None),
    "/version":      ("Show version info",                 None),
    "/history":      ("Show command history",              None),
    "/memory":       ("Search local memory",               "memory"),
}

# Shortcut aliases — single-letter quick access
SHORTCUTS: Dict[str, str] = {
    "a":    "audit",
    "s":    "swarm",
    "d":    "dashboard",
    "p":    "pixel-gallery",
    "ag":   "agents",
    "sc":   "scorecard",
    "cr":   "crawl",
    "rp":   "report",
    "cp":   "competitor",
    "sm":   "sitemap",
    "sh":   "schema",
    "tr":   "track",
    "bl":   "backlinks",
    "ca":   "content-analyze",
    "mn":   "monitor",
    "th":   "theme",
    "pg":   "pixel-gallery",
    "pt":   "portrait",
    "mm":   "memory",
    "h":    "help",
    "q":    "exit",
    "x":    "exit",
    "cls":  "clear",
    "?":    "help",
}

# Natural-language command mapping — words to commands
NATURAL_COMMANDS: Dict[str, str] = {
    "audit":        "audit",
    "swarm":        "swarm",
    "dashboard":    "dashboard",
    "agents":       "agents",
    "scorecard":    "scorecard",
    "crawl":        "crawl",
    "report":       "report",
    "competitor":   "competitor",
    "sitemap":      "sitemap",
    "schema":       "schema",
    "track":        "track",
    "backlinks":    "backlinks",
    "content":      "content-analyze",
    "analyze":      "content-analyze",
    "monitor":      "monitor",
    "theme":        "theme",
    "pixel":        "pixel-gallery",
    "gallery":      "pixel-gallery",
    "portrait":     "portrait",
    "memory":       "memory",
    "search":       "memory",
    "agent":        "agents",
    "exit":         "exit",
    "quit":         "exit",
    "clear":        "clear",
    "help":         "help",
    "stats":        "stats",
    "banner":       "banner",
    "version":       "version",
    "history":      "history",
}


# ══════════════════════════════════════════════════════════════════════════════
# SwarmREPL — the main interactive engine
# ══════════════════════════════════════════════════════════════════════════════

class SwarmREPL:
    """Interactive chat-like REPL for SEO SWARM.

    Opens a persistent session where users type commands naturally,
    with colored prompts, slash-command support, shortcuts, input history,
    and graceful error handling.

    Usage:
        repl = SwarmREPL()
        repl.run()
    """

    def __init__(self):
        """Initialise the REPL: load theme, set up command registry, history."""
        self._running = False
        self._theme_manager = ThemeManager()
        self._command_count = 0
        self._error_count = 0
        self._startup_time = None  # set in run()

        # Resolve theme colours for prompt rendering
        self._refresh_theme_colors()

        # Load command handler registry from existing CLI functions
        self._handlers = self._build_handler_registry()

        # Set up readline history
        self._history_file = os.path.join(
            os.path.expanduser("~"), ".seo-swarm", "repl_history"
        )
        self._setup_history()

    # ── Public entry point ──────────────────────────────────────────────────

    def run(self):
        """Main REPL loop.  Shows banner, then drops into the prompt."""
        import time as _time
        self._running = True
        self._startup_time = _time.time()

        self._show_welcome()

        while self._running:
            try:
                line = self._read_input()
            except (EOFError, KeyboardInterrupt):
                print()  # newline after ^C / ^D
                self._shutdown()
                break

            if line is None:          # EOF / Ctrl+D
                self._shutdown()
                break

            stripped = line.strip()
            if not stripped:
                continue

            self._command_count += 1
            self._save_history(stripped)

            try:
                command, args = self._parse(stripped)
                if command == "exit":
                    self._shutdown()
                    break
                elif command == "help":
                    self._show_help()
                elif command == "clear":
                    self._clear_screen()
                    # Reprint a compact header after clear
                    print(COLORS["bright_cyan"] + "SEO SWARM REPL" + COLORS["reset"] +
                          " — type /help for commands")
                elif command == "stats":
                    self._show_stats()
                elif command == "banner":
                    self._show_welcome()
                elif command == "version":
                    self._show_version()
                elif command == "history":
                    self._show_history()
                elif command == "theme":
                    self._handle_theme(args)
                elif command in self._handlers:
                    self._execute(command, args)
                else:
                    # Unknown — try fuzzy match suggestion
                    suggestion = self._fuzzy_match(command)
                    if suggestion:
                        print(f"  {COLORS['dim']}Unknown command '{command}'. "
                              f"Did you mean '{suggestion}'?{COLORS['reset']}")
                    else:
                        print(f"  {COLORS['bright_red']}Unknown command: "
                              f"{command}{COLORS['reset']}")
                        print(f"  Type {COLORS['bright_cyan']}/help"
                              f"{COLORS['reset']} to see available commands.")

            except Exception as exc:
                self._error_count += 1
                self._print_error(exc)

    # ── Input / prompt ──────────────────────────────────────────────────────

    def _read_input(self) -> Optional[str]:
        """Read one line with a themed prompt. Returns None on EOF/KeyboardInterrupt."""
        try:
            return input(self._prompt())
        except KeyboardInterrupt:
            raise
        except EOFError:
            return None

    def _prompt(self) -> str:
        """Return colored prompt string like 'seo ▸ '"""
        arrow = f"{self._c_prompt}▸{COLORS['reset']}"
        label = f"{self._c_accent}seo{COLORS['reset']}"
        return f"{label} {arrow} "

    # ── Parsing ─────────────────────────────────────────────────────────────

    def _parse(self, line: str) -> Tuple[str, Args]:
        """Parse raw input into (command_key, Args).

        Resolution order:
          1. Slash-commands:  /audit https://example.com
          2. Natural commands: audit https://example.com
          3. Shortcuts:        a https://example.com
          4. Raw pass-through

        Returns:
            Tuple of (command_key_string, Args namespace).
        """
        # ── 0. Empty / whitespace input ────────────────────────────────
        stripped = line.strip()
        if not stripped:
            return (None, Args())

        line = stripped  # Use stripped line for consistent parsing

        # ── 1. Slash command ───────────────────────────────────────────
        if line.startswith("/"):
            parts = line[1:].strip().split(maxsplit=1)
            cmd = parts[0].lower() if parts[0] else ""
            rest = parts[1] if len(parts) > 1 else ""

            # Resolve slash command to handler key
            slash_key = f"/{cmd}"
            if slash_key in SLASH_COMMANDS:
                handler_key = SLASH_COMMANDS[slash_key][1]
                if handler_key is None:
                    # Meta commands: /help, /exit, /quit, /clear, /stats, /banner, /version, /history
                    return (cmd, Args(raw=rest))
                return (handler_key, self._build_args(handler_key, rest))
            else:
                # Unknown slash command — pass through as-is
                return (cmd, Args(raw=rest))

        # ── 2. Bare shortcut (single word, no slash) ──────────────────
        first_word = line.strip().split(maxsplit=1)[0].lower()
        if first_word in SHORTCUTS:
            mapped = SHORTCUTS[first_word]
            if mapped in ("exit", "help", "clear", "stats", "banner", "version", "history"):
                return (mapped, Args(raw=""))
            rest = line.strip().split(maxsplit=1)[1] if " " in line else ""
            return (mapped, self._build_args(mapped, rest))

        # ── 3. Natural language command ───────────────────────────────
        if first_word in NATURAL_COMMANDS:
            mapped = NATURAL_COMMANDS[first_word]
            if mapped in ("exit", "help", "clear", "stats", "banner", "version", "history"):
                return (mapped, Args(raw=""))
            rest = line.strip().split(maxsplit=1)[1] if " " in line else ""
            return (mapped, self._build_args(mapped, rest))

        # ── 4. Fallback: unrecognised command ─────────────────────────
        return ("unknown", Args(raw=line))

    def _build_args(self, handler_key: str, rest: str) -> Args:
        """Build an Args namespace matching what the CLI handlers expect.

        Each handler function in cli.py expects a specific set of attributes
        (e.g., audit expects 'url' + 'agents' + 'json').  We map the raw
        rest string onto the expected arguments.
        """
        rest = rest.strip()

        # Common argument mappings per command
        if handler_key == "audit":
            parts = rest.split()
            url = parts[0] if parts else ""
            return Args(url=url, agents=None, json=False)

        elif handler_key == "swarm":
            return Args(url=rest if rest else "")

        elif handler_key == "dashboard":
            return Args()

        elif handler_key == "agents":
            return Args(pixel_cards=False, pixel_gallery=False, art=False, row=False)

        elif handler_key == "scorecard":
            parts = rest.split()
            url = parts[0] if parts else ""
            return Args(url=url, json=False)

        elif handler_key == "crawl":
            parts = rest.split()
            url = parts[0] if parts else ""
            max_pages = 50
            depth = 3
            # Parse optional --max-pages and --depth
            i = 1
            while i < len(parts):
                if parts[i] in ("--max-pages", "-m") and i + 1 < len(parts):
                    try:
                        max_pages = int(parts[i + 1])
                    except ValueError:
                        pass
                    i += 2
                elif parts[i] in ("--depth", "-d") and i + 1 < len(parts):
                    try:
                        depth = int(parts[i + 1])
                    except ValueError:
                        pass
                    i += 2
                else:
                    i += 1
            return Args(url=url, max_pages=max_pages, depth=depth)

        elif handler_key == "report":
            parts = rest.split()
            url = parts[0] if parts else ""
            fmt = "html"
            output = None
            i = 1
            while i < len(parts):
                if parts[i] in ("--format", "-f") and i + 1 < len(parts):
                    fmt = parts[i + 1]
                    i += 2
                elif parts[i] in ("--output", "-o") and i + 1 < len(parts):
                    output = parts[i + 1]
                    i += 2
                else:
                    i += 1
            return Args(url=url, format=fmt, output=output)

        elif handler_key == "competitor":
            parts = rest.split()
            url = parts[0] if parts else ""
            competitors = parts[1:] if len(parts) > 1 else []
            return Args(url=url, competitors=competitors, json=False)

        elif handler_key == "sitemap":
            parts = rest.split()
            urls = parts if parts else None
            return Args(urls=urls, from_crawl=None, output="sitemap.xml", validate=None)

        elif handler_key == "schema":
            parts = rest.split()
            schema_type = parts[0] if parts else "Organization"
            data = " ".join(parts[1:]) if len(parts) > 1 else "{}"
            return Args(type=schema_type, data=data, list=False)

        elif handler_key == "track":
            parts = rest.split()
            keyword = parts[0] if parts else ""
            url = parts[1] if len(parts) > 1 else None
            return Args(keyword=keyword, url=url, history=False, trends=False, summary=False)

        elif handler_key == "backlinks":
            parts = rest.split()
            domain = parts[0] if parts else ""
            compare = parts[1:] if len(parts) > 1 else None
            return Args(domain=domain, compare=compare)

        elif handler_key == "content-analyze":
            parts = rest.split()
            if parts and parts[0].startswith("http"):
                return Args(text=None, url=parts[0], keyword=parts[1] if len(parts) > 1 else None, file=None)
            else:
                return Args(text=rest if rest else "", url=None, keyword=parts[0] if parts else None, file=None)

        elif handler_key == "monitor":
            parts = rest.split()
            url = parts[0] if parts else ""
            return Args(url=url, history=False, alerts=False, trend=None)

        elif handler_key == "theme":
            return Args(name=rest if rest else None, list=False)

        elif handler_key == "pixel-gallery":
            return Args()

        elif handler_key == "portrait":
            parts = rest.split()
            return Args(name=parts[0] if parts else "", compact=False)

        elif handler_key == "memory":
            return Args(query=rest if rest else "")

        # Generic fallback
        return Args(raw=rest)

    # ── Execution ───────────────────────────────────────────────────────────

    def _execute(self, command: str, args: Args):
        """Execute a parsed command by routing to the registered handler."""
        handler = self._handlers.get(command)
        if handler is None:
            print(f"  {COLORS['bright_red']}No handler for: {command}{COLORS['reset']}")
            return
        try:
            handler(args)
        except Exception as exc:
            self._error_count += 1
            self._print_error(exc)

    # ── Handler registry ────────────────────────────────────────────────────

    def _build_handler_registry(self) -> Dict[str, Callable]:
        """Build a mapping of command keys to CLI handler functions.

        Imports handlers lazily to avoid circular imports and reduce startup time.
        All handlers are imported from seo_swarm.cli.
        """
        from seo_swarm.cli import (
            run_audit, run_agent, run_browser, run_swarm, show_dashboard,
            show_agents, show_portrait, show_pixel_gallery, install_skills,
            search_memory,
            run_scorecard, run_crawl, run_report, run_competitor,
            run_sitemap, run_schema_gen, run_track, run_backlinks,
            run_content_analyze, run_monitor,
            run_theme, run_tui_mode,
        )
        from seo_swarm.skills.loader import SkillLoader

        def _list_skills(args):
            loader = SkillLoader()
            loader.list_skills(getattr(args, 'search', None))

        return {
            "audit":            run_audit,
            "agent":            run_agent,
            "browser":          run_browser,
            "swarm":            run_swarm,
            "dashboard":        show_dashboard,
            "agents":           show_agents,
            "portrait":         show_portrait,
            "pixel-gallery":    show_pixel_gallery,
            "install-skills":   install_skills,
            "skills":           _list_skills,
            "memory":           search_memory,
            "scorecard":        run_scorecard,
            "crawl":            run_crawl,
            "report":           run_report,
            "competitor":       run_competitor,
            "sitemap":          run_sitemap,
            "schema":           run_schema_gen,
            "track":            run_track,
            "backlinks":        run_backlinks,
            "content-analyze":  run_content_analyze,
            "monitor":          run_monitor,
        }

    # ── Theme ───────────────────────────────────────────────────────────────

    def _refresh_theme_colors(self):
        """Cache theme colour codes for prompt and UI elements."""
        tm = self._theme_manager
        self._c_prompt  = tm.color("primary")
        self._c_accent  = tm.color("accent")
        self._c_heading = tm.color("heading")
        self._c_success = tm.color("success")
        self._c_warning = tm.color("warning")
        self._c_error   = tm.color("error")
        self._c_info    = tm.color("info")
        self._c_muted   = tm.color("muted")
        self._c_hlight  = tm.color("highlight")

    def _handle_theme(self, args: Args):
        """Switch theme from REPL, then refresh cached colours."""
        name = getattr(args, 'name', None) or getattr(args, 'raw', '').strip()
        if not name or name == 'list':
            # List themes
            print(f"\n  {self._c_heading}Available Themes:{COLORS['reset']}")
            for tname in self._theme_manager.list_themes():
                marker = " (active)" if tname == self._theme_manager.current.name else ""
                print(f"    {COLORS['bright_cyan']}●{COLORS['reset']} {tname}{COLORS['dim']}{marker}{COLORS['reset']}")
            print()
            return

        try:
            self._theme_manager.apply(name)
            self._theme_manager.save()
            self._refresh_theme_colors()
            print(f"  {self._c_success}✦ Theme switched to: {name}{COLORS['reset']}")
        except ValueError as e:
            print(f"  {self._c_error}{e}{COLORS['reset']}")

    # ── Display helpers ─────────────────────────────────────────────────────

    def _show_welcome(self):
        """Compact welcome screen with key shortcuts."""
        self._clear_screen()

        # Mini banner
        print()
        print(COLORS["bright_cyan"] + COLORS["bold"] + "  ╔" + "═" * 55 + "╗" + COLORS["reset"])
        print(COLORS["bright_cyan"] + COLORS["bold"] + "  ║" + COLORS["reset"] +
              COLORS["bright_yellow"] + COLORS["bold"] +
              "   🐝  S E O   S W A R M   R E P L  🐝" +
              COLORS["reset"] +
              COLORS["bright_cyan"] + COLORS["bold"] + "    ║" + COLORS["reset"])
        print(COLORS["bright_cyan"] + COLORS["bold"] + "  ║" + COLORS["reset"] +
              COLORS["dim"] + "    10 Autonomous SEO Agents — Interactive CLI" +
              COLORS["reset"] +
              COLORS["bright_cyan"] + COLORS["bold"] + "    ║" + COLORS["reset"])
        print(COLORS["bright_cyan"] + COLORS["bold"] + "  ╚" + "═" * 55 + "╝" + COLORS["reset"])
        print()

        # Key commands
        c = COLORS
        print(f"  {c['bright_cyan']}▸ Quick Start{c['reset']}")
        print(f"    {c['bright_yellow']}audit <url>{c['reset']}      Run full SEO audit")
        print(f"    {c['bright_yellow']}swarm <url>{c['reset']}      Run all 10 agents in parallel")
        print(f"    {c['bright_yellow']}dashboard{c['reset']}         Open interactive dashboard")
        print()
        print(f"  {c['bright_cyan']}▸ Shortcuts{c['reset']}")
        print(f"    {c['dim']}a{c['reset']} = audit   {c['dim']}s{c['reset']} = swarm   {c['dim']}d{c['reset']} = dashboard")
        print(f"    {c['dim']}h{c['reset']} = help    {c['dim']}q{c['reset']} = quit    {c['dim']}?{c['reset']} = help")
        print()
        print(f"  {c['bright_cyan']}▸ Slash Commands{c['reset']}")
        print(f"    {c['dim']}/audit /swarm /scorecard /crawl /report /competitor{c['reset']}")
        print(f"    {c['dim']}/sitemap /schema /track /backlinks /content /monitor{c['reset']}")
        print(f"    {c['dim']}/agents /pixel /portrait /theme /help /exit /clear{c['reset']}")
        print()
        print(f"  {c['dim']}Type /help for all commands | Ctrl+C interrupt | Ctrl+D exit{c['reset']}")
        print()

    def _show_help(self):
        """Display styled help with sections grouped by category."""
        c = COLORS
        width = 60

        print()
        print(c["bright_cyan"] + c["bold"] + "  " + "─" * width + c["reset"])
        print(c["bright_yellow"] + c["bold"] + "  SEO SWARM — Command Reference" + c["reset"])
        print(c["bright_cyan"] + c["bold"] + "  " + "─" * width + c["reset"])
        print()

        # ── Core ──
        print(f"  {c['bright_white']}{c['bold']}Core Commands{c['reset']}")
        for slash, (desc, _) in SLASH_COMMANDS.items():
            if slash in ("/audit", "/swarm", "/dashboard", "/agents",
                         "/report", "/scorecard", "/crawl"):
                print(f"    {c['bright_cyan']}{slash:<18}{c['reset']} {c['dim']}{desc}{c['reset']}")

        print()
        print(f"  {c['bright_white']}{c['bold']}Advanced Analysis{c['reset']}")
        for slash, (desc, _) in SLASH_COMMANDS.items():
            if slash in ("/competitor", "/sitemap", "/schema", "/track",
                         "/backlinks", "/content", "/monitor", "/memory"):
                print(f"    {c['bright_cyan']}{slash:<18}{c['reset']} {c['dim']}{desc}{c['reset']}")

        print()
        print(f"  {c['bright_white']}{c['bold']}UI & Meta{c['reset']}")
        for slash, (desc, _) in SLASH_COMMANDS.items():
            if slash in ("/theme", "/pixel", "/portrait", "/help",
                         "/exit", "/quit", "/clear", "/stats",
                         "/banner", "/version", "/history"):
                print(f"    {c['bright_cyan']}{slash:<18}{c['reset']} {c['dim']}{desc}{c['reset']}")

        print()
        print(f"  {c['bright_white']}{c['bold']}Shortcuts{c['reset']}")
        shortcuts_display = [
            ("a", "audit"), ("s", "swarm"), ("d", "dashboard"),
            ("ag", "agents"), ("sc", "scorecard"), ("cr", "crawl"),
            ("rp", "report"), ("cp", "competitor"), ("sm", "sitemap"),
            ("sh", "schema"), ("tr", "track"), ("bl", "backlinks"),
            ("ca", "content-analyze"), ("mn", "monitor"),
            ("th", "theme"), ("pg", "pixel-gallery"), ("pt", "portrait"),
            ("mm", "memory"),
            ("h", "help"), ("q/x", "exit"), ("?", "help"),
        ]
        for shortcut, target in shortcuts_display:
            print(f"    {c['bright_yellow']}{shortcut:<6}{c['reset']} →  {c['dim']}{target}{c['reset']}")

        print()
        print(f"  {c['dim']}All commands also work in natural language: "
              f"'audit https://example.com'{c['reset']}")
        print()

        # ── Navigation tips ──
        print(f"  {c['bright_white']}{c['bold']}Navigation{c['reset']}")
        print(f"    {c['dim']}Ctrl+C{c['reset']}  Interrupt / cancel current command")
        print(f"    {c['dim']}Ctrl+D{c['reset']}  Exit REPL (or type /exit, /quit, q)")
        print(f"    {c['dim']}↑↓{c['reset']}      Browse command history (if available)")
        print(f"    {c['dim']}/clear{c['reset']}   Clear screen")
        print()

    def _show_stats(self):
        """Display REPL session statistics."""
        import time as _time
        c = COLORS
        uptime = _time.time() - self._startup_time if self._startup_time else 0
        mins, secs = divmod(int(uptime), 60)

        print()
        print(f"  {c['bright_cyan']}{c['bold']}REPL Session Stats{c['reset']}")
        print(f"  {c['dim']}{'─' * 40}{c['reset']}")
        print(f"  Commands run:    {self._command_count}")
        print(f"  Errors:          {self._error_count}")
        print(f"  Uptime:          {mins}m {secs}s")
        print(f"  Theme:           {self._theme_manager.current.name}")

        # Agent stats
        registry = AgentRegistry()
        print(f"  Agents loaded:   {registry.count()}")
        print()

    def _show_version(self):
        """Show version information."""
        from seo_swarm import __version__, __author__
        c = COLORS
        print()
        print(f"  {c['bright_cyan']}SEO SWARM{c['reset']} v{__version__}")
        print(f"  {c['dim']}By {__author__}{c['reset']}")
        print(f"  {c['dim']}Python {sys.version.split()[0]} | "
              f"{'readline' if _HAS_READLINE else 'no readline'}{c['reset']}")
        print()

    def _show_history(self):
        """Show recent command history (if readline available)."""
        if not _HAS_READLINE:
            print(f"  {COLORS['dim']}Command history not available "
                  f"(readline not installed){COLORS['reset']}")
            return

        try:
            length = readline.get_current_history_length()
            if length == 0:
                print(f"  {COLORS['dim']}No commands in history yet.{COLORS['reset']}")
                return

            print()
            print(f"  {COLORS['bright_cyan']}{COLORS['bold']}Command History "
                  f"({length} entries){COLORS['reset']}")
            print(f"  {COLORS['dim']}{'─' * 40}{COLORS['reset']}")
            for i in range(1, length + 1):
                entry = readline.get_history_item(i)
                if entry:
                    print(f"    {COLORS['dim']}{i:>3}{COLORS['reset']}  {entry}")
            print()
        except Exception:
            print(f"  {COLORS['dim']}Could not read history.{COLORS['reset']}")

    def _clear_screen(self):
        """Clear terminal screen cross-platform."""
        os.system("cls" if os.name == "nt" else "clear")

    # ── History ─────────────────────────────────────────────────────────────

    def _setup_history(self):
        """Initialise readline history and load from file."""
        if not _HAS_READLINE:
            return

        # Set history file
        try:
            readline.read_history_file(self._history_file)
        except (FileNotFoundError, OSError):
            pass

    def _save_history(self, line: str):
        """Append one line to in-memory (and optionally on-disk) history."""
        if not _HAS_READLINE:
            return

        # Avoid saving empty or whitespace-only
        if not line.strip():
            return

        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self._history_file), exist_ok=True)
            readline.write_history_file(self._history_file)
        except (OSError, IOError):
            pass  # Non-essential; don't crash on history failure

    # ── Error handling ──────────────────────────────────────────────────────

    def _print_error(self, exc: Exception):
        """Print a user-friendly error without a full traceback."""
        msg = str(exc) or type(exc).__name__
        print(f"\n  {COLORS['bright_red']}✖ Error:{COLORS['reset']} {msg}")
        # Optionally show traceback in verbose mode
        if os.environ.get("SEO_SWARM_DEBUG"):
            traceback.print_exc()
        print()

    # ── Fuzzy matching ──────────────────────────────────────────────────────

    def _fuzzy_match(self, candidate: str) -> Optional[str]:
        """Return the closest known command if candidate is within edit distance 2."""
        all_commands = set(NATURAL_COMMANDS.keys()) | set(SHORTCUTS.keys())
        best = None
        best_dist = 999

        for cmd in all_commands:
            dist = self._levenshtein(candidate, cmd)
            if dist < best_dist and dist <= 2:
                best_dist = dist
                best = cmd

        return best

    @staticmethod
    def _levenshtein(a: str, b: str) -> int:
        """Compute Levenshtein edit distance between two strings."""
        if len(a) < len(b):
            return SwarmREPL._levenshtein(b, a)
        if len(b) == 0:
            return len(a)

        prev = list(range(len(b) + 1))
        for i, ca in enumerate(a):
            curr = [i + 1]
            for j, cb in enumerate(b):
                curr.append(min(
                    prev[j + 1] + 1,      # deletion
                    curr[j] + 1,           # insertion
                    prev[j] + (ca != cb),  # substitution
                ))
            prev = curr
        return prev[-1]

    # ── Shutdown ────────────────────────────────────────────────────────────

    def _shutdown(self):
        """Clean exit with goodbye message and history save."""
        self._running = False
        if _HAS_READLINE:
            try:
                readline.write_history_file(self._history_file)
            except (OSError, IOError):
                pass

        print()
        print(f"  {COLORS['bright_yellow']}🐝  SEO SWARM signing off. "
              f"Goodbye!{COLORS['reset']}")
        print()


# ══════════════════════════════════════════════════════════════════════════════
# Module-level convenience entry point
# ══════════════════════════════════════════════════════════════════════════════

def run_repl():
    """Launch the interactive SEO SWARM REPL."""
    SwarmREPL().run()


# ══════════════════════════════════════════════════════════════════════════════
# Smoke test / direct invocation
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    run_repl()
