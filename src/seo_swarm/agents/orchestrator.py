"""SEO SWARM - Agent Orchestrator. Parallel swarm execution engine."""

import concurrent.futures
import time
import random
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from .registry import AgentRegistry, SEOAgent


@dataclass
class AuditResult:
    """Result from a single agent audit task."""
    agent_id: str
    agent_name: str
    status: str  # success, error, skipped
    findings: List[Dict[str, Any]] = field(default_factory=list)
    score: float = 0.0
    duration: float = 0.0
    details: str = ""


class AgentOrchestrator:
    """Orchestrates multiple SEO agents for audit and swarm operations."""

    def __init__(self):
        self.registry = AgentRegistry()
        self.agents = self.registry.get_all()

    def get_agent(self, agent_id: str) -> Optional[SEOAgent]:
        return self.registry.get(agent_id)

    def list_agents(self) -> List[str]:
        return self.registry.list_ids()

    def run_audit(self, target: str, agents: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run a sequential audit with selected agents."""
        selected = agents or self.registry.list_ids()
        results = []

        for agent_id in selected:
            agent = self.registry.get(agent_id)
            if not agent:
                continue

            start = time.time()
            agent.status = "running"
            try:
                finding = self._simulate_agent_work(agent, target)
                duration = time.time() - start
                agent.status = "complete"
                agent.tasks_completed += 1
                results.append(AuditResult(
                    agent_id=agent_id,
                    agent_name=agent.name,
                    status="success",
                    findings=finding,
                    score=random.uniform(75, 98),
                    duration=duration,
                    details=f"{agent.name} completed audit of {target}"
                ))
            except Exception as e:
                agent.status = "error"
                results.append(AuditResult(
                    agent_id=agent_id,
                    agent_name=agent.name,
                    status="error",
                    details=str(e)
                ))

        return {
            "target": target,
            "agents_used": len(results),
            "total_findings": sum(len(r.findings) for r in results),
            "results": [self._result_to_dict(r) for r in results],
            "timestamp": time.time(),
        }

    def run_swarm(self, target: str) -> Dict[str, Any]:
        """Run all agents in parallel as a swarm."""
        results = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = {}
            for agent in self.agents:
                agent.status = "running"
                future = executor.submit(self._simulate_agent_work, agent, target)
                futures[future] = agent

            for future in concurrent.futures.as_completed(futures):
                agent = futures[future]
                start = time.time()
                try:
                    findings = future.result()
                    duration = time.time() - start
                    agent.status = "complete"
                    agent.tasks_completed += 1
                    results.append(AuditResult(
                        agent_id=agent.id,
                        agent_name=agent.name,
                        status="success",
                        findings=findings,
                        score=random.uniform(75, 98),
                        duration=duration,
                    ))
                except Exception as e:
                    agent.status = "error"
                    results.append(AuditResult(
                        agent_id=agent.id,
                        agent_name=agent.name,
                        status="error",
                        details=str(e)
                    ))

        return {
            "target": target,
            "mode": "swarm",
            "agents_used": len(results),
            "total_findings": sum(len(r.findings) for r in results),
            "results": [self._result_to_dict(r) for r in results],
            "timestamp": time.time(),
        }

    def _simulate_agent_work(self, agent: SEOAgent, target: str) -> List[Dict[str, Any]]:
        """Simulate an agent performing SEO analysis tasks."""
        time.sleep(random.uniform(0.2, 0.8))
        findings = []
        templates = {
            "seo-strategist": [
                {"severity": "info", "category": "strategy", "finding": f"Keyword opportunity: {random.choice(['long-tail queries', 'topic clusters', 'local intent'])} detected for {target}"},
                {"severity": "info", "category": "roadmap", "finding": f"Recommended {random.randint(3,8)} priority initiatives for next quarter"},
            ],
            "technical-seo": [
                {"severity": "high", "category": "crawlability", "finding": f"Found {random.randint(2,15)} pages with crawl issues on {target}"},
                {"severity": "medium", "category": "performance", "finding": f"Page speed score: {random.randint(45,95)}/100 - optimization needed"},
                {"severity": "low", "category": "structured-data", "finding": "Missing schema markup on key pages"},
            ],
            "content-seo": [
                {"severity": "medium", "category": "content-gap", "finding": f"Identified {random.randint(3,12)} content gaps vs competitors"},
                {"severity": "info", "category": "internal-linking", "finding": "Internal link structure can be improved for topic clusters"},
            ],
            "on-page-seo": [
                {"severity": "medium", "category": "meta-tags", "finding": f"{random.randint(2,8)} pages have duplicate or missing title tags"},
                {"severity": "low", "category": "headers", "finding": "H1 hierarchy issues detected on multiple pages"},
            ],
            "off-page-seo": [
                {"severity": "info", "category": "backlinks", "finding": f"Domain authority score: {random.randint(20,65)}"},
                {"severity": "medium", "category": "toxic-links", "finding": f"Detected {random.randint(0,5)} potentially toxic backlinks"},
            ],
            "local-seo": [
                {"severity": "high", "category": "nap", "finding": "NAP inconsistencies found across local citations"},
                {"severity": "info", "category": "reviews", "finding": f"Average review rating: {random.uniform(3.0, 5.0):.1f}/5.0"},
            ],
            "seo-developer": [
                {"severity": "medium", "category": "core-web-vitals", "finding": f"LCP: {random.uniform(1.5, 6.0):.1f}s, CLS: {random.uniform(0.0, 0.3):.3f}"},
                {"severity": "low", "category": "accessibility", "finding": "Accessibility score below WCAG 2.1 AA threshold"},
            ],
            "seo-analyst": [
                {"severity": "info", "category": "traffic", "finding": f"Organic traffic trend: {random.choice(['+12%', '-3%', '+25%', 'stable'])}"},
                {"severity": "info", "category": "rankings", "finding": f"Top 3 positions: {random.randint(5,50)} keywords"},
            ],
            "voice-search": [
                {"severity": "info", "category": "featured-snippets", "finding": f"Opportunity to capture {random.randint(3,15)} featured snippets"},
                {"severity": "medium", "category": "faq", "finding": "FAQ schema missing - voice search optimization needed"},
            ],
            "mobile-pwa": [
                {"severity": "high", "category": "mobile-first", "finding": "Mobile page experience score below threshold"},
                {"severity": "medium", "category": "pwa", "finding": "PWA manifest incomplete or missing service worker"},
            ],
        }

        findings = templates.get(agent.id, [{"severity": "info", "category": "general", "finding": f"Audit completed for {target}"}])
        return findings

    def _result_to_dict(self, result: AuditResult) -> Dict[str, Any]:
        return {
            "agent_id": result.agent_id,
            "agent_name": result.agent_name,
            "status": result.status,
            "findings": result.findings,
            "score": round(result.score, 1),
            "duration": round(result.duration, 2),
            "details": result.details,
        }
