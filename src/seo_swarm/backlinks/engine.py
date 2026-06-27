"""
SEO SWARM - Backlink Analyzer Engine
Domain authority estimation, link quality scoring, and competitor comparison.
"""

import re
import math
import hashlib
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from string import ascii_lowercase


@dataclass
class BacklinkProfile:
    """Backlink analysis results for a single domain."""
    domain: str
    domain_authority: float        # 0-100
    total_backlinks: int
    referring_domains: int
    spam_score: float              # 0-100
    quality_distribution: Dict[str, int]  # e.g. {"high": 42, "medium": 120, "low": 38}
    anchor_texts: List[str] = field(default_factory=list)
    top_linking_domains: List[str] = field(default_factory=list)
    estimated_traffic: int = 0


class BacklinkAnalyzer:
    """Analyze domain backlink profiles using heuristics (stdlib only).

    In production you'd connect to Ahrefs / Moz / Majestic APIs.
    This engine uses deterministic domain-based heuristics to produce
    realistic estimates without any external dependencies.
    """

    # Common TLD authority weights (rough heuristic)
    _TLD_WEIGHTS: Dict[str, float] = {
        "gov": 0.95, "edu": 0.90, "org": 0.75,
        "com": 0.65, "net": 0.60, "io": 0.55,
        "co": 0.50, "info": 0.40, "biz": 0.35,
        "xyz": 0.25, "tk": 0.15, "ml": 0.10,
    }

    # Anchor text categories for simulated analysis
    _ANCHOR_CATEGORIES = [
        "branded", "exact-match", "partial-match",
        "generic", "naked-url", "image",
    ]

    def __init__(self):
        self._cache: Dict[str, BacklinkProfile] = {}

    # ------------------------------------------------------------------
    # Internal heuristics
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_tld(domain: str) -> str:
        """Extract top-level domain from a domain string."""
        parts = domain.rsplit(".", 1)
        return parts[-1].lower() if len(parts) > 1 else ""

    @staticmethod
    def _text_entropy(s: str) -> float:
        """Shannon entropy of a string (used for spamminess estimation)."""
        if not s:
            return 0.0
        counts = {c: s.count(c) for c in set(s)}
        length = len(s)
        return -sum((cnt / length) * math.log2(cnt / length) for cnt in counts.values())

    def _domain_seed(self, domain: str) -> float:
        """Deterministic seed for a domain (0-1 range)."""
        h = int(hashlib.md5(domain.lower().encode()).hexdigest()[:8], 16)
        return (h % 10000) / 10000.0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze_domain(self, domain: str) -> BacklinkProfile:
        """Analyze a domain's backlink profile and return a BacklinkProfile."""

        domain = domain.lower().strip()
        # Strip protocol / path if accidentally provided
        domain = re.sub(r"^https?://", "", domain)
        domain = re.sub(r"/.*$", "", domain)
        domain = re.sub(r"^www\.", "", domain)

        if domain in self._cache:
            return self._cache[domain]

        tld = self._extract_tld(domain)
        seed = self._domain_seed(domain)

        # Domain Authority (0-100) — heuristic blend
        tld_weight = self._TLD_WEIGHTS.get(tld, 0.30)
        name_length_bonus = max(0, 0.15 - len(domain) * 0.002)  # shorter ≈ better
        authority = round((seed * 40 + tld_weight * 40 + name_length_bonus * 20), 1)
        authority = max(1.0, min(100.0, authority))

        # Backlink counts (log-scale from authority)
        total_backlinks = int(10 ** (2 + seed * 4))  # 100 → ~1M
        referring_domains = max(1, total_backlinks // int(5 + seed * 50))

        # Spam score (0-100)
        entropy = self._text_entropy(domain)
        spam_base = (1.0 - entropy / 4.5) * 60  # low entropy → spammy
        tld_spam = {"tk": 40, "ml": 35, "xyz": 25, "info": 15, "biz": 10}.get(tld, 0)
        spam_score = round(max(0.0, min(100.0, spam_base + tld_spam + seed * 20)), 1)

        # Quality distribution
        high = max(1, int(referring_domains * (0.1 + seed * 0.15)))
        medium = max(1, int(referring_domains * (0.3 + seed * 0.25)))
        low = referring_domains - high - medium
        quality_distribution = {"high": high, "medium": medium, "low": max(0, low)}

        # Simulated anchor texts
        anchor_texts = [
            domain.replace(f".{tld}", ""),
            f"{domain.replace(f'.{tld}', '').title()} Official",
            f"visit {domain}",
            "click here",
            "learn more",
            domain,
            f"https://{domain}",
        ]

        # Top linking domains (simulated)
        top_linking_domains = [
            f"example{chr(97 + i % 26)}.com" for i in range(5)
        ]

        estimated_traffic = int(total_backlinks * 0.02 * (authority / 100))

        profile = BacklinkProfile(
            domain=domain,
            domain_authority=authority,
            total_backlinks=total_backlinks,
            referring_domains=referring_domains,
            spam_score=spam_score,
            quality_distribution=quality_distribution,
            anchor_texts=anchor_texts,
            top_linking_domains=top_linking_domains,
            estimated_traffic=estimated_traffic,
        )

        self._cache[domain] = profile
        return profile

    def compare_domains(self, domains: List[str]) -> Dict[str, Any]:
        """Compare backlink profiles across multiple domains.

        Returns a dict with per-domain profiles and a comparative summary.
        """
        profiles = {d: self.analyze_domain(d) for d in domains}

        # Winner per metric
        best_authority = max(profiles.values(), key=lambda p: p.domain_authority)
        most_backlinks = max(profiles.values(), key=lambda p: p.total_backlinks)
        most_referring = max(profiles.values(), key=lambda p: p.referring_domains)
        lowest_spam = min(profiles.values(), key=lambda p: p.spam_score)

        # Rankings for each metric
        def rank(metric, reverse=True):
            items = sorted(profiles.items(), key=lambda x: getattr(x[1], metric), reverse=reverse)
            return {d: i + 1 for i, (d, _) in enumerate(items)}

        return {
            "profiles": {d: {
                "domain_authority": p.domain_authority,
                "total_backlinks": p.total_backlinks,
                "referring_domains": p.referring_domains,
                "spam_score": p.spam_score,
                "quality_distribution": p.quality_distribution,
                "estimated_traffic": p.estimated_traffic,
            } for d, p in profiles.items()},
            "best": {
                "authority": best_authority.domain,
                "most_backlinks": most_backlinks.domain,
                "most_referring_domains": most_referring.domain,
                "lowest_spam": lowest_spam.domain,
            },
            "rankings": {
                "authority": rank("domain_authority"),
                "backlinks": rank("total_backlinks"),
                "referring_domains": rank("referring_domains"),
                "spam_least": rank("spam_score", reverse=False),
            },
        }
