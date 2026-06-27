"""
SEO SWARM - Advanced SEO Scorecard Engine
Quantitative 0-100 scoring across 5 SEO dimensions.
Zero external dependencies — pure Python stdlib.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class DimensionScore:
    """Score for a single SEO dimension."""
    name: str
    score: float
    weight: float
    status: str
    details: List[Dict] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class ScorecardResult:
    """Complete SEO scorecard with breakdown across all dimensions."""
    target_url: str
    total_score: float
    grade: str
    dimensions: List[DimensionScore]
    breakdown: Dict[str, float]
    total_recommendations: int
    timestamp: float

    def to_dict(self) -> dict:
        return {
            "target_url": self.target_url,
            "total_score": round(self.total_score, 1),
            "grade": self.grade,
            "dimensions": [
                {"name": d.name, "score": round(d.score, 1), "weight": d.weight,
                 "status": d.status, "details": d.details, "recommendations": d.recommendations}
                for d in self.dimensions
            ],
            "breakdown": {k: round(v, 1) for k, v in self.breakdown.items()},
            "total_recommendations": self.total_recommendations,
            "timestamp": self.timestamp,
        }


class ScorecardEngine:
    """Calculate comprehensive SEO scores from audit data."""

    DIMENSIONS = [
        ("Technical SEO", 0.25),
        ("Content Quality", 0.25),
        ("Performance", 0.20),
        ("Off-Page SEO", 0.15),
        ("Mobile & PWA", 0.15),
    ]

    def calculate(self, target_url: str, audit_data: Optional[dict] = None) -> ScorecardResult:
        """Calculate a full SEO scorecard."""
        if audit_data is None:
            audit_data = {}
        dimensions = []
        breakdown = {}
        for dim_name, weight in self.DIMENSIONS:
            score, details, recs = self._score_dimension(dim_name, target_url, audit_data)
            status = self._status_label(score)
            dim = DimensionScore(name=dim_name, score=score, weight=weight,
                                 status=status, details=details, recommendations=recs)
            dimensions.append(dim)
            breakdown[dim_name] = score
        total = sum(d.score * d.weight for d in dimensions)
        grade = self.get_letter_grade(total)
        total_recs = sum(len(d.recommendations) for d in dimensions)
        import time
        return ScorecardResult(target_url=target_url, total_score=total, grade=grade,
                               dimensions=dimensions, breakdown=breakdown,
                               total_recommendations=total_recs, timestamp=time.time())

    def _score_dimension(self, dim_name: str, url: str, data: dict) -> Tuple[float, List[Dict], List[str]]:
        if dim_name == "Technical SEO": return self._score_technical(url, data)
        if dim_name == "Content Quality": return self._score_content(data)
        if dim_name == "Performance": return self._score_performance(data)
        if dim_name == "Off-Page SEO": return self._score_offpage(url, data)
        if dim_name == "Mobile & PWA": return self._score_mobile(data)
        return 50.0, [], []

    def _score_technical(self, url: str, data: dict) -> Tuple[float, List[Dict], List[str]]:
        score = 70.0; details = []; recs = []
        if url.startswith("https://"):
            score += 10; details.append({"check": "HTTPS", "status": "pass", "value": "Enabled"})
        else:
            details.append({"check": "HTTPS", "status": "fail", "value": "Not enabled"})
            recs.append("Enable HTTPS for your site")
        sitemap = data.get("sitemap_found", True)
        if sitemap:
            score += 5; details.append({"check": "Sitemap", "status": "pass", "value": "Present"})
        else:
            details.append({"check": "Sitemap", "status": "fail", "value": "Missing"})
            recs.append("Add an XML sitemap")
        robots = data.get("robots_txt_found", True)
        if robots:
            score += 5; details.append({"check": "Robots.txt", "status": "pass", "value": "Present"})
        else:
            recs.append("Create a robots.txt file")
        schema_count = data.get("schema_count", 0)
        if schema_count > 2:
            score += 5; details.append({"check": "Structured Data", "status": "pass", "value": f"{schema_count} schemas"})
        elif schema_count > 0:
            score += 2; details.append({"check": "Structured Data", "status": "warning"})
            recs.append("Add more structured data markup")
        else:
            details.append({"check": "Structured Data", "status": "fail", "value": "None"})
            recs.append("Implement JSON-LD structured data")
        crawl = data.get("crawl_issues", 0)
        if crawl == 0: score += 5
        else: score -= min(crawl * 2, 15); recs.append(f"Fix {crawl} crawl issues")
        return min(max(score, 0), 100), details, recs

    def _score_content(self, data: dict) -> Tuple[float, List[Dict], List[str]]:
        score = 65.0; details = []; recs = []
        tl = data.get("title_length", 30)
        if 30 <= tl <= 60: score += 10; details.append({"check": "Title", "status": "pass", "value": f"{tl} chars"})
        elif tl < 30: score -= 5; recs.append(f"Title too short ({tl} chars)")
        else: score -= 3; recs.append(f"Title may be too long ({tl} chars)")
        dl = data.get("description_length", 20)
        if 120 <= dl <= 160: score += 10; details.append({"check": "Meta Desc", "status": "pass", "value": f"{dl} chars"})
        else: recs.append(f"Meta description should be 120-160 chars (currently {dl})")
        h1 = data.get("h1_count", 1)
        if h1 == 1: score += 5
        elif h1 > 1: score -= 5; recs.append("Multiple H1 tags detected")
        else: score -= 8; recs.append("Missing H1 tag")
        return min(max(score, 0), 100), details, recs

    def _score_performance(self, data: dict) -> Tuple[float, List[Dict], List[str]]:
        score = 60.0; details = []; recs = []
        lcp = data.get("lcp", 3.0)
        if lcp < 2.5: score += 15; details.append({"check": "LCP", "status": "good", "value": f"{lcp:.1f}s"})
        elif lcp < 4.0: score += 5; recs.append("Improve LCP")
        else: score -= 10; recs.append("Critical: LCP too slow")
        cls = data.get("cls", 0.1)
        if cls < 0.1: score += 10; details.append({"check": "CLS", "status": "good", "value": str(cls)})
        elif cls < 0.25: score += 3; recs.append("Improve CLS")
        ttfb = data.get("ttfb", 0.5)
        if ttfb < 0.8: score += 5; details.append({"check": "TTFB", "status": "good", "value": f"{ttfb:.1f}s"})
        return min(max(score, 0), 100), details, recs

    def _score_offpage(self, url: str, data: dict) -> Tuple[float, List[Dict], List[str]]:
        score = 50.0; details = []; recs = []
        da = data.get("domain_authority", 30)
        if da > 60: score += 20
        elif da > 40: score += 10
        elif da > 20: score += 5
        else: recs.append("Build quality backlinks to improve DA")
        details.append({"check": "Domain Authority", "status": "info", "value": str(da)})
        toxic = data.get("toxic_links", 0)
        if toxic > 5: score -= 10; recs.append(f"Disavow {toxic} toxic backlinks")
        elif toxic > 0: score -= 3
        return min(max(score, 0), 100), details, recs

    def _score_mobile(self, data: dict) -> Tuple[float, List[Dict], List[str]]:
        score = 65.0; details = []; recs = []
        if data.get("is_mobile_friendly", True): score += 10; details.append({"check": "Mobile", "status": "pass"})
        else: score -= 15; recs.append("Make site mobile-friendly")
        if data.get("viewport_configured", True): score += 5
        else: recs.append("Add viewport meta tag")
        if data.get("touch_elements_spaced", True): score += 3
        if data.get("pwa_ready", False): score += 7; details.append({"check": "PWA", "status": "pass"})
        else: recs.append("Consider PWA features")
        return min(max(score, 0), 100), details, recs

    def get_letter_grade(self, score: float) -> str:
        if score >= 95: return "A+"
        if score >= 90: return "A"
        if score >= 85: return "A-"
        if score >= 80: return "B+"
        if score >= 75: return "B"
        if score >= 70: return "B-"
        if score >= 65: return "C+"
        if score >= 60: return "C"
        if score >= 55: return "C-"
        if score >= 50: return "D+"
        if score >= 45: return "D"
        return "F"

    def _status_label(self, score: float) -> str:
        if score >= 85: return "excellent"
        if score >= 70: return "good"
        if score >= 55: return "fair"
        if score >= 40: return "poor"
        return "critical"
