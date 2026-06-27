"""
SEO SWARM - Reporting Generator
Automated SEO report generator: produces single-file HTML reports with
inline CSS and responsive design, and Markdown reports from audit results.
Uses simple string templates — zero external dependencies.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ReportConfig:
    """Configuration for report generation."""

    title: str = "SEO Audit Report"
    include_summary: bool = True
    include_scorecards: bool = True
    include_findings: bool = True
    include_recommendations: bool = True
    color_brand_primary: str = "#2563eb"
    color_brand_secondary: str = "#1e40af"
    color_success: str = "#16a34a"
    color_warning: str = "#d97706"
    color_danger: str = "#dc2626"
    color_neutral: str = "#6b7280"


class ReportGenerator:
    """Generate SEO audit reports in HTML and Markdown formats.

    Produces self-contained HTML reports (inline CSS, responsive, no external
    dependencies) and clean Markdown reports with color-coded severity
    indicators from structured audit results.

    Usage:
        generator = ReportGenerator()
        path = generator.generate_html(results, "report.html")
        path = generator.generate_markdown(results, "report.md")
    """

    def __init__(self, config: Optional[ReportConfig] = None):
        """Initialize the report generator.

        Args:
            config: Optional ReportConfig to customize colors and sections.
        """
        self.config = config or ReportConfig()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_html(self, results: dict, output_path: str) -> str:
        """Generate a self-contained HTML SEO audit report.

        Produces a single-file HTML document with inline CSS, responsive layout,
        scorecards, findings, and recommendations. No external assets required.

        Args:
            results: Dictionary of audit results. Expected structure:
                {
                    "target": str,
                    "timestamp": float,
                    "scorecard": dict (ScorecardResult.to_dict()),
                    "agents": list of agent results,
                    "crawl_summary": dict,
                }
            output_path: File path to write the HTML report (e.g., "report.html").

        Returns:
            Absolute path to the generated report file.
        """
        cfg = self.config
        target = results.get("target", results.get("target_url", "Unknown"))
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{self._escape_html(cfg.title)} — {self._escape_html(target)}</title>
<style>
/* ==================================================================
   SEO SWARM Report — Inline Stylesheet (responsive, print-friendly)
   ================================================================== */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    background: #f8fafc; color: #1e293b; line-height: 1.6;
}}
.container {{ max-width: 960px; margin: 0 auto; padding: 2rem 1.5rem; }}

/* Header */
.header {{
    background: linear-gradient(135deg, {cfg.color_brand_primary}, {cfg.color_brand_secondary});
    color: #fff; padding: 2.5rem 2rem; border-radius: 12px; margin-bottom: 2rem;
}}
.header h1 {{ font-size: 2rem; font-weight: 700; margin-bottom: 0.25rem; }}
.header .meta {{ opacity: 0.9; font-size: 0.9rem; }}

/* Cards */
.card {{
    background: #fff; border-radius: 10px; padding: 1.5rem; margin-bottom: 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08); border: 1px solid #e2e8f0;
}}
.card h2 {{ font-size: 1.25rem; color: {cfg.color_brand_secondary}; margin-bottom: 1rem; }}

/* Score gauge */
.score-display {{
    display: flex; align-items: center; gap: 1.5rem; flex-wrap: wrap;
    padding: 1.5rem; background: #f1f5f9; border-radius: 10px;
}}
.score-circle {{
    width: 120px; height: 120px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 2.2rem; font-weight: 800; color: #fff;
    flex-shrink: 0;
}}
.score-circle.grade-a {{ background: {cfg.color_success}; }}
.score-circle.grade-b {{ background: #65a30d; }}
.score-circle.grade-c {{ background: {cfg.color_warning}; }}
.score-circle.grade-d {{ background: #ea580c; }}
.score-circle.grade-f {{ background: {cfg.color_danger}; }}

/* Dimension bars */
.dimension-bars {{ flex: 1; min-width: 250px; }}
.dim-bar {{ margin-bottom: 0.6rem; }}
.dim-bar .dim-label {{
    display: flex; justify-content: space-between;
    font-size: 0.85rem; font-weight: 600; margin-bottom: 0.15rem;
}}
.dim-bar .dim-track {{
    height: 10px; background: #e2e8f0; border-radius: 5px; overflow: hidden;
}}
.dim-bar .dim-fill {{
    height: 100%; border-radius: 5px; transition: width 0.6s;
}}
.dim-fill.excellent {{ background: {cfg.color_success}; }}
.dim-fill.good {{ background: #65a30d; }}
.dim-fill.fair {{ background: {cfg.color_warning}; }}
.dim-fill.poor {{ background: {cfg.color_danger}; }}

/* Tables */
table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
th, td {{ padding: 0.6rem 0.75rem; text-align: left; border-bottom: 1px solid #e2e8f0; }}
th {{ background: #f8fafc; font-weight: 700; color: {cfg.color_brand_secondary}; }}

/* Severity badges */
.badge {{
    display: inline-block; padding: 0.15rem 0.5rem; border-radius: 4px;
    font-size: 0.75rem; font-weight: 700; text-transform: uppercase;
}}
.badge.critical {{ background: #fecaca; color: #991b1b; }}
.badge.high     {{ background: #fed7aa; color: #9a3412; }}
.badge.medium   {{ background: #fef08a; color: #854d0e; }}
.badge.low      {{ background: #dbeafe; color: #1e40af; }}
.badge.info     {{ background: #e2e8f0; color: #475569; }}
.badge.success  {{ background: #bbf7d0; color: #166534; }}

/* Recommendations list */
.rec-list {{ list-style: none; }}
.rec-list li {{
    padding: 0.5rem 0.75rem; margin-bottom: 0.4rem;
    background: #fef2f2; border-left: 4px solid {cfg.color_danger};
    border-radius: 0 6px 6px 0; font-size: 0.9rem;
}}
.rec-list li::before {{ content: "⚠ "; }}

/* Pass/fail checks */
.check-item {{
    display: flex; align-items: center; gap: 0.5rem;
    padding: 0.35rem 0; font-size: 0.85rem;
}}
.check-item.pass::before {{ content: "✅"; }}
.check-item.fail::before {{ content: "❌"; }}

/* Summary grid */
.summary-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1rem;
}}
.summary-box {{
    padding: 1rem; border-radius: 8px; text-align: center; background: #f1f5f9;
}}
.summary-box .box-value {{
    font-size: 1.8rem; font-weight: 800; color: {cfg.color_brand_primary};
}}
.summary-box .box-label {{ font-size: 0.8rem; color: {cfg.color_neutral}; }}

/* Footer */
.footer {{
    text-align: center; margin-top: 2rem; padding: 1.5rem;
    color: {cfg.color_neutral}; font-size: 0.8rem;
}}

/* Print styles */
@media print {{
    body {{ background: #fff; }}
    .card {{ box-shadow: none; border: 1px solid #ccc; }}
    .header {{ background: #1e293b !important; -webkit-print-color-adjust: exact; }}
}}

/* Responsive */
@media (max-width: 600px) {{
    .container {{ padding: 1rem; }}
    .score-display {{ flex-direction: column; align-items: center; }}
    .header h1 {{ font-size: 1.4rem; }}
}}
</style>
</head>
<body>
<div class="container">

<!-- Header -->
<div class="header">
    <h1>{self._escape_html(cfg.title)}</h1>
    <div class="meta">
        Target: <strong>{self._escape_html(target)}</strong> &nbsp;|&nbsp;
        Generated: {now}
    </div>
</div>
"""

        # --- Summary section ---
        if cfg.include_summary:
            html += self._build_html_summary(results)

        # --- Scorecards ---
        if cfg.include_scorecards:
            html += self._build_html_scorecard(results, cfg)

        # --- Findings ---
        if cfg.include_findings:
            html += self._build_html_findings(results)

        # --- Recommendations ---
        if cfg.include_recommendations:
            html += self._build_html_recommendations(results, cfg)

        # Footer
        html += f"""
<div class="footer">
    <p>Generated by <strong>SEO SWARM</strong> — Autonomous SEO Agents</p>
    <p>Report timestamp: {now}</p>
</div>

</div><!-- /container -->
</body>
</html>
"""
        # Write file
        out_path = Path(output_path).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html, encoding="utf-8")
        return str(out_path)

    def generate_markdown(self, results: dict, output_path: str) -> str:
        """Generate a Markdown SEO audit report.

        Produces a clean, structured Markdown report with severity indicators,
        scorecards as ASCII tables, and actionable recommendations.

        Args:
            results: Dictionary of audit results (same structure as generate_html).
            output_path: File path to write the Markdown report (e.g., "report.md").

        Returns:
            Absolute path to the generated report file.
        """
        target = results.get("target", results.get("target_url", "Unknown"))
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        md = f"""# {self.config.title}

**Target:** `{target}`  
**Generated:** {now}  
**Tool:** SEO SWARM — Autonomous SEO Agents

---

"""
        # --- Summary ---
        if self.config.include_summary:
            md += self._build_md_summary(results)

        # --- Scorecards ---
        if self.config.include_scorecards:
            md += self._build_md_scorecard(results)

        # --- Findings ---
        if self.config.include_findings:
            md += self._build_md_findings(results)

        # --- Recommendations ---
        if self.config.include_recommendations:
            md += self._build_md_recommendations(results)

        # Footer
        md += f"""
---

*Report generated by [SEO SWARM](https://github.com/uthumany/seo-swarm) at {now}*
"""

        out_path = Path(output_path).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md, encoding="utf-8")
        return str(out_path)

    # ------------------------------------------------------------------
    # HTML section builders
    # ------------------------------------------------------------------

    def _build_html_summary(self, results: dict) -> str:
        """Build the HTML summary section."""
        scorecard = results.get("scorecard", {})
        total_score = scorecard.get("total_score", "—")
        letter_grade = scorecard.get("letter_grade", "—")

        crawl = results.get("crawl_summary", {})
        pages = crawl.get("pages_crawled", "—") if crawl else "—"
        broken = len(crawl.get("broken_links", [])) if crawl else "—"

        agents = results.get("agents", [])
        agents_count = len(agents)
        total_findings = sum(len(a.get("findings", [])) for a in agents)

        return f"""
<div class="card">
    <h2>📊 Summary</h2>
    <div class="summary-grid">
        <div class="summary-box">
            <div class="box-value">{total_score}</div>
            <div class="box-label">Total Score / 100</div>
        </div>
        <div class="summary-box">
            <div class="box-value">{letter_grade}</div>
            <div class="box-label">Grade</div>
        </div>
        <div class="summary-box">
            <div class="box-value">{pages}</div>
            <div class="box-label">Pages Crawled</div>
        </div>
        <div class="summary-box">
            <div class="box-value">{broken}</div>
            <div class="box-label">Broken Links</div>
        </div>
        <div class="summary-box">
            <div class="box-value">{agents_count}</div>
            <div class="box-label">Agents Used</div>
        </div>
        <div class="summary-box">
            <div class="box-value">{total_findings}</div>
            <div class="box-label">Total Findings</div>
        </div>
    </div>
</div>
"""

    def _build_html_scorecard(self, results: dict, cfg: ReportConfig) -> str:
        """Build HTML scorecard with gauge and dimension bars."""
        scorecard = results.get("scorecard", {})
        if not scorecard:
            return ""

        total_score = scorecard.get("total_score", 0)
        letter_grade = scorecard.get("letter_grade", "—")
        dimensions = scorecard.get("dimensions", {})

        # Grade circle class
        grade_class = "grade-f"
        if letter_grade.startswith("A"):
            grade_class = "grade-a"
        elif letter_grade.startswith("B"):
            grade_class = "grade-b"
        elif letter_grade.startswith("C"):
            grade_class = "grade-c"
        elif letter_grade.startswith("D"):
            grade_class = "grade-d"

        # Dimension bars
        dim_bars = ""
        for key, dim in dimensions.items():
            score = dim.get("score", 0)
            name = dim.get("name", key)
            pct = min(100, max(0, score))
            fill_class = (
                "excellent" if pct >= 80 else
                "good" if pct >= 60 else
                "fair" if pct >= 40 else
                "poor"
            )
            dim_bars += f"""<div class="dim-bar">
                <div class="dim-label"><span>{self._escape_html(name)}</span><span>{score:.0f}</span></div>
                <div class="dim-track"><div class="dim-fill {fill_class}" style="width:{pct}%"></div></div>
            </div>\n"""

        return f"""
<div class="card">
    <h2>🏆 SEO Scorecard</h2>
    <div class="score-display">
        <div class="score-circle {grade_class}">{total_score:.0f}</div>
        <div class="dimension-bars">
            {dim_bars}
        </div>
    </div>
</div>
"""

    def _build_html_findings(self, results: dict) -> str:
        """Build HTML findings table from agent results."""
        agents = results.get("agents", [])
        if not agents:
            return ""

        rows = ""
        for agent in agents:
            agent_name = agent.get("agent_name", agent.get("agent_id", "Unknown"))
            findings = agent.get("findings", [])
            status = agent.get("status", "unknown")
            for f in findings:
                sev = f.get("severity", "info").lower()
                rows += f"""<tr>
                    <td>{self._escape_html(agent_name)}</td>
                    <td><span class="badge {sev}">{sev}</span></td>
                    <td>{self._escape_html(f.get("category", ""))}</td>
                    <td>{self._escape_html(f.get("finding", ""))}</td>
                </tr>\n"""

        if not rows:
            return ""

        return f"""
<div class="card">
    <h2>🔍 Detailed Findings</h2>
    <div style="overflow-x:auto;">
    <table>
        <thead><tr>
            <th>Agent</th><th>Severity</th><th>Category</th><th>Finding</th>
        </tr></thead>
        <tbody>{rows}</tbody>
    </table>
    </div>
</div>
"""

    def _build_html_recommendations(self, results: dict, cfg: ReportConfig) -> str:
        """Build HTML recommendations list."""
        # Collect from scorecard
        scorecard = results.get("scorecard", {})
        recs = list(scorecard.get("recommendations", []))

        # Collect from agents
        agents = results.get("agents", [])
        for agent in agents:
            findings = agent.get("findings", [])
            for f in findings:
                if f.get("severity", "").lower() in ("high", "critical"):
                    rec = f.get("finding", "")
                    if rec and rec not in recs:
                        recs.append(rec)

        if not recs:
            return ""

        items = "\n".join(f"<li>{self._escape_html(r)}</li>" for r in recs[:20])

        return f"""
<div class="card">
    <h2>⚠️ Recommendations</h2>
    <ul class="rec-list">{items}</ul>
</div>
"""

    # ------------------------------------------------------------------
    # Markdown section builders
    # ------------------------------------------------------------------

    def _build_md_summary(self, results: dict) -> str:
        """Build Markdown summary."""
        scorecard = results.get("scorecard", {})
        total_score = scorecard.get("total_score", "—")
        letter_grade = scorecard.get("letter_grade", "—")

        crawl = results.get("crawl_summary", {})
        pages = crawl.get("pages_crawled", "—") if crawl else "—"
        broken = len(crawl.get("broken_links", [])) if crawl else "—"

        agents = results.get("agents", [])
        total_findings = sum(len(a.get("findings", [])) for a in agents)

        return f"""## 📊 Summary

| Metric | Value |
|--------|-------|
| **Total Score** | {total_score}/100 |
| **Grade** | {letter_grade} |
| **Pages Crawled** | {pages} |
| **Broken Links** | {broken} |
| **Agents Used** | {len(agents)} |
| **Total Findings** | {total_findings} |

"""

    def _build_md_scorecard(self, results: dict) -> str:
        """Build Markdown scorecard table."""
        scorecard = results.get("scorecard", {})
        if not scorecard:
            return ""

        total_score = scorecard.get("total_score", 0)
        letter_grade = scorecard.get("letter_grade", "—")
        dimensions = scorecard.get("dimensions", {})

        md = f"""## 🏆 SEO Scorecard

**Overall Score:** {total_score:.0f}/100 ({letter_grade})

| Dimension | Score | Weight | Bar |
|-----------|-------|--------|-----|
"""
        for key, dim in dimensions.items():
            score = dim.get("score", 0)
            name = dim.get("name", key)
            weight = dim.get("weight", 0)
            bar = "█" * int(score / 5) + "░" * (20 - int(score / 5))
            md += f"| {name} | {score:.0f} | {weight:.0%} | {bar} |\n"

        return md + "\n"

    def _build_md_findings(self, results: dict) -> str:
        """Build Markdown findings by severity."""
        agents = results.get("agents", [])
        if not agents:
            return ""

        # Group by severity
        sev_map: Dict[str, List[Dict[str, Any]]] = {
            "critical": [], "high": [], "medium": [], "low": [], "info": [],
        }
        for agent in agents:
            agent_name = agent.get("agent_name", agent.get("agent_id", "Unknown"))
            for f in agent.get("findings", []):
                sev = f.get("severity", "info").lower()
                if sev not in sev_map:
                    sev = "info"
                sev_map[sev].append({"agent": agent_name, **f})

        icons = {
            "critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵", "info": "⚪",
        }

        md = "## 🔍 Findings by Severity\n\n"
        for sev in ("critical", "high", "medium", "low", "info"):
            items = sev_map.get(sev, [])
            if not items:
                continue
            icon = icons.get(sev, "")
            md += f"### {icon} {sev.upper()} ({len(items)})\n\n"
            for item in items:
                md += f"- **[{item.get('category', 'general')}]** {item.get('finding', '')} "
                md += f"_(Agent: {item['agent']})_\n"
            md += "\n"

        return md

    def _build_md_recommendations(self, results: dict) -> str:
        """Build Markdown recommendations."""
        scorecard = results.get("scorecard", {})
        recs = list(scorecard.get("recommendations", []))
        agents = results.get("agents", [])
        for agent in agents:
            for f in agent.get("findings", []):
                if f.get("severity", "").lower() in ("high", "critical"):
                    rec = f.get("finding", "")
                    if rec and rec not in recs:
                        recs.append(rec)

        if not recs:
            return ""

        md = "## ⚠️ Priority Recommendations\n\n"
        for i, rec in enumerate(recs[:20], 1):
            md += f"{i}. {rec}\n"
        return md + "\n"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _escape_html(text: str) -> str:
        """Escape HTML special characters.

        Args:
            text: Raw string that may contain HTML special characters.

        Returns:
            HTML-safe escaped string.
        """
        return (
            str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )


# ------------------------------------------------------------------
# Runnable test (python -m seo_swarm.reporting.generator)
# ------------------------------------------------------------------
if __name__ == "__main__":
    import tempfile

    generator = ReportGenerator()

    # Build sample results that exercise all sections
    sample_results = {
        "target": "https://example.com",
        "timestamp": time.time(),
        "scorecard": {
            "total_score": 78.4,
            "letter_grade": "C+",
            "dimensions": {
                "technical_score": {
                    "name": "Technical SEO", "score": 85.0, "weight": 0.25,
                    "recommendations": ["Fix broken links", "Add sitemap"],
                },
                "content_score": {
                    "name": "Content Quality", "score": 72.0, "weight": 0.30,
                    "recommendations": ["Improve title tags", "Add meta descriptions"],
                },
                "performance_score": {
                    "name": "Core Web Vitals", "score": 68.0, "weight": 0.20,
                    "recommendations": ["Reduce LCP", "Eliminate layout shifts"],
                },
                "offpage_score": {
                    "name": "Off-Page & Authority", "score": 82.0, "weight": 0.15,
                    "recommendations": [],
                },
                "mobile_score": {
                    "name": "Mobile Friendliness", "score": 91.0, "weight": 0.10,
                    "recommendations": [],
                },
            },
            "recommendations": [
                "Fix broken links", "Add sitemap",
                "Improve title tags", "Add meta descriptions",
                "Reduce LCP below 2.5s",
            ],
        },
        "crawl_summary": {
            "pages_crawled": 24,
            "total_links_found": 312,
            "broken_links": [{"url": "/dead-page", "status": 404}],
        },
        "agents": [
            {
                "agent_id": "technical-seo",
                "agent_name": "Technical SEO Agent",
                "status": "success",
                "score": 85.0,
                "findings": [
                    {"severity": "high", "category": "crawlability",
                     "finding": "Found 5 pages with crawl issues"},
                    {"severity": "medium", "category": "performance",
                     "finding": "Page speed score: 68/100 - optimization needed"},
                    {"severity": "low", "category": "structured-data",
                     "finding": "Missing schema markup on key pages"},
                ],
            },
            {
                "agent_id": "content-seo",
                "agent_name": "Content SEO Agent",
                "status": "success",
                "score": 72.0,
                "findings": [
                    {"severity": "medium", "category": "content-gap",
                     "finding": "Identified 7 content gaps vs competitors"},
                    {"severity": "high", "category": "meta-tags",
                     "finding": "3 pages have duplicate or missing title tags"},
                ],
            },
            {
                "agent_id": "off-page-seo",
                "agent_name": "Off-Page SEO Agent",
                "status": "success",
                "score": 78.0,
                "findings": [
                    {"severity": "info", "category": "backlinks",
                     "finding": "Domain authority score: 42"},
                    {"severity": "medium", "category": "toxic-links",
                     "finding": "Detected 2 potentially toxic backlinks"},
                ],
            },
        ],
    }

    # Test HTML generation
    with tempfile.TemporaryDirectory() as tmpdir:
        html_path = Path(tmpdir) / "seo_report.html"
        result_path = generator.generate_html(sample_results, str(html_path))
        print("=" * 60)
        print(f"  HTML Report generated: {result_path}")
        content = Path(result_path).read_text(encoding="utf-8")
        print(f"  File size: {len(content):,} bytes")
        print(f"  Lines: {len(content.splitlines())}")
        print("  Sections found:")
        for section in ["Summary", "Scorecard", "Findings", "Recommendations"]:
            present = section.lower() in content.lower()
            print(f"    {section}: {'✓' if present else '✗'}")

    # Test Markdown generation
    with tempfile.TemporaryDirectory() as tmpdir:
        md_path = Path(tmpdir) / "seo_report.md"
        result_path = generator.generate_markdown(sample_results, str(md_path))
        print(f"\n  Markdown Report generated: {result_path}")
        content = Path(result_path).read_text(encoding="utf-8")
        print(f"  File size: {len(content):,} bytes")
        print(f"  Lines: {len(content.splitlines())}")
        print("  Sections found:")
        for section in ["Summary", "Scorecard", "Findings", "Recommendations"]:
            present = section.lower() in content.lower()
            print(f"    {section}: {'✓' if present else '✗'}")

    # Test custom config
    custom_config = ReportConfig(
        title="Custom SEO Analysis",
        color_brand_primary="#7c3aed",
        color_brand_secondary="#6d28d9",
    )
    custom_gen = ReportGenerator(config=custom_config)
    with tempfile.TemporaryDirectory() as tmpdir:
        html_path = Path(tmpdir) / "custom_report.html"
        result_path = custom_gen.generate_html(sample_results, str(html_path))
        content = Path(result_path).read_text(encoding="utf-8")
        print(f"\n  Custom-themed HTML Report: {result_path}")
        print(f"  Brand color present: {'#7c3aed' in content}")

    print("\n" + "=" * 60)
    print("  Report generator test complete.")
