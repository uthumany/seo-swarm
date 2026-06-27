"""
SEO SWARM - Competitor Analysis Engine
Compare target site against competitor URLs for SEO gap analysis.
"""

import json
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional


@dataclass
class CompetitorSite:
    """Data for a single competitor site's SEO profile."""
    url: str
    title: str = ""
    meta: str = ""
    headers: List[str] = field(default_factory=list)
    word_count: int = 0
    keywords: List[str] = field(default_factory=list)


@dataclass
class CompetitorGap:
    """Represents a gap between target and a single competitor."""
    competitor_url: str
    target_missing_keywords: List[str] = field(default_factory=list)
    competitor_only_headers: List[str] = field(default_factory=list)
    competitor_only_meta_keywords: List[str] = field(default_factory=list)
    word_count_difference: int = 0
    title_difference: str = ""


@dataclass
class CompetitorReport:
    """Full competitor comparison report."""
    target: CompetitorSite
    competitors: List[CompetitorSite] = field(default_factory=list)
    gaps: List[CompetitorGap] = field(default_factory=list)
    scores: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to JSON-serializable dictionary."""
        return {
            "target": asdict(self.target),
            "competitors": [asdict(c) for c in self.competitors],
            "gaps": [asdict(g) for g in self.gaps],
            "scores": self.scores,
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize report to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)


class CompetitorEngine:
    """Analyze target site against competitor URLs for SEO gaps."""

    def __init__(self):
        # English stopwords for keyword extraction
        self._stopwords = {
            "the", "is", "in", "at", "of", "a", "an", "and", "or", "to",
            "for", "on", "with", "by", "it", "as", "be", "are", "was",
            "were", "been", "this", "that", "from", "but", "not", "we",
            "they", "you", "he", "she", "his", "her", "its", "their",
            "can", "will", "all", "has", "have", "do", "does", "did",
            "so", "if", "no", "up", "out", "about", "into", "over",
            "after", "before", "between", "just", "than", "then", "also",
            "very", "too", "only", "some", "any", "each", "every",
            "both", "few", "more", "most", "other", "much", "such",
            "here", "there", "when", "where", "why", "how", "which",
            "who", "whom", "what",
        }

    def _extract_keywords(self, text: str, min_length: int = 3) -> List[str]:
        """Extract meaningful keywords from text, filtering stopwords."""
        words = text.lower().split()
        keywords = []
        for w in words:
            # Strip non-alpha chars and normalize
            clean = "".join(c for c in w if c.isalpha())
            if len(clean) >= min_length and clean not in self._stopwords:
                keywords.append(clean)
        # Deduplicate preserving order
        seen = set()
        unique = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique.append(kw)
        return unique

    def _score_site(self, site: CompetitorSite) -> float:
        """Compute a simple SEO score for a site (0-100)."""
        score = 0.0
        # Title present and reasonable length (10-60 chars ideal)
        title_len = len(site.title)
        if title_len > 0:
            score += 15.0
            if 20 <= title_len <= 60:
                score += 15.0
            elif 10 <= title_len <= 70:
                score += 10.0

        # Meta description present and length (50-160 chars ideal)
        meta_len = len(site.meta)
        if meta_len > 0:
            score += 10.0
            if 50 <= meta_len <= 160:
                score += 10.0

        # H1 headers present
        if site.headers:
            score += 15.0
            if len(site.headers) == 1:
                score += 5.0  # Best practice: one H1
        else:
            score -= 5.0

        # Word count (substantial content)
        if site.word_count >= 300:
            score += 15.0
            if site.word_count >= 1000:
                score += 5.0
        elif site.word_count >= 100:
            score += 7.0
        else:
            score -= 5.0

        # Keywords (at least 5 unique meaningful keywords)
        kw_count = len(site.keywords)
        if kw_count >= 10:
            score += 10.0
        elif kw_count >= 5:
            score += 5.0

        return max(0.0, min(100.0, score))

    def compare(self, target: str, competitors: List[str]) -> CompetitorReport:
        """Compare target site against competitor URLs.

        Args:
            target: URL or domain name of the target site to analyze.
            competitors: List of competitor URLs or domain names.

        Returns:
            CompetitorReport with full comparison data.
        """
        # Build target site profile
        target_site = self._build_profile(target)

        # Build competitor profiles
        competitor_sites = [self._build_profile(url) for url in competitors]

        # Analyze gaps between target and each competitor
        gaps = []
        for comp_site in competitor_sites:
            gap = self._analyze_gap(target_site, comp_site)
            gaps.append(gap)

        # Compute scores
        scores = {
            "target": self._score_site(target_site),
        }
        for comp_site in competitor_sites:
            key = comp_site.url
            scores[key] = self._score_site(comp_site)

        return CompetitorReport(
            target=target_site,
            competitors=competitor_sites,
            gaps=gaps,
            scores=scores,
        )

    def _build_profile(self, url: str) -> CompetitorSite:
        """Build a CompetitorSite profile from a URL/domain name."""
        # Strip protocol prefix for display
        domain = url
        for prefix in ("https://", "http://"):
            if domain.startswith(prefix):
                domain = domain[len(prefix):]

        # Simulated page content based on domain
        site = CompetitorSite(url=url)

        # Generate a simulated profile (in production, this would crawl the site)
        import hashlib
        hash_val = int(hashlib.md5(url.encode()).hexdigest(), 16)

        # Title derived from domain
        parts = domain.split(".")
        name = parts[0].capitalize() if parts else domain
        site.title = f"{name} - {'Official Website' if hash_val % 3 == 0 else 'Home'}"

        # Meta description
        meta_options = [
            f"Welcome to {domain}. Your trusted source for {name.lower()} products and services.",
            f"{name} is the leading provider of quality services. Explore our offerings today.",
            f"Discover {name} — the best {name.lower()} resource online. Visit {domain} now.",
        ]
        site.meta = meta_options[hash_val % 3]

        # Headers
        header_sets = [
            [f"Welcome to {name}"],
            [f"{name} Official Site"],
            [f"Discover {name}"],
        ]
        site.headers = header_sets[hash_val % 3]

        # Word count (300-2000 range)
        site.word_count = 300 + (hash_val % 1700)

        # Keywords extracted from title + meta + headers
        all_text = f"{site.title} {site.meta} {' '.join(site.headers)}"
        site.keywords = self._extract_keywords(all_text)

        return site

    def _analyze_gap(
        self, target: CompetitorSite, competitor: CompetitorSite
    ) -> CompetitorGap:
        """Analyze what the competitor has that the target doesn't."""
        target_kws = set(target.keywords)
        comp_kws = set(competitor.keywords)

        # Keywords competitor has that target doesn't
        missing_kws = sorted(comp_kws - target_kws)

        # Overlap for reporting
        overlap = target_kws & comp_kws
        overlap_ratio = len(overlap) / max(len(comp_kws), 1) if comp_kws else 0.0

        # Headers competitor has that target doesn't
        target_headers_set = set(h.lower() for h in target.headers)
        comp_headers_set = set(h.lower() for h in competitor.headers)
        competitor_only_headers = sorted(comp_headers_set - target_headers_set)

        # Meta keyword differences
        target_meta_kws = set(self._extract_keywords(target.meta))
        comp_meta_kws = set(self._extract_keywords(competitor.meta))
        comp_only_meta = sorted(comp_meta_kws - target_meta_kws)

        return CompetitorGap(
            competitor_url=competitor.url,
            target_missing_keywords=missing_kws,
            competitor_only_headers=competitor_only_headers,
            competitor_only_meta_keywords=comp_only_meta,
            word_count_difference=competitor.word_count - target.word_count,
            title_difference=(
                competitor.title if competitor.title != target.title else ""
            ),
        )

    def keyword_overlap(
        self, target: str, competitor: str
    ) -> Dict[str, Any]:
        """Quick keyword overlap analysis between two sites.

        Args:
            target: Target site URL/domain.
            competitor: Competitor site URL/domain.

        Returns:
            Dict with overlap percentage, shared keywords, and unique keywords.
        """
        target_kws = set(self._build_profile(target).keywords)
        comp_kws = set(self._build_profile(competitor).keywords)
        shared = sorted(target_kws & comp_kws)
        total_unique = target_kws | comp_kws

        return {
            "target_url": target,
            "competitor_url": competitor,
            "target_keyword_count": len(target_kws),
            "competitor_keyword_count": len(comp_kws),
            "shared_keywords": shared,
            "shared_count": len(shared),
            "total_unique_keywords": len(total_unique),
            "overlap_percentage": round(
                len(shared) / max(len(total_unique), 1) * 100, 1
            ),
            "target_unique": sorted(target_kws - comp_kws),
            "competitor_unique": sorted(comp_kws - target_kws),
        }


# ---------------------------------------------------------------------------
# Runnable test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    engine = CompetitorEngine()
    target_url = "https://myseosite.com"
    competitors = [
        "https://competitor1.com",
        "https://competitor2.com",
        "https://competitor3.com",
    ]

    # Full comparison
    report = engine.compare(target_url, competitors)
    print("=" * 60)
    print(" COMPETITOR ANALYSIS REPORT")
    print("=" * 60)
    print(report.to_json())

    # Keyword overlap
    print("\n" + "=" * 60)
    print(" KEYWORD OVERLAP ANALYSIS")
    print("=" * 60)
    for comp in competitors:
        overlap = engine.keyword_overlap(target_url, comp)
        print(f"\n{comp}:")
        print(f"  Shared: {overlap['shared_count']}/{overlap['total_unique_keywords']} "
              f"({overlap['overlap_percentage']}%)")
        print(f"  Competitor unique: {overlap['competitor_unique'][:5]}...")
