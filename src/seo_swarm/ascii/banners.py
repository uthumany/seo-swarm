"""
SEO SWARM - ASCII & Pixel Art Banners
========================================
Generates beautiful terminal art: pixel art agent portraits,
ASCII banners, emoticons, and formatted agent cards.

Uses the PixelRenderer for retro 16x16 pixel art portraits
inspired by pixilart.com, piskelapp.com, and classic game sprites.
"""

import sys
from typing import List, Optional

from seo_swarm.agents.registry import SEOAgent
from seo_swarm.ascii.pixel_art import PixelRenderer, PALETTES, AGENT_PIXELS

# Terminal color shorthands
C = {
    "r": "\033[0m", "b": "\033[1m", "d": "\033[2m",
    "cy": "\033[96m", "gn": "\033[92m", "ye": "\033[93m",
    "mg": "\033[95m", "bl": "\033[94m", "rd": "\033[91m",
    "wh": "\033[97m", "bk": "\033[90m",
}

# Mapping agent color names to pixel palette names
COLOR_TO_PALETTE = {
    "bright_cyan": "cyan", "bright_green": "green", "bright_magenta": "magenta",
    "bright_yellow": "yellow", "bright_blue": "blue", "bright_red": "red",
    "cyan": "cyan", "green": "green", "magenta": "magenta",
    "bright_white": "white", "bright_black": "gray", "yellow": "yellow",
    "red": "red", "blue": "blue",
}

# Single-line ASCII art emoticons (from 1lineart.kulaone.com)
ONELINE = {
    "search": "\U0001f50d ( \u30fb_\u30fb)\u2514\u252c\u2500\u252c\u2518",
    "swarm": "\U0001f41d \u00b0\u00b0\u00b0\u00b0\u00b0\u25cf\u00b0\u00b0\u00b0\u00b0\u00b0\u25cf\u00b0\u00b0\u00b0\u25cf\u00b0\u00b0\u00b0 > SEO SWARM",
    "success": "\u2728 (\u25d5\u203f\u25d5\u273f) SEO Audit Complete!",
    "running": "\u2699\ufe0f (\u2312\u25a1\u2312)\u256d\u2500\u2500\u2500\u2500\u256e Agents Working...",
    "brain": "\U0001f9e0 (\u256f\u00b0\u25a1\u00b0)\u256f \u253b\u2501\u2501\u2501\u2501\u2501\u253b Thinking...",
    "link": "\U0001f517 ~~\u257a\u2500\u2500\u2500\u25b6 Link Building Active",
    "mobile": "\U0001f4f1 \u260f\ufe0f (\u3003 \u25d4\u203f\u25d4)\u3003 Mobile Audit Running",
    "chart": "\U0001f4ca \u2191\u2193\u2191 Analysis \u03c3=98% Confidence",
    "shield": "\U0001f6e1\ufe0f (\u256f\u00b0\u25a1\u00b0)\u256f Security Scan Protected",
    "globe": "\U0001f310 ( \u0361\u00b0 \u035c\u0296 \u0361\u00b0) Global SEO Active",
    # New pixel art themed
    "pixel": "\U0001f5bc\ufe0f \u2588\u2580\u2584\u2588 Pixel Art Engine Active",
    "sprite": "\U0001f47e 16\u00d716 Sprite \u25e2\u25e3\u25e4\u25e5 Rendered",
    "retro": "\U0001f3ae RETRO MODE \u25e2\u2588\u2588\u2588\u25e3 GameBoy Era",
}


class ASCIIBanners:
    """Generate terminal art: pixel portraits, ASCII banners, agent cards."""

    def __init__(self):
        self.pixel = PixelRenderer()

    # ── Main Banner ───────────────────────────────────────────────

    def print_banner(self):
        """Print the main SEO SWARM banner with pixel art accents."""
        banner = f"""
{C['cy']}{C['b']}   ╔══════════════════════════════════════════════════════════════╗
   ║                                                              ║
   ║{C['ye']}     ███████╗███████╗ ██████╗     ███████╗██╗    ██╗ █████╗ ██████╗ ███╗   ███╗{C['cy']}   ║
   ║{C['ye']}     ██╔════╝██╔════╝██╔═══██╗    ██╔════╝██║    ██║██╔══██╗██╔══██╗████╗ ████║{C['cy']}   ║
   ║{C['ye']}     ███████╗█████╗  ██║   ██║    ███████╗██║ █╗ ██║███████║██████╔╝██╔████╔██║{C['cy']}   ║
   ║{C['ye']}     ╚════██║██╔══╝  ██║   ██║    ╚════██║██║███╗██║██╔══██║██╔══██╗██║╚██╔╝██║{C['cy']}   ║
   ║{C['ye']}     ███████║███████╗╚██████╔╝    ███████║╚███╔███╔╝██║  ██║██║  ██║██║ ╚═╝ ██║{C['cy']}   ║
   ║{C['ye']}     ╚══════╝╚══════╝ ╚═════╝     ╚══════╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝{C['cy']}   ║
   ║                                                              ║
   ║{C['gn']}     {ONELINE['swarm']}     {C['cy']}   ║
   ║{C['bk']}    Autonomous Multi-Agent SEO Automation Platform v1.1.0         {C['cy']}   ║
   ║{C['mg']}    {ONELINE['pixel']}     {C['cy']}   ║
   ║                                                              ║
   ╚══════════════════════════════════════════════════════════════╝{C['r']}
"""
        print(banner)

    # ── Pixel Art Agent Cards ─────────────────────────────────────

    def show_agent_cards(self, agents: List[SEOAgent]):
        """Display pixel art profile cards for each agent."""
        print(f"\n{C['cy']}{C['b']}  ╔{'═'*56}╗{C['r']}")
        print(f"{C['cy']}{C['b']}  ║{C['r']}  {C['ye']}{ONELINE['pixel']}   {C['bk']}16×16 Pixel Art Agent Gallery{C['r']}  {C['cy']}{C['b']}║{C['r']}")
        print(f"{C['cy']}{C['b']}  ╚{'═'*56}╝{C['r']}\n")

        for i, agent in enumerate(agents):
            palette_name = COLOR_TO_PALETTE.get(agent.color, "gray")
            pal = PALETTES.get(palette_name, PALETTES["gray"])

            # Status indicator
            status_icon = {"idle": "◌", "running": "◉", "complete": "●", "error": "✗"}.get(agent.status, "?")
            status_colors = {
                "idle": C['bk'], "running": C['ye'],
                "complete": C['gn'], "error": C['rd']
            }
            sc = status_colors.get(agent.status, C['wh'])

            # Render card
            card = self.pixel.render_card(
                agent_id=agent.id,
                palette_name=palette_name,
                name=agent.name,
                role=agent.role,
                status=agent.status,
                skills=agent.skills,
                tasks=agent.tasks_completed,
            )
            print(card)
            print()

    # ── Compact Agent List with Pixel Avatars ─────────────────────

    def show_agent_row(self, agents: List[SEOAgent]):
        """Show a compact row of agents with small pixel avatars."""
        print(f"\n{C['cy']}{C['b']}  AGENT SWARM — 10 Specialized SEO Agents{C['r']}")
        print(f"{C['bk']}  {'─'*76}{C['r']}")

        for agent in agents:
            palette_name = COLOR_TO_PALETTE.get(agent.color, "gray")
            portrait = self.pixel.render_portrait(agent.id, palette_name)
            p_lines = portrait.split("\n")

            status_icon = {"idle": "◌", "running": "◉", "complete": "●", "error": "✗"}.get(agent.status, "?")
            pal = PALETTES[palette_name]

            # Single-line row with portrait
            print(f"  {p_lines[3]}  {pal['fg_bright']}{agent.emoji} {agent.name:<28}{C['r']}  "
                  f"{pal['fg']}{status_icon} {agent.status.upper():8}{C['r']}  "
                  f"{C['bk']}Skills: {len(agent.skills)}{C['r']}")

        print(f"{C['bk']}  {'─'*76}{C['r']}\n")

    # ── Single Agent Pixel Portrait ───────────────────────────────

    def show_agent_portrait(self, agent: SEOAgent, full: bool = True):
        """Display a single agent's pixel art portrait."""
        palette_name = COLOR_TO_PALETTE.get(agent.color, "cyan")
        pal = PALETTES[palette_name]

        if full:
            print(self.pixel.render_card(
                agent_id=agent.id,
                palette_name=palette_name,
                name=agent.name,
                role=agent.role,
                status=agent.status,
                skills=agent.skills,
                tasks=agent.tasks_completed,
            ))
        else:
            portrait = self.pixel.render_portrait(agent.id, palette_name)
            print(f"\n{pal['fg_bright']}{C['b']}  {agent.emoji} {agent.name}{C['r']}")
            print(portrait)

    # ── Pixel Art Gallery ─────────────────────────────────────────

    def show_pixel_gallery(self, agents: List[SEOAgent]):
        """Show all 10 pixel art portraits in a gallery grid layout."""
        print(f"\n{C['cy']}{C['b']}  ╔{'═'*66}╗{C['r']}")
        print(f"{C['cy']}{C['b']}  ║  {C['mg']}{ONELINE['retro']}  {C['bk']}Pixel Art Agent Gallery (16×16 sprites){C['r']}  {C['cy']}{C['b']}║{C['r']}")
        print(f"{C['cy']}{C['b']}  ╚{'═'*66}╝{C['r']}\n")

        # Render 2 agents per row in a grid
        for i in range(0, len(agents), 2):
            a1 = agents[i]
            a2 = agents[i + 1] if i + 1 < len(agents) else None

            pal1 = PALETTES[COLOR_TO_PALETTE.get(a1.color, "gray")]
            p1 = self.pixel.render_portrait(a1.id, COLOR_TO_PALETTE.get(a1.color, "gray"))
            p1_lines = p1.split("\n")

            if a2:
                pal2 = PALETTES[COLOR_TO_PALETTE.get(a2.color, "gray")]
                p2 = self.pixel.render_portrait(a2.id, COLOR_TO_PALETTE.get(a2.color, "gray"))
                p2_lines = p2.split("\n")
            else:
                pal2 = pal1
                p2_lines = [""] * 8

            # Pair header
            print(f"  {pal1['fg_bright']}{C['b']}{a1.emoji} {a1.name:<27}{C['r']}    "
                  f"{pal2['fg_bright']}{C['b']}{a2.emoji if a2 else ''} {a2.name if a2 else '':<27}{C['r']}")

            # Pair portraits side by side
            for row in range(8):
                print(f"  {p1_lines[row]}    {p2_lines[row]}")
            print()

    # ── Utility Methods ───────────────────────────────────────────

    def print_small_banner(self):
        """Print a compact banner."""
        print(f"{C['cy']}{C['b']}  \U0001f41d SEO SWARM v1.1.0 \U0001f41d  {ONELINE['pixel']}{C['r']}")

    def print_agent_header(self, agent_name: str, color: str = "cyan"):
        """Print a single agent header."""
        pal = PALETTES.get(color, PALETTES["cyan"])
        print(f"\n{pal['fg_bright']}{C['b']}┌{'─'*50}┐")
        print(f"│  {agent_name:^46}  │")
        print(f"└{'─'*50}┘{C['r']}")

    def print_separator(self, char: str = "─", width: int = 80, color: str = "cyan"):
        """Print a colored separator line."""
        pal = PALETTES.get(color, PALETTES["cyan"])
        print(f"{pal['fg']}{char * width}{C['r']}")

    def print_oneline(self, name: str):
        """Print a single-line ASCII art / emoticon."""
        art = ONELINE.get(name, name)
        print(f"  {art}")
