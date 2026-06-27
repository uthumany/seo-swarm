"""
SEO SWARM - ASCII Art Banners & Agent Cards
Generates beautiful ASCII art for the CLI and agent profile cards.
"""

import random
import sys
from typing import List

from seo_swarm.agents.registry import SEOAgent

# Terminal colors
C = {
    "r": "\033[0m",
    "cy": "\033[96m", "gn": "\033[92m", "ye": "\033[93m",
    "mg": "\033[95m", "bl": "\033[94m", "rd": "\033[91m",
    "wh": "\033[97m", "bk": "\033[90m", "b": "\033[1m", "d": "\033[2m",
}

# Agent ASCII art profile pictures
AGENT_ASCII = {
    "seo-strategist": r"""
   {c}    .-""""""-.
   {c}  .'   _   _   '.
   {c} /   .' '. .' '.   \
   {c}|   |  _| |_ |  |   |
   {c}|    \\________/    |
   {c} '.   \________/   .'
   {c}   '-._  JIQ  _.-'
   {c}       '------'     {r}""",

    "technical-seo": r"""
   {c}    .-'''|   |-.
   {c}   /     |   |  \
   {c}  |  _/=========\_  |
   {c}  | /|  O  |  O  |\ |
   {c}  || |_____|_____| ||
   {c}  | \=============/ |
   {c}   \_____________/
   {c}    '-----------'    {r}""",

    "content-seo": r"""
   {c}     .--------.
   {c}   .'  .====.  '.
   {c}  / __  ____  __ \
   {c} |  /  \/    \/  \  |
   {c} |  \__________/  |
   {c} |       ||       |
   {c}  \     _||_     /
   {c}   '.__/    \__.'   {r}""",

    "on-page-seo": r"""
   {c}     _____________
   {c}    /  ___________ \
   {c}   /  /  O   O   \  \
   {c}  |  |     _     |  |
   {c}  |  |    '-'    |  |
   {c}  |  |  .-----.  |  |
   {c}   \  \/_______\/  /
   {c}    \_____________/  {r}""",

    "off-page-seo": r"""
   {c}      _,._
   {c}    .'     '.
   {c}   /  _   _  \
   {c}  :  (o) (o)  :
   {c}  |     ^     |
   {c}  |  .-----.  |
   {c}   \ '-----' /
   {c}    '-------'      {r}""",

    "local-seo": r"""
   {c}     ___________
   {c}    /           \
   {c}   |  ()     ()  |
   {c}   |      "      |
   {c}   |    \___/    |
   {c}   |   .-----.   |
   {c}    \__/     \__/
   {c}       '-----'     {r}""",

    "seo-developer": r"""
   {c}      .------.
   {c}    .'   ||   '.
   {c}   /  _  ||  _  \
   {c}  |  / \ || / \  |
   {c}  |  \_/ || \_/  |
   {c}  |   ___||___   |
   {c}   \ /________\ /
   {c}    '----------'   {r}""",

    "seo-analyst": r"""
   {c}      .-'''''-.
   {c}    .'   _=_   '.
   {c}   /    /   \    \
   {c}  |    | O O |    |
   {c}  |     \_-_/     |
   {c}  |    ._____/    |
   {c}   \  /      \  /
   {c}    '----------'   {r}""",

    "voice-search": r"""
   {c}      ._______.
   {c}    .'    _    '.
   {c}   /    .' '.    \
   {c}  |   ()   ()   |
   {c}  |      /|\      |
   {c}  |     / | \     |
   {c}   \   /  |  \   /
   {c}    '----------'   {r}""",

    "mobile-pwa": r"""
   {c}      _________
   {c}    .'         '.
   {c}   /   _______   \
   {c}  |   |  _  _  |   |
   {c}  |   | |_||_| |   |
   {c}  |   |       | |   |
   {c}   \  |_______|/   /
   {c}    '._________.'   {r}""",
}

# Single-line ASCII art emoticons
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
}


class ASCIIBanners:
    """Generate ASCII art banners and agent cards."""

    def print_banner(self):
        """Print the main SEO SWARM banner."""
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
   ║{C['bk']}          Autonomous Multi-Agent SEO Automation Platform v1.0.0{C['cy']}          ║
   ║                                                              ║
   ╚══════════════════════════════════════════════════════════════╝{C['r']}
"""
        print(banner)

    def show_agent_cards(self, agents: List[SEOAgent]):
        """Display ASCII art profile cards for each agent."""
        print(f"\n{C['cy']}{C['b']}  \u250c{'─'*80}\u2510{C['r']}")

        for i, agent in enumerate(agents):
            color = C.get({
                "bright_cyan": "cy", "bright_green": "gn", "bright_magenta": "mg",
                "bright_yellow": "ye", "bright_blue": "bl", "bright_red": "rd",
                "cyan": "cy", "green": "gn", "magenta": "mg",
                "bright_white": "wh", "bright_black": "bk",
            }.get(agent.color, "wh"))

            art = AGENT_ASCII.get(agent.id, "")
            if art:
                art_colored = art.format(c=color, r=C['r'])
            else:
                art_colored = f"  {color}[{agent.emoji} NO ART]{C['r']}"

            status_icon = {"idle": "  \u25cb", "running": "  \u25d0", "complete": "  \u25cf", "error": "  \u2717"}.get(agent.status, "?")
            status_color = {"idle": C['bk'], "running": C['ye'], "complete": C['gn'], "error": C['rd']}.get(agent.status, C['wh'])

            print(f"{C['cy']}  \u2502{C['r']}                                                                                {C['cy']}\u2502{C['r']}")
            print(f"{C['cy']}  \u2502{C['r']}  {art_colored.split(chr(10))[1] if art else ''}")
            print(f"{C['cy']}  \u2502{C['r']}  {color}{C['b']}{agent.emoji} {agent.name}{C['r']}")
            print(f"{C['cy']}  \u2502{C['r']}  {color}{'─'*40}{C['r']}")
            print(f"{C['cy']}  \u2502{C['r']}  {C['bk']}Role:{C['r']} {agent.role}")
            print(f"{C['cy']}  \u2502{C['r']}  {C['bk']}Status:{C['r']} {status_color}{status_icon}{C['r']}")
            print(f"{C['cy']}  \u2502{C['r']}  {C['bk']}Tasks:{C['r']} {agent.tasks_completed} completed")
            print(f"{C['cy']}  \u2502{C['r']}  {C['bk']}Skills:{C['r']} {', '.join(agent.skills[:4])}")
            print(f"{C['cy']}  \u2502{C['r']}  {C['bk']}Desc:{C['r']} {agent.description[:70]}...")

        print(f"{C['cy']}  \u2514{'─'*80}\u2518{C['r']}")

    def print_small_banner(self):
        """Print a compact banner."""
        print(f"{C['cy']}{C['b']}  \U0001f41d SEO SWARM v1.0.0 \U0001f41d  {ONELINE['search']}{C['r']}")

    def print_agent_header(self, agent_name: str, color: str = "cy"):
        """Print a single agent header."""
        c = C.get(color, C['cy'])
        print(f"\n{c}{C['b']}\u250c{'─'*50}\u2510")
        print(f"\u2502  {agent_name:^46}  \u2502")
        print(f"\u2514{'─'*50}\u2518{C['r']}")

    def print_separator(self, char: str = "\u2500", width: int = 80, color: str = "cy"):
        """Print a colored separator line."""
        print(f"{C.get(color, C['cy'])}{char * width}{C['r']}")

    def print_oneline(self, name: str):
        """Print a single-line ASCII art."""
        art = ONELINE.get(name, name)
        print(f"  {art}")
