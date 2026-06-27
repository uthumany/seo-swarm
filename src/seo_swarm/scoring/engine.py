"""
SEO SWARM - Advanced SEO Scorecard Engine
Quantitative 0-100 scoring across 5 SEO dimensions.
Zero external dependencies — pure Python stdlib.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class DimensionScore:
    name: str; score: float; weight: float; status: str
    details: List[Dict] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class ScorecardResult:
    target_url: str; total_score: float; grade: str
    dimensions: List[DimensionScore]; breakdown: Dict[str, float]
    total_recommendations: int; timestamp: float

    def to_dict(self) -> dict:
        return {
            "target_url": self.target_url, "total_score": round(self.total_score, 1),
            "grade": self.grade,
            "dimensions": [{"name": d.name, "score": round(d.score, 1), "weight": d.weight,
                            "status": d.status, "details": d.details,
                            "recommendations": d.recommendations} for d in self.dimensions],
            "breakdown": {k: round(v, 1) for k, v in self.breakdown.items()},
            "total_recommendations": self.total_recommendations,
            "timestamp": self.timestamp,
        }


class ScorecardEngine:
    DIMENSIONS = [("Technical SEO", 0.25), ("Content Quality", 0.25),
                  ("Performance", 0.20), ("Off-Page SEO", 0.15), ("Mobile & PWA", 0.15)]

    def calculate(self, target_url: str, audit_data: Optional[dict] = None) -> ScorecardResult:
        if audit_data is None: audit_data = {}
        dimensions = []; breakdown = {}
        for dim_name, weight in self.DIMENSIONS:
            score, details, recs = self._score_dimension(dim_name, target_url, audit_data)
            dim = DimensionScore(name=dim_name, score=score, weight=weight,
                                 status=self._status_label(score), details=details,
                                 recommendations=recs)
            dimensions.append(dim); breakdown[dim_name] = score
        total = sum(d.score * d.weight for d in dimensions)
        grade = self.get_letter_grade(total)
        recs = sum(len(d.recommendations) for d in dimensions)
        import time
        return ScorecardResult(target_url=target_url, total_score=total, grade=grade,
                               dimensions=dimensions, breakdown=breakdown,
                               total_recommendations=recs, timestamp=time.time())

    def _score_dimension(self, name: str, url: str, data: dict) -> Tuple[float, List[Dict], List[str]]:
        return {"Technical SEO": self._tech, "Content Quality": self._content,
                "Performance": self._perf, "Off-Page SEO": self._offpage,
                "Mobile & PWA": self._mobile}.get(name, lambda u, d: (50, [], []))(url, data)

    def _tech(self, url: str, d: dict):
        s = 70; de = []; r = []
        if url.startswith("https://"): s += 10; de.append({"check": "HTTPS", "status": "pass"})
        else: r.append("Enable HTTPS")
        if d.get("sitemap_found", True): s += 5; de.append({"check": "Sitemap", "status": "pass"})
        else: r.append("Add XML sitemap")
        if d.get("robots_txt_found", True): s += 5; de.append({"check": "Robots.txt", "status": "pass"})
        else: r.append("Create robots.txt")
        sc = d.get("schema_count", 0)
        if sc > 2: s += 5; de.append({"check": "Schema", "status": "pass"})
        elif sc == 0: r.append("Add structured data")
        else: de.append({"check": "Schema", "status": "warning"}); r.append("Add more schema")
        ci = d.get("crawl_issues", 0)
        if ci == 0: s += 5
        else: s -= min(ci * 2, 15); r.append(f"Fix {ci} crawl issues")
        return min(max(s, 0), 100), de, r

    def _content(self, url: str, d: dict):
        s = 65; de = []; r = []
        tl = d.get("title_length", 30)
        if 30 <= tl <= 60: s += 10; de.append({"check": "Title", "status": "pass"})
        elif tl < 30: s -= 5; r.append(f"Title too short ({tl} chars)")
        else: s -= 3; r.append(f"Title may be too long ({tl})")
        dl = d.get("description_length", 20)
        if 120 <= dl <= 160: s += 10
        else: r.append(f"Meta description should be 120-160 chars (is {dl})")
        h1 = d.get("h1_count", 1)
        if h1 == 1: s += 5
        elif h1 > 1: s -= 5; r.append("Multiple H1 tags")
        else: s -= 8; r.append("Missing H1 tag")
        return min(max(s, 0), 100), de, r

    def _perf(self, url: str, d: dict):
        s = 60; de = []; r = []
        lcp = d.get("lcp", 3.0)
        if lcp < 2.5: s += 15; de.append({"check": "LCP", "status": "good"})
        elif lcp < 4.0: s += 5; r.append("Improve LCP")
        else: s -= 10; r.append("LCP too slow")
        cls = d.get("cls", 0.1)
        if cls < 0.1: s += 10; de.append({"check": "CLS", "status": "good"})
        elif cls < 0.25: s += 3; r.append("Improve CLS")
        if d.get("ttfb", 0.5) < 0.8: s += 5
        return min(max(s, 0), 100), de, r

    def _offpage(self, url: str, d: dict):
        s = 50; de = []; r = []
        da = d.get("domain_authority", 30)
        if da > 60: s += 20
        elif da > 40: s += 10
        elif da > 20: s += 5
        else: r.append("Build quality backlinks")
        de.append({"check": "DA", "status": "info", "value": str(da)})
        tox = d.get("toxic_links", 0)
        if tox > 5: s -= 10; r.append(f"Disavow {tox} toxic links")
        elif tox > 0: s -= 3
        return min(max(s, 0), 100), de, r

    def _mobile(self, url: str, d: dict):
        s = 65; de = []; r = []
        if d.get("is_mobile_friendly", True): s += 10; de.append({"check": "Mobile", "status": "pass"})
        else: s -= 15; r.append("Make site mobile-friendly")
        if d.get("viewport_configured", True): s += 5
        else: r.append("Add viewport meta tag")
        if d.get("pwa_ready", False): s += 7; de.append({"check": "PWA", "status": "pass"})
        else: r.append("Consider PWA features")
        return min(max(s, 0), 100), de, r

    def get_letter_grade(self, score: float) -> str:
        for threshold, grade in [(95, "A+"), (90, "A"), (85, "A-"), (80, "B+"),
                                  (75, "B"), (70, "B-"), (65, "C+"), (60, "C"),
                                  (55, "C-"), (50, "D+"), (45, "D")]:
            if score >= threshold: return grade
        return "F"

    def _status_label(self, score: float) -> str:
        for t, s in [(85, "excellent"), (70, "good"), (55, "fair"), (40, "poor")]:
            if score >= t: return s
        return "critical"
