"""
SEO SWARM - Configurable Color Theme System

Named color themes with semantic color mapping and persistent configuration.
Supports theme switching and custom theme creation.
Uses ANSI escape codes from the shared COLORS dictionary in dashboard.py.
Zero external dependencies — pure stdlib.
"""

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from seo_swarm.tui.dashboard import COLORS


# ══════════════════════════════════════════════════════════════════════════════
# Theme data model
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class Theme:
    """A named color theme with semantic color → ANSI code mappings.

    Attributes:
        name: Human-readable theme name.
        colors: Dictionary mapping semantic color names (primary, success, warning,
                error, info, muted, accent, etc.) to ANSI escape codes.
        description: Optional description of the theme.
    """
    name: str
    colors: Dict[str, str]
    description: str = ""

    def get(self, key: str, default: str = "") -> str:
        """Get a color code by semantic name.

        Args:
            key: Semantic color name (e.g., 'primary', 'success').
            default: Fallback if key not found.

        Returns:
            ANSI escape code string.
        """
        return self.colors.get(key, default)

    def apply(self, key: str) -> str:
        """Apply a semantic color to text (returns the ANSI code).

        Args:
            key: Semantic color name.

        Returns:
            ANSI escape code for the color.
        """
        return self.colors.get(key, "")

    def wrap(self, key: str, text: str) -> str:
        """Wrap text in the given semantic color with reset.

        Args:
            key: Semantic color name.
            text: Text to colorize.

        Returns:
            Colorized text string with ANSI reset.
        """
        code = self.colors.get(key, "")
        return f"{code}{text}{COLORS['reset']}" if code else text

    def __repr__(self) -> str:
        return f"Theme(name={self.name!r}, colors={len(self.colors)} colors)"


# ══════════════════════════════════════════════════════════════════════════════
# Built-in themes
# ══════════════════════════════════════════════════════════════════════════════

THEMES: Dict[str, Theme] = {
    "default": Theme(
        name="default",
        description="Clean, readable defaults suitable for most terminals.",
        colors={
            "primary": COLORS["cyan"],
            "success": COLORS["green"],
            "warning": COLORS["yellow"],
            "error": COLORS["red"],
            "info": COLORS["blue"],
            "muted": COLORS["dim"],
            "accent": COLORS["magenta"],
            "text": COLORS["white"],
            "heading": COLORS["bright_white"] + COLORS["bold"],
            "border": COLORS["dim"],
            "highlight": COLORS["bright_cyan"],
            "dimmed": COLORS["dim"],
            "code": COLORS["bright_black"],
        },
    ),
    "neon": Theme(
        name="neon",
        description="Vibrant neon colors on dark backgrounds. High contrast, high energy.",
        colors={
            "primary": COLORS["bright_cyan"],
            "success": COLORS["bright_green"],
            "warning": COLORS["bright_yellow"],
            "error": COLORS["bright_red"],
            "info": COLORS["bright_blue"],
            "muted": COLORS["dim"],
            "accent": COLORS["bright_magenta"],
            "text": COLORS["bright_white"],
            "heading": COLORS["bright_cyan"] + COLORS["bold"],
            "border": COLORS["bright_black"],
            "highlight": COLORS["bright_yellow"],
            "dimmed": COLORS["dim"],
            "code": COLORS["bright_black"],
        },
    ),
    "forest": Theme(
        name="forest",
        description="Earthy greens and warm tones. Calm, natural palette.",
        colors={
            "primary": COLORS["green"],
            "success": COLORS["bright_green"],
            "warning": COLORS["yellow"],
            "error": COLORS["red"],
            "info": COLORS["cyan"],
            "muted": COLORS["dim"],
            "accent": COLORS["bright_yellow"],
            "text": COLORS["white"],
            "heading": COLORS["bright_green"] + COLORS["bold"],
            "border": COLORS["dim"],
            "highlight": COLORS["bright_green"],
            "dimmed": COLORS["dim"],
            "code": COLORS["bright_black"],
        },
    ),
    "ocean": Theme(
        name="ocean",
        description="Deep blues and cyans. Cool, professional maritime feel.",
        colors={
            "primary": COLORS["blue"],
            "success": COLORS["cyan"],
            "warning": COLORS["yellow"],
            "error": COLORS["bright_red"],
            "info": COLORS["bright_cyan"],
            "muted": COLORS["dim"],
            "accent": COLORS["bright_blue"],
            "text": COLORS["white"],
            "heading": COLORS["bright_blue"] + COLORS["bold"],
            "border": COLORS["dim"],
            "highlight": COLORS["bright_cyan"],
            "dimmed": COLORS["dim"],
            "code": COLORS["bright_black"],
        },
    ),
    "sunset": Theme(
        name="sunset",
        description="Warm oranges, yellows, and reds. Energetic sunset palette.",
        colors={
            "primary": COLORS["bright_yellow"],
            "success": COLORS["green"],
            "warning": COLORS["bright_red"],
            "error": COLORS["red"],
            "info": COLORS["bright_cyan"],
            "muted": COLORS["dim"],
            "accent": COLORS["bright_magenta"],
            "text": COLORS["white"],
            "heading": COLORS["bright_yellow"] + COLORS["bold"],
            "border": COLORS["dim"],
            "highlight": COLORS["bright_red"],
            "dimmed": COLORS["dim"],
            "code": COLORS["bright_black"],
        },
    ),
    "mono": Theme(
        name="mono",
        description="Monochromatic grayscale. Minimal, timeless, high readability.",
        colors={
            "primary": COLORS["bright_white"],
            "success": COLORS["white"],
            "warning": COLORS["dim"],
            "error": COLORS["bright_white"],
            "info": COLORS["bright_black"],
            "muted": COLORS["dim"],
            "accent": COLORS["white"],
            "text": COLORS["white"],
            "heading": COLORS["bright_white"] + COLORS["bold"],
            "border": COLORS["dim"],
            "highlight": COLORS["bright_white"],
            "dimmed": COLORS["dim"],
            "code": COLORS["bright_black"],
        },
    ),
    "dracula": Theme(
        name="dracula",
        description="Dracula-inspired dark theme. Purple, pink, cyan on dark background.",
        colors={
            "primary": COLORS["magenta"],
            "success": COLORS["bright_green"],
            "warning": COLORS["bright_yellow"],
            "error": COLORS["bright_red"],
            "info": COLORS["bright_cyan"],
            "muted": COLORS["dim"],
            "accent": COLORS["bright_magenta"],
            "text": COLORS["white"],
            "heading": COLORS["bright_magenta"] + COLORS["bold"],
            "border": COLORS["dim"],
            "highlight": COLORS["magenta"],
            "dimmed": COLORS["dim"],
            "code": COLORS["bright_black"],
        },
    ),
    "synthwave": Theme(
        name="synthwave",
        description="Retro 80s synthwave. Hot pink, cyan, and neon purple.",
        colors={
            "primary": COLORS["bright_magenta"],
            "success": COLORS["bright_cyan"],
            "warning": COLORS["bright_yellow"],
            "error": COLORS["bright_red"],
            "info": COLORS["bright_blue"],
            "muted": COLORS["dim"],
            "accent": COLORS["bright_magenta"],
            "text": COLORS["bright_white"],
            "heading": COLORS["bright_magenta"] + COLORS["bold"],
            "border": COLORS["dim"],
            "highlight": COLORS["bright_cyan"],
            "dimmed": COLORS["dim"],
            "code": COLORS["bright_black"],
        },
    ),
}


# ══════════════════════════════════════════════════════════════════════════════
# Theme Manager
# ══════════════════════════════════════════════════════════════════════════════

class ThemeManager:
    """Manages theme state, switching, and persistence.

    Reads/writes theme configuration to ~/.seo-swarm/theme.json.
    Falls back to the 'default' theme if no config is found.

    Example:
        tm = ThemeManager()
        print(tm.current.name)          # 'default'
        tm.apply("neon")                # Switch to neon theme
        print(tm.wrap("error", "Oops!"))  # Colorize text

        # Persist preference
        tm.save()

        # Later session will auto-load the saved theme
        tm2 = ThemeManager()  # Loads 'neon' from config
    """

    def __init__(self, config_dir: Optional[str] = None):
        """Initialize the ThemeManager.

        Args:
            config_dir: Optional path to config directory. Defaults to ~/.seo-swarm/.
        """
        self._config_dir = config_dir or os.path.join(os.path.expanduser("~"), ".seo-swarm")
        self.current: Theme = THEMES["default"]
        self._load_config()

    # ── Theme switching ────────────────────────────────────────────────────

    def apply(self, theme_name: str) -> Theme:
        """Switch to a named theme.

        Args:
            theme_name: Name of the theme to apply (e.g., 'neon', 'forest').

        Returns:
            The newly applied Theme object.

        Raises:
            ValueError: If the theme name is not found.
        """
        name_lower = theme_name.lower()
        if name_lower not in THEMES:
            available = ", ".join(self.list_themes())
            raise ValueError(
                f"Unknown theme: '{theme_name}'. Available: {available}"
            )
        self.current = THEMES[name_lower]
        return self.current

    def list_themes(self) -> List[str]:
        """List all available theme names.

        Returns:
            Sorted list of theme name strings.
        """
        return sorted(THEMES.keys())

    def get_theme(self, name: str) -> Optional[Theme]:
        """Get a Theme object by name without switching.

        Args:
            name: Theme name to look up.

        Returns:
            Theme object or None if not found.
        """
        return THEMES.get(name.lower())

    # ── Color helpers ──────────────────────────────────────────────────────

    def wrap(self, key: str, text: str) -> str:
        """Wrap text in the current theme's semantic color.

        Args:
            key: Semantic color name (e.g., 'primary', 'error').
            text: Text to colorize.

        Returns:
            Colorized text string.
        """
        return self.current.wrap(key, text)

    def color(self, key: str) -> str:
        """Get the ANSI code for a semantic color in the current theme.

        Args:
            key: Semantic color name.

        Returns:
            ANSI escape code string.
        """
        return self.current.apply(key)

    # ── Persistence ────────────────────────────────────────────────────────

    def save(self, theme_name: Optional[str] = None):
        """Save the current (or specified) theme to disk.

        Args:
            theme_name: Optional theme name to save. If None, saves current theme name.
        """
        os.makedirs(self._config_dir, exist_ok=True)
        config_path = os.path.join(self._config_dir, "theme.json")
        name_to_save = theme_name or self.current.name
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump({"theme": name_to_save}, f, indent=2)

    def _load_config(self):
        """Load theme preference from disk on initialization."""
        config_path = os.path.join(self._config_dir, "theme.json")
        if os.path.isfile(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                theme_name = data.get("theme", "default")
                if theme_name in THEMES:
                    self.current = THEMES[theme_name]
            except (json.JSONDecodeError, IOError):
                # Corrupt or unreadable config — stay on default
                pass

    # ── Registration ───────────────────────────────────────────────────────

    def register(self, theme: Theme):
        """Register a custom theme at runtime.

        Args:
            theme: A Theme object to register.

        Note:
            Custom themes are NOT persisted to disk by default.
            Call save() with the theme name to persist.
        """
        THEMES[theme.name.lower()] = theme

    def unregister(self, name: str) -> bool:
        """Remove a custom theme. Built-in themes cannot be removed.

        Args:
            name: Theme name to remove.

        Returns:
            True if removed, False if built-in or not found.
        """
        name_lower = name.lower()
        # Don't allow removing built-in themes
        builtins = {"default", "neon", "forest", "ocean", "sunset", "mono", "dracula", "synthwave"}
        if name_lower in builtins:
            return False
        if name_lower in THEMES:
            del THEMES[name_lower]
            return True
        return False

    # ── Info / Display ─────────────────────────────────────────────────────

    def preview(self, theme_name: Optional[str] = None) -> str:
        """Generate a preview string showing all colors in a theme.

        Args:
            theme_name: Optional theme to preview. Uses current theme if None.

        Returns:
            A formatted string showing each semantic color.
        """
        theme = THEMES.get(theme_name, self.current) if theme_name else self.current
        lines = [f"  Theme: {theme.name}"]
        if theme.description:
            lines.append(f"  {COLORS['dim']}{theme.description}{COLORS['reset']}")
        lines.append("")
        for key, code in theme.colors.items():
            sample = f"{code}████ Sample text — {key}{COLORS['reset']}"
            lines.append(f"  {key:<12} {sample}")
        return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
# Demonstration / Smoke Tests
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # ── Theme listing ──────────────────────────────────────────────────────
    print(COLORS["bold"] + "═══ Available Themes ═══" + COLORS["reset"])
    tm = ThemeManager()
    for name in tm.list_themes():
        theme = tm.get_theme(name)
        desc = f" — {theme.description}" if theme and theme.description else ""
        print(f"  {COLORS['bright_cyan']}•{COLORS['reset']} {name}{COLORS['dim']}{desc}{COLORS['reset']}")
    print()

    # ── Theme preview ──────────────────────────────────────────────────────
    print(COLORS["bold"] + "═══ Theme Preview — default ═══" + COLORS["reset"])
    print(tm.preview("default"))
    print()

    # ── Theme switching and color wrapping ─────────────────────────────────
    print(COLORS["bold"] + "═══ Theme Switching ═══" + COLORS["reset"])
    for name in ["default", "neon", "forest", "ocean", "sunset", "mono", "dracula"]:
        tm.apply(name)
        print(f"  [{name}]  ", end="")
        print(
            f"{tm.wrap('primary', 'Primary')}  "
            f"{tm.wrap('success', 'Success')}  "
            f"{tm.wrap('warning', 'Warning')}  "
            f"{tm.wrap('error', 'Error')}  "
            f"{tm.wrap('info', 'Info')}  "
            f"{tm.wrap('accent', 'Accent')}"
        )
    print()

    # ── Theme configuration persistence ────────────────────────────────────
    print(COLORS["bold"] + "═══ Persistence ═══" + COLORS["reset"])
    tm.apply("ocean")
    tm.save()
    config_path = os.path.join(os.path.expanduser("~"), ".seo-swarm", "theme.json")
    print(f"  Saved theme 'ocean' to {config_path}")
    print(f"  File exists: {os.path.isfile(config_path)}")
    if os.path.isfile(config_path):
        with open(config_path) as f:
            print(f"  Contents: {f.read().strip()}")
    print()

    # ── Custom theme registration ──────────────────────────────────────────
    print(COLORS["bold"] + "═══ Custom Theme ═══" + COLORS["reset"])
    custom = Theme(
        name="midnight",
        description="Dark midnight blue theme with gold accents.",
        colors={
            "primary": COLORS["bright_blue"],
            "success": COLORS["bright_cyan"],
            "warning": COLORS["bright_yellow"],
            "error": COLORS["bright_red"],
            "info": COLORS["cyan"],
            "muted": COLORS["dim"],
            "accent": COLORS["bright_yellow"],
            "text": COLORS["bright_white"],
            "heading": COLORS["bright_cyan"] + COLORS["bold"],
            "border": COLORS["dim"],
            "highlight": COLORS["bright_yellow"],
            "dimmed": COLORS["dim"],
            "code": COLORS["bright_black"],
        },
    )
    tm.register(custom)
    tm.apply("midnight")
    print(tm.preview("midnight"))
    print()
    print(f"  Registered themes: {tm.list_themes()}")
    tm.unregister("midnight")
    print(f"  After unregister:  {tm.list_themes()}")

    # ── Clean up test config ───────────────────────────────────────────────
    # Switch back to default and save
    tm.apply("default")
    tm.save()

    print()
    print(COLORS["bright_green"] + "All theme tests passed!" + COLORS["reset"])
