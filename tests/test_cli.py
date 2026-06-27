"""
Tests for SEO SWARM CLI.
"""

import sys
import os
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def test_agent_registry():
    """Test that all 10 agents are registered."""
    from seo_swarm.agents.registry import AgentRegistry
    agents = AgentRegistry.get_all()
    assert len(agents) == 10
    assert AgentRegistry.count() == 10

    # Check specific agents exist
    assert AgentRegistry.get("technical-seo") is not None
    assert AgentRegistry.get("seo-strategist") is not None
    agent = AgentRegistry.get("local-seo")
    assert agent.name == "Local SEO Specialist"
    assert agent.emoji == "\U0001f4cd"  # pin


def test_agent_list_ids():
    """Test listing agent IDs."""
    from seo_swarm.agents.registry import AgentRegistry
    ids = AgentRegistry.list_ids()
    assert "mobile-pwa" in ids
    assert "voice-search" in ids
    assert "seo-analyst" in ids


def test_agent_get_by_role():
    """Test searching agents by role keyword."""
    from seo_swarm.agents.registry import AgentRegistry
    results = AgentRegistry.get_by_role("Content")
    assert len(results) >= 1
    assert any(a.id == "content-seo" for a in results)


def test_agent_to_dict():
    """Test agent serialization."""
    from seo_swarm.agents.registry import AgentRegistry
    agent = AgentRegistry.get("technical-seo")
    d = agent.to_dict()
    assert d["id"] == "technical-seo"
    assert d["name"] == "Technical SEO Specialist"
    assert "skills" in d


def test_memory_engine():
    """Test self-improving memory system."""
    from seo_swarm.memory.engine import MemoryEngine
    mem = MemoryEngine(db_path="/tmp/test_seo_swarm_memory.db")

    # Save
    mem.save("test_key", "test_value", "test_category")
    mem.save("keyword_research", "long-tail keywords for SaaS", "research")

    # Search
    results = mem.search("keyword")
    assert len(results) >= 1
    assert any(r["key"] == "keyword_research" for r in results)

    # Learn
    mem.learn("pattern1", "insight from data", 0.8, "test")
    learnings = mem.get_learnings()
    assert len(learnings) >= 1
    assert learnings[0]["pattern"] == "pattern1"

    # Stats
    stats = mem.stats()
    assert stats["total_memories"] >= 2
    assert stats["total_learnings"] >= 1

    mem.clear()
    mem.close()


def test_skill_loader():
    """Test skill loading."""
    from seo_swarm.skills.loader import SkillLoader
    loader = SkillLoader()

    # Count skills
    result = loader.install_all()
    assert result["seo"] >= 20
    assert result["browser"] >= 10

    # Get specific skill
    skill = loader.get_skill("browser use")
    assert skill is not None
    assert "browser-use" in skill["url"]

    # List with search
    skills = loader.list_skills("technical")
    assert len(skills) >= 1


def test_ascii_banners():
    """Test ASCII art banner rendering."""
    from seo_swarm.ascii.banners import ASCIIBanners, ONELINE
    banner = ASCIIBanners()

    # Test oneline art exists
    assert "search" in ONELINE
    assert "swarm" in ONELINE
    assert "success" in ONELINE
    assert len(ONELINE) >= 8


def test_browser_engine():
    """Test browser automation engine."""
    from seo_swarm.browser.engine import BrowserEngine
    engine = BrowserEngine(headless=True)

    engine.navigate("https://example.com")
    assert engine.current_url == "https://example.com"
    assert len(engine.history) == 1

    result = engine.execute_task("extract-meta")
    assert result["task"] == "extract-meta"
    assert "title" in result

    result = engine.execute_task("audit-performance")
    assert result["task"] == "audit-performance"
    assert "lcp" in result
    assert result["performance_score"] >= 0

    engine.close()


def test_orchestrator_audit():
    """Test agent orchestrator audit."""
    from seo_swarm.agents.orchestrator import AgentOrchestrator
    orch = AgentOrchestrator()
    results = orch.run_audit("https://testsite.com", agents=["technical-seo", "local-seo"])
    assert results["target"] == "https://testsite.com"
    assert results["agents_used"] == 2
    assert "results" in results


def test_orchestrator_swarm():
    """Test swarm parallel execution."""
    from seo_swarm.agents.orchestrator import AgentOrchestrator
    orch = AgentOrchestrator()
    results = orch.run_swarm("https://testsite.com")
    assert results["mode"] == "swarm"
    assert results["agents_used"] == 10
    assert len(results["results"]) == 10


def test_orchestrator_list():
    """Test listing agents from orchestrator."""
    from seo_swarm.agents.orchestrator import AgentOrchestrator
    orch = AgentOrchestrator()
    agents = orch.list_agents()
    assert len(agents) == 10
    assert "seo-strategist" in agents
    assert "mobile-pwa" in agents
