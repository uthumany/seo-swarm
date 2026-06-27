"""
SEO SWARM - Terminal UI Dashboard
Rich terminal dashboard with ASCII art, colors, and progress indicators.
"""

import sys
import time
import random
from typing import Dict, Any, List

# ANSI color codes
COLORS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "italic": "\033[3m",
    "underline": "\033[4m",
    "black": "\033[30m", "red": "\033[31m", "green": "\033[32m",
    "yellow": "\033[33m", "blue": "\033[34m", "magenta": "\033[35m",
    "cyan": "\033[36m", "white": "\033[37m",
    "bright_black": "\033[90m", "bright_red": "\033[91m", "bright_green": "\033[92m",
    "bright_yellow": "\033[93m", "bright_blue": "\033[94m", "bright_magenta": "\033[95m",
    "bright_cyan": "\033[96m", "bright_white": "\033[97m",
    "bg_black": "\033[40m", "bg_red": "\033[41m", "bg_green": "\033[42m",
    "bg_yellow": "\033[43m", "bg_blue": "\033[44m", "bg_magenta": "\033[45m",
    "bg_cyan": "\033[46m", "bg_white": "\033[47m",
}

STATUS_ICONS = {
    "idle": "  \u25cb  ",      # circle
    "running": "  \u25d0  ",   # half-circle
    "complete": "  \u25cf  ",  # filled circle
    "error": "  \u2717  ",     # x mark
}

STATUS_COLORS = {
    "idle": COLORS["dim"],
    "running": COLORS["bright_yellow"],
    "complete": COLORS["bright_green"],
    "error": COLORS["bright_red"],
}


class TerminalDashboard:
    """Interactive terminal dashboard for SEO Swarm."""

    def __init__(self):
        self.width = 100

    def show(self):
        """Show the main interactive dashboard."""
        self.clear_screen()
        print(COLORS["bright_cyan"] + COLORS["bold"] + "=" * self.width + COLORS["reset"])
        print(COLORS["bright_yellow"] + COLORS["bold"] + "  \U0001f41d SEO SWARM DASHBOARD \U0001f41d" + COLORS["reset"])
        print(COLORS["bright_cyan"] + "=" * self.width + COLORS["reset"])
        print()
        self._show_agent_panel()
        print()
        self._show_stats_panel()
        print()
        self._show_command_panel()

    def render_audit_results(self, results: Dict[str, Any]):
        """Render audit results in terminal."""
        self.clear_screen()
        print(COLORS["bright_cyan"] + COLORS["bold"] + "=" * self.width + COLORS["reset"])
        print(COLORS["bright_green"] + COLORS["bold"] + f"  SEO AUDIT RESULTS: {results['target']}" + COLORS["reset"])
        print(COLORS["bright_cyan"] + "=" * self.width + COLORS["reset"])
        print()

        for i, r in enumerate(results["results"]):
            status_color = COLORS["bright_green"] if r["status"] == "success" else COLORS["bright_red"]
            c = COLORS["reset"]
            print(f"  {status_color}{STATUS_ICONS.get(r['status'], '?')}{c}  "
                  f"{COLORS['bold']}{r['agent_name']:<30}{c}  "
                  f"{COLORS['bright_yellow']}Score: {r['score']:.1f}%{c}  "
                  f"{COLORS['dim']}Duration: {r['duration']:.2f}s{c}")

            for f in r.get("findings", []):
                sev_color = {
                    "high": COLORS["bright_red"],
                    "medium": COLORS["bright_yellow"],
                    "low": COLORS["bright_green"],
                    "info": COLORS["bright_blue"],
                }.get(f["severity"], COLORS["white"])
                print(f"      {sev_color}[{f['severity'].upper()}]{c} [{f['category']}] {f['finding']}")
            print()

        print(COLORS["bright_cyan"] + "-" * self.width + COLORS["reset"])
        print(f"  {COLORS['bold']}Total Findings: {results['total_findings']}{COLORS['reset']}  |  "
              f"Agents Used: {results['agents_used']}")

    def render_swarm_results(self, results: Dict[str, Any]):
        """Render swarm results (same format as audit but with swarm header)."""
        print(COLORS["bright_magenta"] + COLORS["bold"] + "  \U0001f41d SWARM MODE - All agents ran in parallel \U0001f41d" + COLORS["reset"])
        print()
        self.render_audit_results(results)

    def _show_agent_panel(self):
        """Show the agent status panel."""
        from seo_swarm.agents.registry import AgentRegistry
        agents = AgentRegistry().get_all()

        print(f"  {COLORS['bold']}{COLORS['bright_white']}AGENTS ({len(agents)} active){COLORS['reset']}")
        print(f"  {COLORS['dim']}{'-'*70}{COLORS['reset']}")

        for agent in agents:
            c = COLORS.get(agent.color, COLORS["white"])
            icon = STATUS_ICONS.get(agent.status, "  ?  ")
            sc = STATUS_COLORS.get(agent.status, COLORS["dim"])
            print(f"  {sc}{icon}{COLORS['reset']}  "
                  f"{c}{agent.emoji} {agent.name:<30}{COLORS['reset']}  "
                  f"{COLORS['dim']}{agent.role}{COLORS['reset']}")

    def _show_stats_panel(self):
        """Show statistics panel."""
        print(f"  {COLORS['bold']}{COLORS['bright_white']}STATISTICS{COLORS['reset']}")
        print(f"  {COLORS['dim']}{'-'*70}{COLORS['reset']}")
        print(f"  {COLORS['bright_cyan']}\u25cf{COLORS['reset']} Total Agents:      10")
        print(f"  {COLORS['bright_green']}\u25cf{COLORS['reset']} Preloaded Skills:  25+")
        print(f"  {COLORS['bright_yellow']}\u25cf{COLORS['reset']} Browser Plugins:   10")
        print(f"  {COLORS['bright_magenta']}\u25cf{COLORS['reset']} Memory System:     Active")
        print(f"  {COLORS['bright_blue']}\u25cf{COLORS['reset']} Install Methods:    11")

    def _show_command_panel(self):
        """Show available commands."""
        print(f"  {COLORS['bold']}{COLORS['bright_white']}QUICK COMMANDS{COLORS['reset']}")
        print(f"  {COLORS['dim']}{'-'*70}{COLORS['reset']}")
        cmds = [
            ("seo-swarm audit <url>", "Run full SEO audit"),
            ("seo-swarm swarm <url>", "Run all agents in parallel"),
            ("seo-swarm agent <name> --url <url>", "Run specific agent"),
            ("seo-swarm agents --art", "Show ASCII art agent cards"),
            ("seo-swarm install-skills", "Install preloaded skills"),
            ("seo-swarm memory <query>", "Search memory database"),
        ]
        for cmd, desc in cmds:
            print(f"  {COLORS['bright_cyan']}{cmd:<42}{COLORS['reset']} {COLORS['dim']}{desc}{COLORS['reset']}")

    def clear_screen(self):
        """Clear terminal screen."""
        print("\033[2J\033[H", end="")

    def progress_bar(self, current: int, total: int, label: str = "", width: int = 50):
        """Render a progress bar."""
        pct = current / total if total > 0 else 0
        filled = int(width * pct)
        bar = COLORS["bright_green"] + "\u2588" * filled + COLORS["dim"] + "\u2591" * (width - filled) + COLORS["reset"]
        sys.stdout.write(f"\r  {label:20} {bar} {pct*100:.0f}%")
        sys.stdout.flush()
