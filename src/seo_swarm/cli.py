#!/usr/bin/env python3
"""
SEO SWARM - Autonomous SEO Swarm Agents CLI
Main entry point for the SEO Swarm terminal application.
"""

import sys
import os
import argparse
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from seo_swarm.agents.registry import AgentRegistry
from seo_swarm.tui.dashboard import TerminalDashboard
from seo_swarm.memory.engine import MemoryEngine
from seo_swarm.ascii.banners import ASCIIBanners
from seo_swarm.skills.loader import SkillLoader
from seo_swarm.browser.engine import BrowserEngine


def run_audit(args):
    """Run an SEO audit on a target URL."""
    from seo_swarm.agents.orchestrator import AgentOrchestrator
    orchestrator = AgentOrchestrator()
    results = orchestrator.run_audit(target=args.url, agents=args.agents)
    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        TerminalDashboard().render_audit_results(results)


def run_agent(args):
    """Run a specific SEO agent."""
    from seo_swarm.agents.orchestrator import AgentOrchestrator
    orchestrator = AgentOrchestrator()
    agent = orchestrator.get_agent(args.name)
    if agent:
        agent.run(target=args.url, verbose=args.verbose)
    else:
        print(f"Agent '{args.name}' not found. Available: {orchestrator.list_agents()}")


def run_browser(args):
    """Launch autonomous browser automation."""
    engine = BrowserEngine()
    engine.navigate(args.url)
    if args.task:
        engine.execute_task(args.task)
    engine.close()


def run_swarm(args):
    """Run all agents in parallel as a swarm."""
    from seo_swarm.agents.orchestrator import AgentOrchestrator
    orchestrator = AgentOrchestrator()
    results = orchestrator.run_swarm(target=args.url)
    TerminalDashboard().render_swarm_results(results)


def show_dashboard(args):
    """Display the interactive terminal dashboard."""
    TerminalDashboard().show()


def show_agents(args):
    """List all agents with pixel art portraits or ASCII cards."""
    registry = AgentRegistry()
    banner = ASCIIBanners()
    if args.pixel_gallery:
        banner.show_pixel_gallery(registry.get_all())
    elif args.pixel_cards:
        banner.show_agent_cards(registry.get_all())
    elif args.art:
        banner.show_agent_cards(registry.get_all())  # fallback to pixel cards
    elif args.row:
        banner.show_agent_row(registry.get_all())
    else:
        for agent in registry.get_all():
            print(f"  [{agent.color}]{agent.emoji} {agent.name:<30} {agent.role}")


def show_portrait(args):
    """Show a single agent's pixel art portrait."""
    registry = AgentRegistry()
    agent = registry.get(args.name)
    if agent:
        ASCIIBanners().show_agent_portrait(agent, full=not args.compact)
    else:
        print(f"Agent '{args.name}' not found. Available: {', '.join(registry.list_ids())}")


def show_pixel_gallery(args):
    """Show the full pixel art gallery of all agents."""
    registry = AgentRegistry()
    ASCIIBanners().show_pixel_gallery(registry.get_all())


def install_skills(args):
    """Install preloaded SEO skills."""
    loader = SkillLoader()
    loader.install_all()


def search_memory(args):
    """Search the local memory database."""
    engine = MemoryEngine()
    results = engine.search(args.query)
    for r in results:
        print(f"  [{r['score']:.2f}] {r['key']}: {r['value'][:120]}...")


def main():
    """Main CLI entry point."""
    ASCIIBanners().print_banner()

    parser = argparse.ArgumentParser(
        prog="seo-swarm",
        description="SEO SWARM - Autonomous SEO Swarm Agents CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  seo-swarm audit https://example.com              # Run full SEO audit
  seo-swarm audit https://example.com --json       # JSON output
  seo-swarm agent technical-seo --url example.com
  seo-swarm swarm https://example.com                # All agents in parallel
  seo-swarm dashboard                                # Interactive TUI
  seo-swarm agents --pixel-cards                     # Pixel art agent cards
  seo-swarm agents --pixel-gallery                   # Pixel art gallery grid
  seo-swarm pixel-gallery                            # Full pixel art gallery
  seo-swarm portrait technical-seo                   # Single agent pixel portrait
  seo-swarm portrait seo-strategist --compact        # Compact portrait
  seo-swarm agents --row                             # Compact agent row view
  seo-swarm browser https://example.com              # Autonomous browser
  seo-swarm install-skills                           # Install preloaded skills
  seo-swarm memory "keyword research"                # Search memory
"""
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # audit command
    p_audit = subparsers.add_parser("audit", help="Run SEO audit on a URL")
    p_audit.add_argument("url", help="Target URL to audit")
    p_audit.add_argument("--agents", "-a", nargs="+", help="Specific agents to run")
    p_audit.add_argument("--json", "-j", action="store_true", help="Output as JSON")

    # agent command
    p_agent = subparsers.add_parser("agent", help="Run a specific SEO agent")
    p_agent.add_argument("name", help="Agent name (e.g., technical-seo)")
    p_agent.add_argument("--url", "-u", required=True, help="Target URL")
    p_agent.add_argument("--verbose", "-v", action="store_true")

    # browser command
    p_browser = subparsers.add_parser("browser", help="Autonomous browser control")
    p_browser.add_argument("url", help="URL to navigate to")
    p_browser.add_argument("--task", "-t", help="Task to execute")

    # swarm command
    p_swarm = subparsers.add_parser("swarm", help="Run all agents in parallel swarm")
    p_swarm.add_argument("url", help="Target URL")

    # dashboard command
    subparsers.add_parser("dashboard", help="Show interactive terminal dashboard")

    # agents command
    p_agents = subparsers.add_parser("agents", help="List all SEO agents")
    p_agents.add_argument("--art", "-a", action="store_true", help="Show pixel art agent cards")
    p_agents.add_argument("--pixel-cards", "-p", action="store_true", help="Show detailed pixel art cards")
    p_agents.add_argument("--pixel-gallery", "-g", action="store_true", help="Show pixel art gallery grid")
    p_agents.add_argument("--row", "-r", action="store_true", help="Show compact row view")

    # portrait command
    p_portrait = subparsers.add_parser("portrait", help="Show single agent pixel art portrait")
    p_portrait.add_argument("name", help="Agent ID (e.g., technical-seo, seo-strategist)")
    p_portrait.add_argument("--compact", "-c", action="store_true", help="Compact portrait only")

    # pixel-gallery command
    subparsers.add_parser("pixel-gallery", help="Show full pixel art gallery grid")

    # install-skills command
    subparsers.add_parser("install-skills", help="Install preloaded SEO skills")

    # skills command
    p_skills = subparsers.add_parser("skills", help="List installed skills")
    p_skills.add_argument("--search", "-s", help="Search skills by name")

    # memory command
    p_memory = subparsers.add_parser("memory", help="Search local memory")
    p_memory.add_argument("query", help="Search query")

    args = parser.parse_args()

    commands = {
        "audit": run_audit,
        "agent": run_agent,
        "browser": run_browser,
        "swarm": run_swarm,
        "dashboard": show_dashboard,
        "agents": show_agents,
        "portrait": show_portrait,
        "pixel-gallery": show_pixel_gallery,
        "install-skills": install_skills,
        "skills": lambda a: SkillLoader().list_skills(a.search if hasattr(a, 'search') else None),
        "memory": search_memory,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
