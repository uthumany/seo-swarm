"""SEO SWARM - Terminal UI Package.

Widget library, spinner engine, theming system, layout engine,
interactive menus, notifications, progress tracking, and dashboards.
All zero-dependency, pure stdlib with ANSI escape codes.
"""

# Widgets
from seo_swarm.tui.widgets import Box, Panel, Table, Tree, Divider

# Spinners
from seo_swarm.tui.spinner import Spinner, MultiSpinner, SPINNER_FRAMES

# Themes
from seo_swarm.tui.themes import Theme, ThemeManager, THEMES

# Progress tracking
from seo_swarm.tui.progress import ProgressTracker, LiveDisplay

# Interactive menus
from seo_swarm.tui.menu import Menu, SelectMenu, Prompt

# Notifications and animations
from seo_swarm.tui.notify import Toast, NotificationStack, Animator

# Layout engine
from seo_swarm.tui.layout import Layout, Columns, FlexRow, StatusBar

# Legacy dashboard + next-gen
from seo_swarm.tui.dashboard import TerminalDashboard, COLORS
from seo_swarm.tui.dashboard_v2 import DashboardV2

__all__ = [
    # Widgets
    "Box", "Panel", "Table", "Tree", "Divider",
    # Spinners
    "Spinner", "MultiSpinner", "SPINNER_FRAMES",
    # Themes
    "Theme", "ThemeManager", "THEMES",
    # Progress
    "ProgressTracker", "LiveDisplay",
    # Menus
    "Menu", "SelectMenu", "Prompt",
    # Notifications
    "Toast", "NotificationStack", "Animator",
    # Layout
    "Layout", "Columns", "FlexRow", "StatusBar",
    # Dashboards
    "TerminalDashboard", "DashboardV2", "COLORS",
]
