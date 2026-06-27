"""
SEO SWARM - Skill Loader
Loads, installs, and manages preloaded SEO agent skills from GitHub repositories.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional


# Preloaded SEO skill repositories
SEO_SKILLS = [
    {
        "name": "SEO Audit Skill",
        "url": "https://github.com/seo-skills/seo-audit-skill",
        "category": "audit",
        "description": "Automated SEO auditing of websites: technical SEO, content, performance, security.",
    },
    {
        "name": "Claude SEO",
        "url": "https://github.com/AgricIDaniel/claude-seo",
        "category": "analysis",
        "description": "Comprehensive SEO analysis across all industries with parallel sub-skills and specialist agents.",
    },
    {
        "name": "Antigravity Awesome Skills",
        "url": "https://github.com/sickn33/antigravity-awesome-skills",
        "category": "library",
        "description": "Massive library of 1,500+ reusable SKILL.md playbooks including SEO and marketing bundles.",
    },
    {
        "name": "Tech SEO Audit Skill",
        "url": "https://github.com/Suganthan-Mohanadasan/tech-seo-audit-skill",
        "category": "technical",
        "description": "Comprehensive technical SEO audits analyzing crawl data with prioritized findings.",
    },
    {
        "name": "Ecommerce SEO Audit Skill",
        "url": "https://github.com/affilino/ecommerce-seo-audit-skill",
        "category": "ecommerce",
        "description": "Professional ecommerce SEO audits for Shopify and other ecommerce platforms.",
    },
    {
        "name": "Claude SEO AI",
        "url": "https://github.com/Hainrixz/claude-seo-ai",
        "category": "dual-audit",
        "description": "Audits on two axes: classic SEO and AI-search/Generative Engine Optimization (GEO/AEO).",
    },
    {
        "name": "Local SEO Skills",
        "url": "https://github.com/garrettjsmith/localseoskills",
        "category": "local",
        "description": "Local SEO expert with local search visibility, tool integrations, and automation templates.",
    },
    {
        "name": "Citedy SEO Agent",
        "url": "https://github.com/citedy/citedy-seo-agent",
        "category": "content",
        "description": "Complete SEO content marketing team: trend scouting, competitor analysis, multilingual articles.",
    },
    {
        "name": "Agentic SEO Skill",
        "url": "https://github.com/Bhanunamikaze/Agentic-SEO-Skill",
        "category": "analysis",
        "description": "LLM-first SEO analysis with specialized sub-skills for deep auditing and optimization.",
    },
    {
        "name": "SEO & GEO Claude Skills",
        "url": "https://github.com/aaron-he-zhu/seo-geo-claude-skills",
        "category": "geo",
        "description": "Zero-dependency Markdown skills for SEO and Generative Engine Optimization in Claude Code.",
    },
    {
        "name": "Agent SEO",
        "url": "https://github.com/ivankuznetsov/claude-seo",
        "category": "content",
        "description": "SEO content creation, analysis, optimization including topic research and humanizing AI content.",
    },
    {
        "name": "Agentkit SEO",
        "url": "https://github.com/agentkit-seo/agentkit-seo",
        "category": "aco",
        "description": "Agent Context Optimization (ACO) ensuring content is optimized for AI agents and LLMs.",
    },
    {
        "name": "Ultimate SEO + GEO",
        "url": "https://github.com/mykpono/ultimate-seo-geo",
        "category": "comprehensive",
        "description": "Definitive LLM-agnostic SEO agent skill combining traditional SEO with GEO for modern visibility.",
    },
    {
        "name": "SEO Plugin",
        "url": "https://github.com/danielrosehill/seo-plugin",
        "category": "workflow",
        "description": "SEO optimization workflows, meta tag management, and search engine optimization in Claude Code.",
    },
    {
        "name": "AI SEO Audit Agent",
        "url": "https://github.com/Ellen1889/ai-seo-audit-agent",
        "category": "audit",
        "description": "Auto-scrape and analyze webpage structures generating professional SEO audit reports in 2 minutes.",
    },
    {
        "name": "SEO Agents",
        "url": "https://github.com/0xnu/seo_agents",
        "category": "analysis",
        "description": "Dedicated SEO AI agents focused on comprehensive SEO analysis and data-driven recommendations.",
    },
    {
        "name": "SEO Mastery Agent Skills",
        "url": "https://github.com/kpab/seo-mastery-agent-skills",
        "category": "advanced",
        "description": "Structured data, advanced technical SEO, and comprehensive search optimization strategies.",
    },
    {
        "name": "Marketing Skills",
        "url": "https://github.com/coreyhaines31/marketingskills",
        "category": "marketing",
        "description": "Broad suite of marketing skills: CRO, copywriting, SEO, analytics, growth engineering.",
    },
    {
        "name": "Agentic SEO (Addy Osmani)",
        "url": "https://github.com/addyosmani/agentic-seo",
        "category": "aeo",
        "description": "Audit documentation and websites for Agentic Engine Optimization (AEO) for AI coding agents.",
    },
    {
        "name": "LangChain Hreflang Tools",
        "url": "https://github.com/diffen/langchain-hreflang",
        "category": "international",
        "description": "International SEO analysis with comprehensive LangChain tools for hreflang implementation.",
    },
]

# Browser automation skill repositories
BROWSER_SKILLS = [
    {"name": "Browser Use", "url": "https://github.com/browser-use/browser-use", "category": "browser"},
    {"name": "Vercel Agent Browser", "url": "https://github.com/vercel-labs/agent-browser", "category": "browser"},
    {"name": "Skyvern", "url": "https://github.com/Skyvern-AI/skyvern", "category": "browser"},
    {"name": "Stagehand", "url": "https://github.com/browserbase/stagehand", "category": "browser"},
    {"name": "Scrapling", "url": "https://github.com/D4Vinci/Scrapling", "category": "browser"},
    {"name": "LaVague", "url": "https://github.com/lavague-ai/LaVague", "category": "browser"},
    {"name": "OpenCLI", "url": "https://github.com/jackwener/opencli", "category": "browser"},
    {"name": "Agent Reach", "url": "https://github.com/Panniantong/agent-reach", "category": "browser"},
    {"name": "ZeroStep", "url": "https://github.com/Rat01047/zerostep-ai-playwright", "category": "browser"},
    {"name": "AIPex Browser Control", "url": "https://github.com/AIPexStudio/aipex-browser", "category": "browser"},
]


class SkillLoader:
    """Loads and manages preloaded SEO skills."""

    SKILLS_DIR = Path.home() / ".seo-swarm" / "skills"
    CACHE_FILE = SKILLS_DIR / "skills_cache.json"

    def __init__(self):
        self.SKILLS_DIR.mkdir(parents=True, exist_ok=True)
        self._seo_skills = SEO_SKILLS
        self._browser_skills = BROWSER_SKILLS

    def install_all(self) -> Dict[str, int]:
        """Install all preloaded skills (metadata only, not cloning repos)."""
        all_skills = self._seo_skills + self._browser_skills
        cache = {"installed_at": str(Path.home()), "skills": all_skills, "count": len(all_skills)}
        self.CACHE_FILE.write_text(json.dumps(cache, indent=2))
        print(f"  \u2705 Installed {len(all_skills)} skills ({len(self._seo_skills)} SEO + {len(self._browser_skills)} browser)")
        return {"seo": len(self._seo_skills), "browser": len(self._browser_skills)}

    def list_skills(self, search: Optional[str] = None) -> List[Dict]:
        """List installed skills with optional search filter."""
        skills = self._seo_skills + self._browser_skills
        if search:
            skills = [s for s in skills if search.lower() in s["name"].lower() or search.lower() in s.get("description", "").lower()]

        for s in skills:
            cat_color = {"audit": "\033[91m", "analysis": "\033[94m", "browser": "\033[93m",
                         "content": "\033[95m", "technical": "\033[92m", "local": "\033[96m"}.get(s["category"], "")
            print(f"  {cat_color}[{s['category']:12}]\033[0m {s['name']:<35} {s['description'][:70]}")
        return skills

    def get_skill(self, name: str) -> Optional[Dict]:
        """Get a specific skill by name."""
        for s in self._seo_skills + self._browser_skills:
            if s["name"].lower() == name.lower():
                return s
        return None

    def get_category_count(self) -> Dict[str, int]:
        """Get count of skills by category."""
        cats = {}
        for s in self._seo_skills + self._browser_skills:
            cats[s["category"]] = cats.get(s["category"], 0) + 1
        return cats
