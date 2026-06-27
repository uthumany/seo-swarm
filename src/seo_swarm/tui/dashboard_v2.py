"""
SEO SWARM - Dashboard V2 (Next-Gen Terminal UI)
================================================
Complete redesign using the new layout engine, status bar,
and responsive terminal components. Pure ANSI escape codes.
"""

import sys
import os
import time
import shutil
from typing import Dict, Any, List, Optional

from .layout import Layout, Columns, FlexRow, StatusBar, render_bar, render_spinner, _strip_ansi


# ═══════════════════════════════════════════════════════════════════════════════
# THEME
# ═══════════════════════════════════════════════════════════════════════════════

THEMES = {
    "default": {
        "primary":         "\033[96m",   # bright cyan
        "secondary":       "\033[94m",   # bright blue
        "accent":          "\033[93m",   # bright yellow
        "success":         "\033[92m",   # bright green
        "error":           "\033[91m",   # bright red
        "warning":         "\033[93m",   # bright yellow
        "info":            "\033[96m",   # bright cyan
        "dim":             "\033[90m",   # bright black
        "bold":            "\033[1m",
        "reset":           "\033[0m",
        "header_color":    "\033[96m",   # bright cyan
        "border_color":    "\033[90m",   # dim
        "status_bar_color":"\033[90m",
        "bg":              "",
    },
    "dark": {
        "primary":         "\033[36m",
        "secondary":       "\033[34m",
        "accent":          "\033[33m",
        "success":         "\033[32m",
        "error":           "\033[31m",
        "warning":         "\033[33m",
        "info":            "\033[36m",
        "dim":             "\033[2m",
        "bold":            "\033[1m",
        "reset":           "\033[0m",
        "header_color":    "\033[36m",
        "border_color":    "\033[2m",
        "status_bar_color":"\033[2m",
        "bg":              "",
    },
    "cyberpunk": {
        "primary":         "\033[95m",   # bright magenta
        "secondary":       "\033[96m",   # bright cyan
        "accent":          "\033[93m",
        "success":         "\033[92m",
        "error":           "\033[91m",
        "warning":         "\033[93m",
        "info":            "\033[94m",
        "dim":             "\033[90m",
        "bold":            "\033[1m",
        "reset":           "\033[0m",
        "header_color":    "\033[95m",
        "border_color":    "\033[90m",
        "status_bar_color":"\033[90m",
        "bg":              "\033[45m",
    },
}


def _resolve_theme():
    """Resolve theme from environment or config, fallback to 'default'."""
    env_theme = os.environ.get("SEO_SWARM_THEME", "").lower()
    if env_theme in THEMES:
        return THEMES[env_theme]
    # Could read from config file in the future
    return THEMES["default"]


# ═══════════════════════════════════════════════════════════════════════════════
# SEVERITY / STATUS HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

SEVERITY_ICONS = {
    "high":     "🔴",
    "medium":   "🟡",
    "low":      "🟢",
    "info":     "🔵",
    "critical": "⛔",
}

SEVERITY_COLORS = {
    "high":     "error",
    "medium":   "warning",
    "low":      "success",
    "info":     "info",
    "critical": "error",
}

AGENT_STATUS_ICONS = {
    "idle":     "○",
    "running":  "◐",
    "complete": "●",
    "error":    "✗",
    "paused":   "⏸",
}

AGENT_STATUS_COLORS = {
    "idle":     "dim",
    "running":  "accent",
    "complete": "success",
    "error":    "error",
    "paused":   "warning",
}


def _agent_icon(status: str) -> str:
    return AGENT_STATUS_ICONS.get(status, "?")


def _severity_color(theme: dict, severity: str) -> str:
    color_key = SEVERITY_COLORS.get(severity, "dim")
    return theme.get(color_key, theme["dim"])


def _grade_color(theme: dict, grade: str) -> str:
    first = grade[0] if grade else "C"
    if first == "A":
        return theme["success"]
    elif first == "B":
        return theme["info"]
    elif first == "C":
        return theme["accent"]
    else:
        return theme["error"]


# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD V2
# ═══════════════════════════════════════════════════════════════════════════════

class DashboardV2:
    """Next-gen terminal dashboard with layout engine, status bar, and themes.

    Usage:
        db = DashboardV2()
        db.show()
        db.show_loading("Running audit...")
        db.show_audit_results(results)
        db.show_help_overlay()
    """

    def __init__(self, theme_name: str = None):
        self.theme = _resolve_theme()
        if theme_name and theme_name in THEMES:
            self.theme = THEMES[theme_name]

        self._status_bar = StatusBar(theme_color=self.theme["status_bar_color"])
        self._version = self._detect_version()
        self._term_width = shutil.get_terminal_size((80, 24)).columns

    @staticmethod
    def _detect_version() -> str:
        try:
            import seo_swarm
            return getattr(seo_swarm, '__version__', '?.?.?')
        except Exception:
            return '?.?.?'

    # ── Common rendering helpers ───────────────────────────────────────────────

    def _header(self, title: str = "SEO SWARM DASHBOARD") -> str:
        """Render the SEO SWARM banner header."""
        t = self.theme
        r = t["reset"]
        w = self._term_width
        bee = "🐝"
        line = t["header_color"] + t["bold"] + "═" * w + r
        padded_title = f"  {bee} {title} {bee}"
        title_line = t["accent"] + t["bold"] + padded_title.center(w) + r
        return f"{line}\n{title_line}\n{line}"

    def _divider(self, char: str = "─") -> str:
        t = self.theme
        return t["border_color"] + char * self._term_width + t["reset"]

    def _section_title(self, text: str) -> str:
        t = self.theme
        return f"  {t['bold']}{t['secondary']}{text}{t['reset']}"

    def _refresh_term_width(self):
        """Refresh terminal width from the environment."""
        self._term_width = shutil.get_terminal_size((80, 24)).columns

    def clear_screen(self):
        """Clear terminal screen and reset cursor."""
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()

    # ── Main Dashboard ────────────────────────────────────────────────────────

    def show(self):
        """Render the main interactive dashboard."""
        self._refresh_term_width()
        self.clear_screen()

        t = self.theme
        r = t["reset"]
        w = self._term_width

        # Header
        print(self._header())
        print()

        # Main content: two-column layout (60/40 split)
        cols = Columns(widths=[0.6, 0.4], gap=3)
        cols.add_column(self._render_agent_panel(), wrap=False)
        cols.add_column(self._render_side_panel(), wrap=True)
        print(cols.render(w))
        print()

        # Quick commands
        print(self._section_title("⚡ QUICK COMMANDS"))
        print(self._divider())
        cmds = [
            ("audit <url>",     "Full SEO audit"),
            ("swarm <url>",     "All agents in parallel"),
            ("agent <name>",    "Run specific agent"),
            ("scorecard <url>", "SEO scorecard (0-100)"),
            ("dashboard",       "This dashboard"),
            ("help",            "Show help overlay"),
        ]
        for cmd, desc in cmds:
            print(f"  {t['primary']}{cmd:<22}{r} {t['dim']}{desc}{r}")

        print()
        # Status bar at bottom
        self._status_bar.set_left(f"SEO SWARM {self._version}")
        self._status_bar.set_center("Dashboard Ready")
        self._status_bar.set_right("Press Ctrl+C to exit")
        print(self._status_bar.render(w))

    def _render_agent_panel(self) -> str:
        """Build the left agent status panel (returns raw string)."""
        t = self.theme
        r = t["reset"]

        try:
            from seo_swarm.agents.registry import AgentRegistry
            agents = AgentRegistry().get_all()
        except Exception:
            agents = []

        lines = [f"  {t['bold']}{t['secondary']}🤖 AGENTS ({len(agents)}){r}",
                 f"  {t['border_color']}{'─' * 50}{r}"]

        for agent in agents:
            icon = _agent_icon(agent.status)
            color_key = AGENT_STATUS_COLORS.get(agent.status, "dim")
            sc = t.get(color_key, t["dim"])
            ac = t.get(agent.color, t["primary"])
            lines.append(
                f"  {sc}{icon}{r}  {ac}{agent.emoji} {agent.name:<28}{r}"
            )

        if not agents:
            lines.append(f"  {t['dim']}No agents loaded.{r}")

        return '\n'.join(lines)

    def _render_side_panel(self) -> str:
        """Build the right side panel (quick stats + activity)."""
        t = self.theme
        r = t["reset"]

        lines = [f"  {t['bold']}{t['secondary']}📊 QUICK STATS{r}",
                 f"  {t['border_color']}{'─' * 40}{r}",
                 f"  {t['success']}●{r} Agents:          10",
                 f"  {t['info']}●{r} Skills:          25+",
                 f"  {t['accent']}●{r} Plugins:         10",
                 f"  {t['primary']}●{r} Memory:         Active",
                 f"  {t['secondary']}●{r} Theme:          {os.environ.get('SEO_SWARM_THEME', 'default')}",
                 "",
                 f"  {t['bold']}{t['secondary']}📋 RECENT ACTIVITY{r}",
                 f"  {t['border_color']}{'─' * 40}{r}",
                 f"  {t['dim']}No recent activity{r}",
                 f"  {t['dim']}Run an audit to start{r}",
        ]

        return '\n'.join(lines)

    # ── Audit Results ─────────────────────────────────────────────────────────

    def show_audit_results(self, results: Dict[str, Any]):
        """Render styled audit results with scorecard, icons, and severity indicators."""
        self._refresh_term_width()
        self.clear_screen()

        t = self.theme
        r = t["reset"]
        w = self._term_width

        target = results.get("target", "unknown")
        agent_results = results.get("results", [])
        total_findings = results.get("total_findings", 0)

        # Header
        print(self._header(f"AUDIT RESULTS"))
        print()
        print(f"  {t['bold']}Target:{r} {t['success']}{target}{r}")
        print(f"  {t['bold']}Findings:{r} {t['accent']}{total_findings}{r}")
        print()

        # Agent results table
        if agent_results:
            print(self._section_title("🔍 AGENT FINDINGS"))
            print(self._divider())

            for i, ares in enumerate(agent_results):
                agent_name = ares.get("agent_name", f"Agent {i+1}")
                status = ares.get("status", "unknown")
                score = ares.get("score", 0)
                duration = ares.get("duration", 0)
                color_key = AGENT_STATUS_COLORS.get(status, "dim")
                sc = t.get(color_key, t["dim"])

                status_icon = "●" if status == "success" else "✗"
                bar = render_bar(score, width=15, color=t["accent"])
                print(f"  {sc}{status_icon}{r}  {t['bold']}{agent_name:<28}{r}  "
                      f"{bar}  {t['dim']}{duration:.1f}s{r}")

                findings = ares.get("findings", [])
                for f in findings:
                    sev = f.get("severity", "info")
                    cat = f.get("category", "general")
                    text = f.get("finding", "")
                    sev_icon = SEVERITY_ICONS.get(sev, "●")
                    sev_col = _severity_color(t, sev)
                    print(f"       {sev_icon} {sev_col}[{sev.upper()}]{r} "
                          f"{t['dim']}[{cat}]{r} {text}")

                if i < len(agent_results) - 1:
                    print(f"  {t['border_color']}{'·' * 60}{r}")

            print()

        # Summary footer
        agents_used = results.get("agents_used", len(agent_results))
        print(self._divider())
        print(f"  {t['bold']}Agents Used:{r} {agents_used}  |  "
              f"{t['bold']}Findings:{r} {total_findings}")
        print()

        # Status bar
        self._status_bar.set_left(f"SEO SWARM {self._version}")
        self._status_bar.set_center(f"Audit: {target[:30]}")
        self._status_bar.set_right(f"Findings: {total_findings}")
        print(self._status_bar.render(w))

    # ── Scorecard Results ─────────────────────────────────────────────────────

    def show_scorecard(self, scorecard):
        """Render a styled SEO scorecard."""
        self._refresh_term_width()
        self.clear_screen()

        t = self.theme
        r = t["reset"]
        w = self._term_width

        print(self._header("SEO SCORECARD"))
        print()

        target = getattr(scorecard, 'target_url', 'Unknown')
        total = getattr(scorecard, 'total_score', 0)
        grade = getattr(scorecard, 'grade', 'N/A')
        dims = getattr(scorecard, 'dimensions', [])
        recs = getattr(scorecard, 'total_recommendations', 0)

        print(f"  {t['bold']}URL:{r}    {t['info']}{target}{r}")
        print(f"  {t['bold']}Score:{r}  {_grade_color(t, grade)}{total:.1f}/100 "
              f" {t['bold']}Grade:{r} {_grade_color(t, grade)}{grade}{r}")
        print()

        if dims:
            print(self._section_title("📈 DIMENSIONS"))
            print(self._divider())
            for d in dims:
                name = getattr(d, 'name', 'Unknown')
                score = getattr(d, 'score', 0)
                status = getattr(d, 'status', 'fair')
                bar = render_bar(score, width=25)
                print(f"  {name:<20} {bar}  {t['accent']}[{status.upper()}]{r}")

        print()

        if recs > 0:
            print(self._section_title(f"💡 RECOMMENDATIONS ({recs})"))
            print(self._divider())
            for d in dims:
                for rec in getattr(d, 'recommendations', [])[:2]:
                    print(f"  {t['accent']}▶{r} {rec}")
            print()

        print(self._divider())
        self._status_bar.set_left(f"SEO SWARM {self._version}")
        self._status_bar.set_center(f"Scorecard: {grade}")
        self._status_bar.set_right(f"{total:.0f}/100")
        print(self._status_bar.render(w))

    # ── Swarm Results ─────────────────────────────────────────────────────────

    def show_swarm_results(self, results: Dict[str, Any]):
        """Render swarm mode results."""
        self._refresh_term_width()
        self.clear_screen()

        t = self.theme
        r = t["reset"]
        w = self._term_width

        print(self._header("🐝 SWARM MODE"))
        print()

        print(f"  {t['accent']}All agents run in parallel — combined results below.{r}")
        print()
        self.show_audit_results(results)

    # ── Competitor Analysis ───────────────────────────────────────────────────

    def show_competitor(self, report):
        """Render a competitor analysis report."""
        self._refresh_term_width()
        self.clear_screen()

        t = self.theme
        r = t["reset"]
        w = self._term_width

        print(self._header("COMPETITOR ANALYSIS"))
        print()

        target = getattr(report, 'target', 'Unknown')
        competitors = getattr(report, 'competitors', [])
        gaps = getattr(report, 'gaps', {})

        print(f"  {t['bold']}Target:{r} {t['info']}{target}{r}")
        print()

        for comp in competitors:
            url = getattr(comp, 'url', 'Unknown')
            title = getattr(comp, 'title', '')
            desc = getattr(comp, 'description', '')
            wc = getattr(comp, 'word_count', 0)
            headers = getattr(comp, 'headers', {})
            gap_count = len(gaps.get(url, []))

            print(f"  {t['bold']}{t['accent']}▶ {url}{r}")
            print(f"    {t['dim']}Title:     {title[:55]}{r}")
            print(f"    {t['dim']}Meta:      {desc[:55]}{r}")
            if headers:
                print(f"    {t['dim']}H1:        {headers.get('h1', ['N/A'])[0][:50]}{r}")
            print(f"    {t['dim']}Words:     {wc}  |  Gaps: {gap_count}{r}")
            print()

        self._status_bar.set_left(f"SEO SWARM {self._version}")
        self._status_bar.set_center(f"Competitors: {len(competitors)}")
        self._status_bar.set_right(f"Target: {target[:20]}")
        print(self._status_bar.render(w))

    # ── Loading Screen ────────────────────────────────────────────────────────

    def show_loading(self, message: str = "Loading..."):
        """Render a full-screen loading state with spinner."""
        self._refresh_term_width()
        self.clear_screen()

        t = self.theme
        r = t["reset"]
        w = self._term_width

        print(self._header())
        print()
        print()
        spinner = render_spinner(int(time.time() * 10))
        centered = f"  {spinner}  {t['accent']}{message}{r}  {spinner}"
        print(centered.center(w + _strip_ansi(centered).count('\033') * 5))
        print()
        print()

        self._status_bar.set_left(f"SEO SWARM {self._version}")
        self._status_bar.set_center("Working...")
        self._status_bar.set_right("")
        print(self._status_bar.render(w))

    def show_loading_animated(self, message: str = "Loading...", duration: float = 2.0,
                              interval: float = 0.1):
        """Show an animated loading screen for a given duration."""
        self._refresh_term_width()
        t = self.theme
        r = t["reset"]
        w = self._term_width

        frames = int(duration / interval)
        for i in range(frames):
            self.clear_screen()
            print(self._header())
            print()
            print()
            spinner = render_spinner(i)
            centered = f"  {spinner}  {t['accent']}{message}{r}  {spinner}"
            print(centered.center(w))
            print()
            print()

            self._status_bar.set_left(f"SEO SWARM {self._version}")
            self._status_bar.set_center(f"Progress: {i+1}/{frames}")
            self._status_bar.set_right("")
            print(self._status_bar.render(w))
            sys.stdout.flush()
            time.sleep(interval)

    # ── Error Display ─────────────────────────────────────────────────────────

    def show_error(self, message: str, details: str = ""):
        """Render a styled error display."""
        self._refresh_term_width()
        self.clear_screen()

        t = self.theme
        r = t["reset"]
        w = self._term_width

        print(self._header("ERROR"))
        print()
        print()

        # Error box
        box_w = min(70, w - 4)
        print(f"  {t['error']}┌{'─' * box_w}┐{r}")
        print(f"  {t['error']}│{r} {t['bold']}{t['error']}⛔ ERROR{r}".ljust(
            box_w + _strip_ansi(f"│ ⛔ ERROR").count('\033') * 2) + f"{t['error']}│{r}")
        print(f"  {t['error']}├{'─' * box_w}┤{r}")

        # Word-wrap the message
        msg = message
        while msg:
            chunk = msg[:box_w - 2]
            msg = msg[box_w - 2:]
            print(f"  {t['error']}│{r} {t['dim']}{chunk}{r}".ljust(box_w + 4) + f"{t['error']}│{r}")

        if details:
            print(f"  {t['error']}│{r} {t['dim']}{details[:box_w - 2]}{r}".ljust(box_w + 4) + f"{t['error']}│{r}")

        print(f"  {t['error']}└{'─' * box_w}┘{r}")
        print()
        print()
        print(f"  {t['dim']}Press Ctrl+C to exit, or run another command.{r}")

        self._status_bar.set_left(f"SEO SWARM {self._version}")
        self._status_bar.set_center("ERROR")
        self._status_bar.set_right("✗")
        print()
        print(self._status_bar.render(w))

    # ── Empty State ───────────────────────────────────────────────────────────

    def show_empty(self, message: str = "Nothing here yet"):
        """Render an empty state placeholder."""
        self._refresh_term_width()
        self.clear_screen()

        t = self.theme
        r = t["reset"]
        w = self._term_width

        print(self._header())
        print()
        print()

        # Empty state box
        box_w = min(50, w - 4)
        box_h = 5
        print(f"  {t['border_color']}┌{'─' * box_w}┐{r}")
        for i in range(box_h):
            if i == box_h // 2:
                centered = f"  {t['dim']}📭  {message}{r}"
                print(f"  {t['border_color']}│{r} {centered.center(box_w - 2)} {t['border_color']}│{r}")
            else:
                print(f"  {t['border_color']}│{r}{' ' * (box_w + 2)}{t['border_color']}│{r}")
        print(f"  {t['border_color']}└{'─' * box_w}┘{r}")

        print()
        print()
        print(f"  {t['dim']}Use 'seo-swarm audit <url>' to get started.{r}")

        self._status_bar.set_left(f"SEO SWARM {self._version}")
        self._status_bar.set_center(message)
        self._status_bar.set_right("")
        print()
        print(self._status_bar.render(w))

    # ── Help Overlay ──────────────────────────────────────────────────────────

    def show_help_overlay(self):
        """Render a keyboard shortcut help overlay."""
        self._refresh_term_width()
        self.clear_screen()

        t = self.theme
        r = t["reset"]
        w = self._term_width

        print(self._header("HELP"))
        print()

        print(self._section_title("⌨️  KEYBOARD SHORTCUTS"))
        print(self._divider())

        shortcuts = [
            ("q / Ctrl+C",   "Quit application"),
            ("d",             "Toggle dashboard"),
            ("a",             "Run audit"),
            ("s",             "Show scorecard"),
            ("h / ?",         "This help overlay"),
            ("r",             "Refresh / recalculate"),
            ("c",             "Competitor analysis"),
            ("l",             "Loading screen demo"),
            ("e",             "Error screen demo"),
            ("m",             "Empty state demo"),
        ]
        for key, desc in shortcuts:
            print(f"  {t['accent']}{key:<18}{r} {t['dim']}{desc}{r}")

        print()
        print(self._section_title("📋 COMMANDS"))
        print(self._divider())

        commands = [
            ("seo-swarm audit <url>",       "Run full SEO audit on a target URL"),
            ("seo-swarm swarm <url>",       "Run all 10 agents in parallel mode"),
            ("seo-swarm agent <name>",      "Run a specific agent"),
            ("seo-swarm scorecard <url>",   "Generate 0-100 SEO scorecard"),
            ("seo-swarm crawl <url>",       "Crawl a website for SEO data"),
            ("seo-swarm report <url>",      "Generate SEO audit report (HTML/MD)"),
            ("seo-swarm competitor <url>",  "Compare against competitor URLs"),
            ("seo-swarm track <keyword>",   "Keyword rank tracking"),
            ("seo-swarm backlinks <domain>","Analyze backlink profile"),
            ("seo-swarm monitor <url>",     "SEO health monitoring"),
            ("seo-swarm dashboard",         "Interactive terminal dashboard"),
            ("seo-swarm agents",            "List all available agents"),
        ]
        for cmd, desc in commands:
            print(f"  {t['primary']}{cmd:<34}{r} {t['dim']}{desc}{r}")

        print()
        print(self._section_title("🎨 THEMES"))
        print(self._divider())
        print(f"  Set {t['accent']}SEO_SWARM_THEME{r} env var: "
              f"{t['dim']}default, dark, cyberpunk{r}")
        print()

        print(self._divider())

        self._status_bar.set_left(f"SEO SWARM {self._version}")
        self._status_bar.set_center("Help — Press q to close")
        self._status_bar.set_right(f"Theme: {os.environ.get('SEO_SWARM_THEME', 'default')}")
        print()
        print(self._status_bar.render(w))

    # ── Demo / Interactive ────────────────────────────────────────────────────

    def run_demo(self):
        """Run a demo sequence showing all screens."""
        self._refresh_term_width()

        self.show()
        input("\n  Press Enter for loading screen...")

        self.show_loading("Running SEO audit on example.com")
        time.sleep(2)

        # Simulated audit results
        fake_results = {
            "target": "https://example.com",
            "total_findings": 12,
            "agents_used": 5,
            "results": [
                {
                    "agent_name": "Technical SEO Specialist",
                    "status": "success",
                    "score": 92.5,
                    "duration": 1.23,
                    "findings": [
                        {"severity": "high", "category": "crawlability",
                         "finding": "Missing canonical tags on 3 pages"},
                        {"severity": "medium", "category": "performance",
                         "finding": "LCP exceeds 2.5s threshold"},
                    ]
                },
                {
                    "agent_name": "Content SEO Specialist",
                    "status": "success",
                    "score": 78.0,
                    "duration": 0.95,
                    "findings": [
                        {"severity": "low", "category": "meta",
                         "finding": "Meta descriptions too short on 5 pages"},
                        {"severity": "info", "category": "headings",
                         "finding": "Multiple H1 tags detected"},
                    ]
                },
                {
                    "agent_name": "Off-Page SEO Specialist",
                    "status": "error",
                    "score": 45.0,
                    "duration": 2.10,
                    "findings": [
                        {"severity": "high", "category": "backlinks",
                         "finding": "Only 12 referring domains detected"},
                    ]
                },
            ]
        }

        self.show_audit_results(fake_results)
        input("\n  Press Enter for help overlay...")

        self.show_help_overlay()
        input("\n  Press Enter for error demo...")

        self.show_error("Connection to example.com timed out after 30 seconds.",
                        details="The server may be down or blocking requests. Try again later.")
        input("\n  Press Enter for empty state...")

        self.show_empty("No audit history yet")
        input("\n  Press Enter to finish demo...")

        self.show()
        print()
        print(f"  {THEMES['default']['success']}✓ Demo complete!{THEMES['default']['reset']}")


# ═══════════════════════════════════════════════════════════════════════════════
# BACKWARD COMPATIBILITY ALIAS
# ═══════════════════════════════════════════════════════════════════════════════

class LegacyTerminalDashboard(DashboardV2):
    """Drop-in replacement for TerminalDashboard using the V2 engine.

    This ensures existing calls like `TerminalDashboard().show()` still work
    but render with the new layout engine.
    """

    def render_audit_results(self, results):
        self.show_audit_results(results)

    def render_swarm_results(self, results):
        self.show_swarm_results(results)

    def render_scorecard(self, scorecard):
        self.show_scorecard(scorecard)

    def render_competitor(self, report):
        self.show_competitor(report)


# Alias for seamless drop-in
TerminalDashboardV2 = LegacyTerminalDashboard
