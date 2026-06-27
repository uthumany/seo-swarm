"""SEO SWARM - Terminal UI Package.

Widget library, spinner engine, theming system, and dashboard components.
All zero-dependency, pure stdlib with ANSI escape codes.
"""

from seo_swarm.tui.widgets import Box, Panel, Table, Tree, Divider
from seo_swarm.tui.spinner import Spinner, MultiSpinner
from seo_swarm.tui.themes import Theme, ThemeManager, THEMES

# Legacy dashboard
from seo_swarm.tui.dashboard import TerminalDashboard, COLORS

__all__ = [
    # Widgets
    "Box",
    "Panel",
    "Table",
    "Tree",
    "Divider",
    # Spinners
    "Spinner",
    "MultiSpinner",
    # Themes
    "Theme",
    "ThemeManager",
    "THEMES",
    # Dashboard
    "TerminalDashboard",
    "COLORS",
]
