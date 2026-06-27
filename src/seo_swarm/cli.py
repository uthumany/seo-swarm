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
    """Display the interactive terminal dashboard — auto-detects enhanced TUI."""
    from pathlib import Path
    import json
    cfg = Path.home() / ".seo-swarm" / "config.json"
    mode = "classic"
    if cfg.exists():
        try:
            config = json.loads(cfg.read_text() or "{}")
            mode = config.get("tui_mode", "classic")
        except json.JSONDecodeError:
            pass

    if mode == "enhanced":
        try:
            from seo_swarm.tui.dashboard_v2 import DashboardV2
            DashboardV2().show()
            return
        except ImportError:
            pass  # Fall back to classic

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


# ── v1.2.0 Advanced Feature Handlers ──────────────────────────────

def run_scorecard(args):
    """Calculate SEO scorecard (0-100 scoring across 5 dimensions)."""
    from seo_swarm.scoring.engine import ScorecardEngine
    engine = ScorecardEngine()
    result = engine.calculate(args.url)
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        TerminalDashboard().render_scorecard(result)


def run_crawl(args):
    """Crawl a website for real SEO data."""
    from seo_swarm.crawler.engine import CrawlerEngine
    engine = CrawlerEngine()
    result = engine.crawl(args.url, max_pages=args.max_pages, max_depth=args.depth)
    print(f"\n  Crawled: {len(result.pages)} pages from {args.url}")
    print(f"  Total links: {result.total_links}  |  Broken: {result.broken_links}")
    for p in result.pages[:10]:
        print(f"    [{p.status}] {p.url}")


def run_report(args):
    """Generate SEO audit report (HTML or Markdown)."""
    from seo_swarm.agents.orchestrator import AgentOrchestrator
    from seo_swarm.reporting.generator import ReportGenerator
    from seo_swarm.scoring.engine import ScorecardEngine

    orchestrator = AgentOrchestrator()
    scorecard = ScorecardEngine().calculate(args.url)
    audit = orchestrator.run_audit(args.url)
    combined = {"scorecard": scorecard.to_dict(), "audit": audit}

    gen = ReportGenerator()
    fmt = args.format if args.format != "md" else "markdown"
    out = args.output or f"seo-swarm-report.{'md' if fmt == 'markdown' else 'html'}"
    path = gen.generate_html(combined, out) if fmt == "html" else gen.generate_markdown(combined, out)
    print(f"  Report generated: {path}")


def run_competitor(args):
    """Compare against competitor URLs."""
    from seo_swarm.competitor.engine import CompetitorEngine
    engine = CompetitorEngine()
    report = engine.compare(args.url, args.competitors)
    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        TerminalDashboard().render_competitor(report)


def run_sitemap(args):
    """Generate or validate XML sitemaps."""
    from seo_swarm.sitemap.generator import SitemapGenerator
    gen = SitemapGenerator()
    if args.validate:
        result = gen.validate(args.validate)
        print(json.dumps(result, indent=2))
    elif args.urls:
        urls = [{"loc": u} for u in args.urls]
        path = gen.generate(urls, args.output)
        print(f"  Sitemap generated: {path}")
    elif args.from_crawl:
        from seo_swarm.crawler.engine import CrawlerEngine
        crawler = CrawlerEngine()
        crawl = crawler.crawl(args.from_crawl, max_pages=100)
        urls = [{"loc": p.url} for p in crawl.pages]
        path = gen.generate(urls, args.output)
        print(f"  Sitemap from crawl: {path} ({len(urls)} URLs)")
    else:
        print("  Use --urls, --from-crawl, or --validate")


def run_schema_gen(args):
    """Generate JSON-LD schema markup."""
    from seo_swarm.schema_gen.generator import SchemaGenerator
    gen = SchemaGenerator()
    if args.list:
        print("  Available schema types:")
        for t in gen.list_types():
            print(f"    - {t}")
    else:
        data = json.loads(args.data) if args.data else {}
        result = gen.generate(args.type, data)
        print(result)


def run_track(args):
    """Keyword rank tracking."""
    from seo_swarm.tracker.engine import RankTracker
    tracker = RankTracker()
    if args.summary:
        summary = tracker.get_summary()
        print(json.dumps(summary, indent=2))
    elif args.trends:
        trends = tracker.get_trends()
        print(f"\n  Top Gainers:")
        for t in trends.get("gainers", [])[:5]:
            print(f"    ↑ +{t['change']}  {t['keyword']} → pos {t['position']}")
        print(f"  Top Losers:")
        for t in trends.get("losers", [])[:5]:
            print(f"    ↓ {t['change']}  {t['keyword']} → pos {t['position']}")
    elif args.history:
        history = tracker.get_history(args.keyword)
        for h in history:
            print(f"  [{h['date']}] pos {h['position']} — {h['keyword']}")
    else:
        result = tracker.track(args.keyword, args.url or "https://example.com")
        print(f"  Keyword: {result['keyword']}  |  Position: {result['position']}")


def run_backlinks(args):
    """Analyze backlink profile."""
    from seo_swarm.backlinks.engine import BacklinkAnalyzer
    analyzer = BacklinkAnalyzer()
    if args.compare:
        result = analyzer.compare_domains([args.domain] + args.compare)
        print(json.dumps(result, indent=2))
    else:
        profile = analyzer.analyze_domain(args.domain)
        print(f"\n  Domain: {args.domain}")
        print(f"  Authority: {profile.domain_authority}/100")
        print(f"  Backlinks: {profile.total_backlinks}  |  Ref Domains: {profile.referring_domains}")
        print(f"  Spam Score: {profile.spam_score}%")


def run_content_analyze(args):
    """Analyze content quality."""
    from seo_swarm.content_analyzer.engine import ContentAnalyzer
    analyzer = ContentAnalyzer()
    text = ""
    if args.text:
        text = args.text
    elif args.file:
        text = open(args.file).read()
    elif args.url:
        # try to fetch
        import urllib.request
        try:
            text = urllib.request.urlopen(args.url, timeout=10).read().decode()
        except:
            text = f"Sample content from {args.url} for analysis."
    else:
        print("  Provide --text, --url, or --file")
        return

    result = analyzer.analyze(text, args.keyword)
    print(f"\n  Readability: {result.readability_score:.1f} (Grade {result.grade_level})")
    print(f"  Word Count: {result.word_count}  |  Sentences: {result.sentence_count}")
    if result.keyword_density is not None:
        print(f"  Keyword Density: {result.keyword_density:.1f}%")


def run_monitor(args):
    """SEO health monitoring."""
    from seo_swarm.monitor.engine import HealthMonitor
    from seo_swarm.scoring.engine import ScorecardEngine

    monitor = HealthMonitor()
    if args.alerts:
        alerts = monitor.check_alerts(args.url)
        for a in alerts:
            sev = {"critical": "\U0001f534", "warning": "\U0001f7e1", "info": "\U0001f535"}.get(a.severity, "\u26aa")
            print(f"  {sev} [{a.severity.upper()}] {a.message}")
        if not alerts:
            print("  \u2705 No active alerts")
    elif args.history:
        snapshots = monitor.get_history(args.url)
        for s in snapshots:
            print(f"  [{s.timestamp}] Score: {s.total_score:.0f}  Issues: {s.total_issues}  Status: {s.status}")
    elif args.trend:
        trend = monitor.get_trend_data(args.url, args.trend)
        for t in trend:
            print(f"  [{t[0]}] {t[1]:.1f}")
    else:
        scorecard = ScorecardEngine().calculate(args.url)
        sid = monitor.take_snapshot(args.url, scorecard.to_dict())
        print(f"  Snapshot saved: {sid}")
        print(f"  Score: {scorecard.total_score:.1f}  Grade: {scorecard.grade}")


# ── v1.3.0 TUI/UX Handlers ────────────────────────────────────────

def run_theme(args):
    """Switch terminal color theme."""
    try:
        from seo_swarm.tui.themes import ThemeManager
        tm = ThemeManager()
    except ImportError:
        print("  Themes coming soon — install v1.3.0+")
        return

    if args.list:
        for name in tm.list_themes():
            current = " (active)" if name == tm.current.name else ""
            print(f"  \u25cf {name}{current}")
    elif args.name:
        tm.apply(args.name)
        print(f"  \u2728 Theme switched to: {args.name}")
    else:
        print(f"  Current theme: {tm.current.name}")
        print("  Available: " + ", ".join(tm.list_themes()))


def run_tui_mode(args):
    """Toggle TUI mode between classic and enhanced."""
    if args.mode:
        from pathlib import Path
        cfg = Path.home() / ".seo-swarm" / "config.json"
        cfg.parent.mkdir(parents=True, exist_ok=True)
        import json
        config = {}
        if cfg.exists():
            config = json.loads(cfg.read_text() or "{}")
        config["tui_mode"] = args.mode
        cfg.write_text(json.dumps(config, indent=2))
        print(f"  TUI mode set to: {args.mode}")
    else:
        from pathlib import Path
        cfg = Path.home() / ".seo-swarm" / "config.json"
        mode = "classic"
        if cfg.exists():
            import json
            config = json.loads(cfg.read_text() or "{}")
            mode = config.get("tui_mode", "classic")
        print(f"  Current TUI mode: {mode}")
        print("  Use: seo-swarm tui classic  or  seo-swarm tui enhanced")
        print(f"  Use: seo-swarm tui classic  or  seo-swarm tui enhanced")


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

    # -- NEW v1.2.0 Advanced Commands --

    # scorecard command
    p_score = subparsers.add_parser("scorecard", help="Calculate SEO scorecard (0-100)")
    p_score.add_argument("url", help="Target URL")
    p_score.add_argument("--json", "-j", action="store_true", help="JSON output")

    # crawl command
    p_crawl = subparsers.add_parser("crawl", help="Crawl a website for SEO data")
    p_crawl.add_argument("url", help="Target URL")
    p_crawl.add_argument("--max-pages", "-m", type=int, default=50, help="Max pages to crawl")
    p_crawl.add_argument("--depth", "-d", type=int, default=3, help="Crawl depth")

    # report command
    p_report = subparsers.add_parser("report", help="Generate SEO audit report")
    p_report.add_argument("url", help="Target URL")
    p_report.add_argument("--format", "-f", choices=["html", "markdown", "md"], default="html")
    p_report.add_argument("--output", "-o", help="Output file path")

    # competitor command
    p_comp = subparsers.add_parser("competitor", help="Compare against competitors")
    p_comp.add_argument("url", help="Target URL")
    p_comp.add_argument("--competitors", "-c", nargs="+", required=True, help="Competitor URLs")
    p_comp.add_argument("--json", "-j", action="store_true")

    # sitemap command
    p_sm = subparsers.add_parser("sitemap", help="Generate XML sitemap")
    p_sm.add_argument("--urls", "-u", nargs="+", help="URLs to include")
    p_sm.add_argument("--from-crawl", "-c", help="Generate from crawl of this URL")
    p_sm.add_argument("--output", "-o", default="sitemap.xml", help="Output path")
    p_sm.add_argument("--validate", "-v", help="Validate existing sitemap file")

    # schema command
    p_schema = subparsers.add_parser("schema", help="Generate JSON-LD schema markup")
    p_schema.add_argument("--type", "-t", required=True, help="Schema type (Organization, Article, FAQ, Product, etc.)")
    p_schema.add_argument("--data", "-d", default="{}", help="JSON data for schema")
    p_schema.add_argument("--list", "-l", action="store_true", help="List available schema types")

    # rank-tracker command
    p_track = subparsers.add_parser("track", help="Keyword rank tracking")
    p_track.add_argument("keyword", help="Keyword to track")
    p_track.add_argument("--url", "-u", help="Target URL")
    p_track.add_argument("--history", "-H", action="store_true", help="Show history")
    p_track.add_argument("--trends", action="store_true", help="Show ranking trends")
    p_track.add_argument("--summary", "-s", action="store_true", help="Show tracking summary")

    # backlinks command
    p_bl = subparsers.add_parser("backlinks", help="Analyze backlink profile")
    p_bl.add_argument("domain", help="Domain to analyze")
    p_bl.add_argument("--compare", "-c", nargs="+", help="Compare multiple domains")

    # content-analyze command
    p_ca = subparsers.add_parser("content-analyze", help="Analyze content quality")
    p_ca.add_argument("--text", "-t", help="Text to analyze")
    p_ca.add_argument("--url", "-u", help="URL to fetch and analyze")
    p_ca.add_argument("--keyword", "-k", help="Target keyword for density check")
    p_ca.add_argument("--file", "-f", help="File containing text to analyze")

    # monitor command
    p_mon = subparsers.add_parser("monitor", help="SEO health monitoring")
    p_mon.add_argument("url", help="Target URL")
    p_mon.add_argument("--history", "-H", action="store_true", help="Show health history")
    p_mon.add_argument("--alerts", "-a", action="store_true", help="Show active alerts")
    p_mon.add_argument("--trend", "-t", help="Show trend for specific metric")

    # -- v1.3.0 TUI/UX commands --

    # theme command
    p_theme = subparsers.add_parser("theme", help="Switch terminal color theme")
    p_theme.add_argument("name", nargs="?", help="Theme name (default, neon, forest, ocean, sunset, mono)")
    p_theme.add_argument("--list", "-l", action="store_true", help="List available themes")

    # tui-mode command
    p_tui = subparsers.add_parser("tui", help="Toggle TUI mode (classic or enhanced)")
    p_tui.add_argument("mode", nargs="?", choices=["classic", "enhanced"], help="TUI mode")

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
        # v1.2.0 advanced features
        "scorecard": run_scorecard,
        "crawl": run_crawl,
        "report": run_report,
        "competitor": run_competitor,
        "sitemap": run_sitemap,
        "schema": run_schema_gen,
        "track": run_track,
        "backlinks": run_backlinks,
        "content-analyze": run_content_analyze,
        "monitor": run_monitor,
        # v1.3.0 TUI/UX
        "theme": run_theme,
        "tui": run_tui_mode,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
