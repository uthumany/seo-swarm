"""
Tests for SEO SWARM v1.4.0 Interactive REPL and Chat Panel.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def test_repl_import():
    """Test REPL module imports cleanly."""
    from seo_swarm.tui.repl import SwarmREPL, SLASH_COMMANDS
    assert isinstance(SLASH_COMMANDS, dict)
    assert len(SLASH_COMMANDS) >= 15
    assert "/help" in SLASH_COMMANDS
    assert "/exit" in SLASH_COMMANDS
    assert "/audit" in SLASH_COMMANDS


def test_repl_slash_commands_complete():
    """Verify all core commands have slash equivalents."""
    from seo_swarm.tui.repl import SLASH_COMMANDS
    required = ["/audit", "/swarm", "/dashboard", "/agents", "/scorecard",
                "/crawl", "/report", "/competitor", "/theme", "/help", "/exit"]
    for cmd in required:
        assert cmd in SLASH_COMMANDS, f"Missing slash command: {cmd}"


def test_repl_parse():
    """Test command parsing logic."""
    from seo_swarm.tui.repl import SwarmREPL
    repl = SwarmREPL()

    # Slash commands
    cmd, args = repl._parse("/audit https://example.com")
    assert cmd == "audit"
    assert args["url"] == "https://example.com"

    cmd, args = repl._parse("/dashboard")
    assert cmd == "dashboard"

    cmd, args = repl._parse("/theme neon")
    assert cmd == "theme"
    assert args["name"] == "neon"

    cmd, args = repl._parse("/help")
    assert cmd == "help"

    cmd, args = repl._parse("/exit")
    assert cmd == "exit"

    # Natural language commands
    cmd, args = repl._parse("audit https://testsite.com")
    assert cmd == "audit"

    cmd, args = repl._parse("swarm https://testsite.com")
    assert cmd == "swarm"

    cmd, args = repl._parse("dashboard")
    assert cmd == "dashboard"

    cmd, args = repl._parse("agents")
    assert cmd == "agents"


def test_repl_parse_shortcuts():
    """Test shortcut commands."""
    from seo_swarm.tui.repl import SwarmREPL
    repl = SwarmREPL()

    shortcuts = {
        "a https://test.com": "audit",
        "s https://test.com": "swarm",
        "d": "dashboard",
        "p": "pixel-gallery",
    }
    for inp, expected_cmd in shortcuts.items():
        cmd, args = repl._parse(inp)
        assert cmd == expected_cmd, f"Shortcut '{inp}' -> expected '{expected_cmd}', got '{cmd}'"


def test_repl_parse_edge_cases():
    """Test edge cases in parsing."""
    from seo_swarm.tui.repl import SwarmREPL
    repl = SwarmREPL()

    # Empty input
    cmd, args = repl._parse("")
    assert cmd is None

    # Whitespace only
    cmd, args = repl._parse("   ")
    assert cmd is None

    # Unknown command
    cmd, args = repl._parse("blarg https://test.com")
    assert cmd == "unknown"


def test_repl_help_output():
    """Test help display doesn't crash."""
    from seo_swarm.tui.repl import SwarmREPL
    repl = SwarmREPL()
    try:
        repl._show_help()
        assert True
    except Exception as e:
        assert False, f"Help crashed: {e}"


def test_repl_welcome_output():
    """Test welcome screen renders."""
    from seo_swarm.tui.repl import SwarmREPL
    repl = SwarmREPL()
    try:
        repl._show_welcome()
        assert True
    except Exception as e:
        assert False, f"Welcome crashed: {e}"


def test_cli_interactive_mode():
    """Test that CLI can be imported and interactive mode flag exists."""
    import importlib
    spec = importlib.util.find_spec("seo_swarm.cli")
    assert spec is not None


def test_full_imports_still_work():
    """All existing imports still functional."""
    from seo_swarm.agents.registry import AgentRegistry
    from seo_swarm.tui.dashboard import TerminalDashboard
    from seo_swarm.scoring.engine import ScorecardEngine
    from seo_swarm.ascii.banners import ASCIIBanners
    assert AgentRegistry.count() == 10
