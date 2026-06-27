"""
SEO SWARM - Pixel Art Engine
================================
Renders 16x16 pixel art agent portraits in the terminal using
Unicode half-block characters for retro game-inspired visuals.

Inspired by:
  - pixilart.com (online pixel art community)
  - piskelapp.com (sprite editor)
  - itch.io/game-assets (free pixel art assets)
  - github.com/collections/pixel-art-tools
"""

from typing import Dict, List, Tuple

# ── Color Palette System ─────────────────────────────────────────────
# Each agent has a primary color palette for its pixel art

PALETTES: Dict[str, Dict[str, str]] = {
    "cyan": {
        "fg_bright": "\033[96m", "fg": "\033[36m", "fg_dark": "\033[90m",
        "bg_bright": "\033[106m", "bg": "\033[46m", "bg_dark": "\033[100m",
        "r": "\033[0m",
    },
    "green": {
        "fg_bright": "\033[92m", "fg": "\033[32m", "fg_dark": "\033[90m",
        "bg_bright": "\033[102m", "bg": "\033[42m", "bg_dark": "\033[100m",
        "r": "\033[0m",
    },
    "magenta": {
        "fg_bright": "\033[95m", "fg": "\033[35m", "fg_dark": "\033[90m",
        "bg_bright": "\033[105m", "bg": "\033[45m", "bg_dark": "\033[100m",
        "r": "\033[0m",
    },
    "yellow": {
        "fg_bright": "\033[93m", "fg": "\033[33m", "fg_dark": "\033[90m",
        "bg_bright": "\033[103m", "bg": "\033[43m", "bg_dark": "\033[100m",
        "r": "\033[0m",
    },
    "blue": {
        "fg_bright": "\033[94m", "fg": "\033[34m", "fg_dark": "\033[90m",
        "bg_bright": "\033[104m", "bg": "\033[44m", "bg_dark": "\033[100m",
        "r": "\033[0m",
    },
    "red": {
        "fg_bright": "\033[91m", "fg": "\033[31m", "fg_dark": "\033[90m",
        "bg_bright": "\033[101m", "bg": "\033[41m", "bg_dark": "\033[100m",
        "r": "\033[0m",
    },
    "white": {
        "fg_bright": "\033[97m", "fg": "\033[37m", "fg_dark": "\033[90m",
        "bg_bright": "\033[107m", "bg": "\033[47m", "bg_dark": "\033[100m",
        "r": "\033[0m",
    },
    "gray": {
        "fg_bright": "\033[37m", "fg": "\033[90m", "fg_dark": "\033[2m",
        "bg_bright": "\033[47m", "bg": "\033[100m", "bg_dark": "\033[40m",
        "r": "\033[0m",
    },
}


def p(hex_chars: str) -> List[List[int]]:
    """Parse a compact hex representation into a pixel grid.

    Each row should be 16 hex digits. Rows shorter than 16 are
    right-padded with zeros; rows longer are truncated to 16.
    """
    rows = [l.strip() for l in hex_chars.strip().split("\n") if l.strip()]
    result = []
    for row in rows:
        if len(row) > 16:
            row = row[:16]
        elif len(row) < 16:
            row = row + "0" * (16 - len(row))
        result.append([int(c, 16) for c in row])
    # Ensure exactly 16 rows
    while len(result) < 16:
        result.append([0] * 16)
    return result[:16]


# ── Agent Pixel Art Portraits (16×16, hex-encoded) ──────────────────
# Each portrait is 16×16 pixels. Hex digits 0-F for brightness.
# Rendering uses half-block ▀ for top/bottom pixel in each character cell.

AGENT_PIXELS: Dict[str, str] = {
    # 🔧 Technical SEO Specialist — Robot face with goggles (green)
    "technical-seo": """
    0000000000000000
    0000000550000000
    000005FFF5000000
    00005FFFFF5000000
    000555FFFF5550000
    005FFFFFFFFFF5000
    005FF555555FF5000
    055FF5FFF5FF55000
    055FF5FFF5FF55000
    005FF555555FF5000
    005FFFFFFFFFF5000
    0005FFFFFFFFFF5000
    00055FF555FF55000
    000055FFFFF5500000
    000000555550000000
    0000000000000000
    """,

    # 🧠 SEO Strategist — Brain/neural network (cyan)
    "seo-strategist": """
    0000000000000000
    0000000550000000
    000005FFF5000000
    00005FFFFF5000000
    0005FF5FF5FF50000
    005FF555555FF5000
    055FF5F5F5FF55000
    05FFF5FFF5FFF5000
    05FFFF5F5FFFF5000
    055FFF555FFF55000
    0055FFFFFFF55000
    00055FFFFF55000
    000005FFFFF5000000
    000005F555F5000000
    000000555550000000
    0000000000000000
    """,

    # ✍️ Content SEO Specialist — Quill pen writing (magenta)
    "content-seo": """
    0000000000000000
    0000000000050000
    0000000005F50000
    000000005FFF50000
    00000005FFFF50000
    000005FFFFF55000
    000055FFF55550000
    000055F5F55550000
    0055FF5FF5550000
    055F55FFFF550000
    0555FFFFF5500000
    0055FFF555000000
    0005FFF500000000
    00005F5500000000
    0000055000000000
    0000000000000000
    """,

    # 🔍 On-Page SEO Analyst — Magnifying glass (yellow)
    "on-page-seo": """
    0000000550000000
    000005FFF5000000
    00055FFFFF550000
    005FFFFFFFFF5000
    055FFF555FFF5500
    05FFF5005FFF5000
    05FFF5005FFF5000
    055FFF555FFF5500
    005FFFFFFF555000
    00055FFFFF500000
    000005FFFFF5000000
    000005FFFFF5000000
    0000005FFFFF5000000
    0000005FFFFF5000000
    0000055FFFFF5500000
    000000555555000000
    """,

    # 🔗 Off-Page SEO Specialist — Chain links (blue)
    "off-page-seo": """
    0000000000000000
    0000055555000000
    00055FFFFF550000
    005FFFFFFFFFF5000
    05FF5555555FF5000
    05FF55FFF55FF5000
    05FF5555555FF5000
    055FF55555FF55000
    005FFFFFFFFFF5000
    05FF5555555FF5000
    05FF55FFF55FF5000
    05FF5555555FF5000
    005FFFFFFFFFF5000
    00055FFFFF550000
    0000055555000000
    0000000000000000
    """,

    # 📍 Local SEO Specialist — Map pin marker (red)
    "local-seo": """
    0000005555000000
    000005FFFF5000000
    00005FFFFFF500000
    0005FFFFFFFF50000
    005FFF5F5FFF5000
    05FFF55555FFF5000
    05FFF55555FFF5000
    05FFFFFFFFFFFF5000
    05FFFFF55FFFFF5000
    005FFFFF55FFFFF5000
    0005FFFFFFF50000
    00005FFFFF500000
    000005FFF5000000
    0000005F50000000
    0000000500000000
    0000000000000000
    """,

    # 💻 SEO Developer — Monitor/screen with code (white)
    "seo-developer": """
    0000000000000000
    0005555555555000
    005FFFFFFFFFF5000
    05FF5FF5FF5FF5000
    05FFF5F5F5FFF5000
    05FF5FFFFF5FF5000
    05FFF55555FFF5000
    05FF5FFFFF5FF5000
    055FFFFFFFFFF55000
    0055555555555000
    000FFFFFFFFF0000
    00FFFFFFFFFFF00
    00FFFFFFFFFFF00
    000FFFFFFFFFF000
    0000000000000000
    0000000000000000
    """,

    # 📊 SEO Data Analyst — Bar chart/bars (cyan-dark)
    "seo-analyst": """
    0000000000000000
    0055005500550000
    05FF505FF505FF5000
    05FF505FF505FF5000
    05FF505FF505FF5000
    05FF505FF505FF5000
    05FF555FFF555FF5000
    05FFFFFFFFFFF5000
    05FF555FF555FF5000
    05FF505FF505FF5000
    05FF505FF505FF5000
    05FF555FF555FF5000
    05FFFFFFFFFFF5000
    0055555555555000
    0000000000000000
    0000000000000000
    """,

    # 🎙️ Voice Search Specialist — Microphone (magenta-bright)
    "voice-search": """
    0000000000000000
    0000005555000000
    000005FFFF5000000
    00005F5FF5F50000
    00005F5FF5F50000
    00005F5FF5F50000
    00055F5FF5F55000
    0005FFFFFFF50000
    0005FFFFFFF50000
    00005FFFFF500000
    000005FFF5000000
    0000005F50000000
    0000005F50000000
    0000055F55000000
    0000555555500000
    0000000000000000
    """,

    # 📱 Mobile & PWA SEO Specialist — Smartphone (green-dark)
    "mobile-pwa": """
    0000000000000000
    0000000555000000
    000005FFFFF5000000
    00055FFFFFFFFFF5000
    0005FFFFFFFFFFF5000
    005FFF5FFF5FFF5000
    005FFF5FFF5FFF5000
    005FFFFFFFFFFFF5000
    005FFF5FFF5FFF5000
    005FFF5FFF5FFF5000
    005FF5555555FF5000
    005FF5FFFF5FF5000
    0005FF5555FF50000
    00055FFFFFFF550000
    00000555555500000
    0000000000000000
    """,
}


class PixelRenderer:
    """Renders pixel art portraits in terminal with ANSI colors."""

    def __init__(self):
        pass

    def render_portrait(self, agent_id: str, palette_name: str = "cyan") -> str:
        """Render a 16x16 pixel art portrait for the given agent.

        Uses Unicode half-block characters (▀, ▄, █, ░) for double vertical
        resolution, achieving a crisp 16x16 look with 8 character rows.
        The entire portrait is wrapped in the palette color — no per-pixel ANSI.
        """
        palette = PALETTES.get(palette_name, PALETTES["gray"])
        hex_data = AGENT_PIXELS.get(agent_id)
        if not hex_data:
            return self._unknown_portrait(palette_name)

        grid = p(hex_data)
        lines = []
        fg = palette["fg_bright"]
        r = palette["r"]

        # Render 2 pixel rows per character row using ▀ (upper half block)
        for y in range(0, 16, 2):
            row_chars = []
            for x in range(16):
                top = grid[y][x] if y < len(grid) else 0
                bot = grid[y + 1][x] if (y + 1) < len(grid) else 0
                row_chars.append(self._pixel_char_simple(top, bot))
            lines.append(f"{fg}{''.join(row_chars)}{r}")
        return "\n".join(lines)

    def _pixel_char_simple(self, top: int, bot: int) -> str:
        """Convert two vertical pixels to exactly 2 characters.
        Uses Unicode block chars for terminal rendering.
          - 0 = empty
          - 1-7 = light shade (░ partial block)
          - 8-F = solid block (█ fully filled)
        Always returns exactly 2 characters.
        """
        def level(c):
            if c == 0: return 0
            return 2 if c >= 8 else 1

        tl = level(top)
        bl = level(bot)

        # Map (top_level, bottom_level) → 2-char sequence
        # ▀ = U+2580 UPPER HALF BLOCK (top filled, bottom empty)
        # ▄ = U+2584 LOWER HALF BLOCK (top empty, bottom filled)
        # █ = U+2588 FULL BLOCK (both filled)
        # ░ = U+2591 LIGHT SHADE (both light)
        # ▒ = U+2592 MEDIUM SHADE
        # ▓ = U+2593 DARK SHADE
        # Two spaces for empty

        MAP = {
            (0, 0): "  ",
            (2, 0): "▀ ",
            (1, 0): "░ ",
            (0, 2): "▄ ",
            (0, 1): "░ ",
            (2, 2): "██",
            (1, 1): "░░",
            (2, 1): "▀░",
            (1, 2): "░▄",
        }

        return MAP.get((tl, bl), "??")

    def _pixel_char(self, top: int, bot: int, pal: Dict[str, str]) -> str:
        """Convert two vertical pixels to a colored half-block character.

        Uses 3 brightness levels:
          - 0 = empty (space)
          - 1-7 = mid-tone (foreground color block)
          - 8-F = bright (background color block)
        """
        r = pal["r"]

        def level(c):
            """0=empty, 1=mid, 2=bright"""
            if c == 0:
                return 0
            return 2 if c >= 8 else 1

        tl = level(top)
        bl = level(bot)

        # Both empty
        if tl == 0 and bl == 0:
            return "  "

        # Top only
        if tl > 0 and bl == 0:
            c = pal["bg_bright"] if tl == 2 else pal["fg"]
            return f"{c}▀{r} "

        # Bottom only
        if tl == 0 and bl > 0:
            c = pal["bg_bright"] if bl == 2 else pal["fg"]
            return f"{c}▄{r} "

        # Both same level
        if tl == bl:
            c = pal["bg_bright"] if tl == 2 else pal["fg"]
            return f"{c}█{r} "

        # Different levels — top bright, bottom mid
        if tl == 2 and bl == 1:
            return f"{pal['bg_bright']}▀{r}{pal['fg']}▄{r}"[:4]
        # Top mid, bottom bright
        if tl == 1 and bl == 2:
            return f"{pal['fg']}▀{r}{pal['bg_bright']}▄{r}"[:4]
        # Both mid (should have been caught above)
        return f"{pal['fg']}█{r} "

    def _brightness(self, level: int, pal: Dict[str, str]) -> str:
        """Map a hex brightness level (0-F) to an ANSI color code."""
        if level == 0:
            return pal["fg_dark"]  # dark/off
        elif level <= 4:
            return pal["fg"]
        elif level <= 9:
            return pal["fg_bright"]
        else:
            return pal["bg_bright"]

    def render_card(self, agent_id: str, palette_name: str,
                    name: str, role: str, status: str,
                    skills: List[str], tasks: int) -> str:
        """Render a full agent card with pixel art portrait and metadata."""
        palette = PALETTES.get(palette_name, PALETTES["gray"])
        p = palette
        portrait = self.render_portrait(agent_id, palette_name)
        portrait_lines = portrait.split("\n")

        # Status indicator
        status_map = {
            "idle": f"{p['fg_dark']}◌ IDLE{p['r']}",
            "running": f"{p['fg']}◉ RUNNING{p['r']}",
            "complete": f"{p['fg_bright']}● DONE{p['r']}",
            "error": f"\033[91m✗ ERROR{p['r']}",
        }
        status_str = status_map.get(status, status)

        # Build card
        border = f"{p['fg']}┌{'─'*48}┐{p['r']}"
        footer = f"{p['fg']}└{'─'*48}┘{p['r']}"
        mid = f"{p['fg']}│{p['r']}"

        lines = [border]
        # Header row with portrait
        lines.append(f"{mid}  {portrait_lines[0]}    {p['fg_bright']}{p['fg']} {name}{p['r']}")
        for i in range(1, 8):
            info = ""
            if i == 1:
                info = f"{p['fg_dark']}Role:{p['r']} {role[:35]}"
            elif i == 2:
                info = f"{p['fg_dark']}Status:{p['r']} {status_str}"
            elif i == 3:
                info = f"{p['fg_dark']}Tasks:{p['r']} {tasks} completed"
            elif i == 4:
                info = f"{p['fg_dark']}Skills:{p['r']} {', '.join(skills[:4])}"
            elif i == 5:
                info = f"{p['fg_dark']}Type:{p['r']} Pixel Art 16×16 (retro)"
            elif i == 6:
                info = f"{p['fg_dark']}Engine:{p['r']} SEO SWARM v1.1.0"
            elif i == 7:
                info = f"{p['fg_bright']}  █ pixel art rendered via unicode █{p['r']}"
            lines.append(f"{mid}  {portrait_lines[i]}    {info}")
        lines.append(footer)
        return "\n".join(lines)

    def _unknown_portrait(self, palette_name: str) -> str:
        """Fallback portrait for unknown agents."""
        palette = PALETTES.get(palette_name, PALETTES["gray"])
        p = palette
        return "\n".join([
            f"{p['fg']}  ▄▄▄▄▄▄▄▄▄▄  {p['r']}",
            f"{p['fg']}  ██████████  {p['r']}",
            f"{p['fg']}  ██ ???? ██  {p['r']}",
            f"{p['fg']}  ██████████  {p['r']}",
            f"{p['fg']}  ▀▀▀▀▀▀▀▀▀▀  {p['r']}",
        ])

    def simple_portrait(self, agent_id: str, palette_name: str = "cyan") -> str:
        """Return just the portrait without card framing."""
        return self.render_portrait(agent_id, palette_name)


# ── Compact Pixel Avatars (8×8, for tight spaces) ───────────────────

COMPACT_PIXELS: Dict[str, str] = {
    "technical-seo": """00233200224442003333330324664203E66E3003666330023663200000000""",
    "seo-strategist": """002332000233320023D332023D6D20033DD3300233332000233200000000""",
    "content-seo": """000023000233200233D320023D320033D3300033320000332000000000""",
    "on-page-seo": """00222000022220022B22002BBB2002BB2000022200000220000000000""",
    "off-page-seo": """0000000002222002266200269962026996200222200000000000000000""",
    "local-seo": """000440000044400044E440044EE44004EE400004EE40000044000000000""",
    "seo-developer": """0000000005555005566550566655055555006666600666600000000""",
    "seo-analyst": """03303300333330033333003333300333330033333000333300000000""",
    "voice-search": """00444000044440044444404444440444440004EE4000444400000000""",
    "mobile-pwa": """0000000034443403444430344A430344443034AA4303444300033000""",
}
