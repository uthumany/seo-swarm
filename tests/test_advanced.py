"""
Tests for SEO SWARM v1.2.0 Advanced Features.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def test_scorecard_engine():
    """Test the SEO scorecard engine."""
    from seo_swarm.scoring.engine import ScorecardEngine
    engine = ScorecardEngine()
    result = engine.calculate("https://example.com")
    assert result.total_score > 0
    assert result.grade in ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "F"]
    assert len(result.dimensions) == 5
    assert result.total_recommendations >= 0
    d = result.to_dict()
    assert "breakdown" in d
    assert "dimensions" in d


def test_scorecard_letter_grades():
    """Test letter grade mapping."""
    from seo_swarm.scoring.engine import ScorecardEngine
    engine = ScorecardEngine()
    assert engine.get_letter_grade(97) == "A+"
    assert engine.get_letter_grade(88) == "A-"
    assert engine.get_letter_grade(72) == "B-"
    assert engine.get_letter_grade(62) == "C"
    assert engine.get_letter_grade(42) == "F"


def test_scorecard_with_data():
    """Test scorecard with provided audit data."""
    from seo_swarm.scoring.engine import ScorecardEngine
    engine = ScorecardEngine()
    data = {
        "title_length": 45, "description_length": 140,
        "h1_count": 1, "lcp": 2.0, "cls": 0.05,
        "ttfb": 0.3, "domain_authority": 50,
        "crawl_issues": 2, "schema_count": 3,
    }
    result = engine.calculate("https://testsite.com", data)
    assert result.total_score > 60
    assert result.total_recommendations >= 0


def test_scorecard_json_output():
    """Test JSON serialization."""
    from seo_swarm.scoring.engine import ScorecardEngine
    import json
    engine = ScorecardEngine()
    result = engine.calculate("https://test.com")
    j = json.dumps(result.to_dict())
    data = json.loads(j)
    assert "total_score" in data
    assert "grade" in data
    assert len(data["dimensions"]) == 5


def test_scorecard_low_scores():
    """Test scorecard with bad data."""
    from seo_swarm.scoring.engine import ScorecardEngine
    engine = ScorecardEngine()
    data = {
        "title_length": 5, "description_length": 5,
        "h1_count": 0, "lcp": 6.0, "cls": 0.5,
        "domain_authority": 5, "crawl_issues": 20,
    }
    result = engine.calculate("http://bad.com", data)
    assert result.total_score < 65  # Poorly configured site should score low


def test_scoring_imports():
    """Test all new module imports are available."""
    modules = [
        "seo_swarm.scoring.engine",
    ]
    for mod in modules:
        __import__(mod)
        assert True  # Import succeeded


# ── Existing tests still pass ──

def test_agent_registry():
    from seo_swarm.agents.registry import AgentRegistry
    assert AgentRegistry.count() == 10
    assert AgentRegistry.get("technical-seo") is not None


def test_memory_engine():
    from seo_swarm.memory.engine import MemoryEngine
    mem = MemoryEngine(db_path="/tmp/test_seo_v120.db")
    mem.save("test", "value")
    results = mem.search("test")
    assert len(results) >= 1
    mem.clear()
    mem.close()


def test_orchestrator():
    from seo_swarm.agents.orchestrator import AgentOrchestrator
    orch = AgentOrchestrator()
    agents = orch.list_agents()
    assert len(agents) == 10
