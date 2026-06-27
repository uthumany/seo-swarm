"""
SEO SWARM - Agent Registry
Manages all 10 specialized SEO agents with their metadata, skills, and ASCII art.
"""

import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class SEOAgent:
    """A specialized SEO agent with ASCII art profile."""
    id: str
    name: str
    role: str
    emoji: str
    color: str  # ANSI color code
    description: str
    skills: List[str] = field(default_factory=list)
    ascii_art: str = ""
    status: str = "idle"  # idle, running, complete, error
    tasks_completed: int = 0
    confidence: float = 100.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "name": self.name, "role": self.role,
            "emoji": self.emoji, "color": self.color,
            "description": self.description, "skills": self.skills,
            "status": self.status, "tasks_completed": self.tasks_completed
        }


class AgentRegistry:
    """Registry of all 10 specialized SEO agents."""

    AGENTS = {
        "seo-strategist": {
            "name": "SEO Strategist",
            "role": "SEO Strategy & Roadmap",
            "emoji": "\U0001f9e0",  # brain
            "color": "bright_cyan",
            "description": "Develops the overall SEO roadmap, sets measurable KPIs, identifies target keywords and user intent, aligns search strategies with business goals, and prioritizes initiatives across web, mobile, and PWA platforms.",
            "skills": ["keyword-research", "competitive-analysis", "kpi-tracking", "seo-roadmap"],
        },
        "technical-seo": {
            "name": "Technical SEO Specialist",
            "role": "Technical SEO & Site Architecture",
            "emoji": "\U0001f527",  # wrench
            "color": "bright_green",
            "description": "Optimizes site architecture, crawlability, indexation, page speed, structured data, mobile-friendliness, and handles server logs, sitemaps, canonicalization, and JavaScript rendering audits.",
            "skills": ["site-audit", "crawl-analysis", "schema-markup", "pagespeed", "xml-sitemaps", "robots-txt"],
        },
        "content-seo": {
            "name": "Content SEO Specialist",
            "role": "Content Strategy & Optimization",
            "emoji": "\u270d\ufe0f",  # writing hand
            "color": "bright_magenta",
            "description": "Researches topic clusters and high-intent keywords, creates content briefs, optimizes on-page copy, meta tags, headings, and internal linking to satisfy search queries and align with user intent.",
            "skills": ["content-briefs", "topic-clusters", "meta-optimization", "internal-linking", "content-gap"],
        },
        "on-page-seo": {
            "name": "On-Page SEO Analyst",
            "role": "On-Page Element Optimization",
            "emoji": "\U0001f50d",  # magnifying glass
            "color": "bright_yellow",
            "description": "Audits individual page elements: title tags, meta descriptions, URL structures, header hierarchy, image alt text, content relevance, and internal link signals.",
            "skills": ["title-optimization", "meta-audit", "header-analysis", "alt-text", "url-optimization"],
        },
        "off-page-seo": {
            "name": "Off-Page SEO Specialist",
            "role": "Link Building & Authority",
            "emoji": "\U0001f517",  # link
            "color": "bright_blue",
            "description": "Builds domain authority through ethical link acquisition, digital PR, influencer partnerships, and brand mention management; monitors backlink profiles and disavows harmful links.",
            "skills": ["backlink-analysis", "outreach", "brand-mentions", "competitor-links", "disavow"],
        },
        "local-seo": {
            "name": "Local SEO Specialist",
            "role": "Local Search & Geo Optimization",
            "emoji": "\U0001f4cd",  # pin
            "color": "bright_red",
            "description": "Optimizes for geo-specific queries by managing Google Business Profiles, maintaining NAP consistency, developing localized content, and acquiring local reviews.",
            "skills": ["google-business", "nap-consistency", "local-citations", "review-management", "geo-targeting"],
        },
        "seo-developer": {
            "name": "SEO Developer",
            "role": "Technical Implementation & Code",
            "emoji": "\U0001f4bb",  # laptop
            "color": "bright_white",
            "description": "Implements technical SEO at code level: structured data markup, JavaScript rendering fixes, PWA progressive enhancement, service worker configs, Core Web Vitals and accessibility standards.",
            "skills": ["structured-data", "js-rendering", "core-web-vitals", "pwa-seo", "accessibility"],
        },
        "seo-analyst": {
            "name": "SEO Data Analyst",
            "role": "Data Analysis & Reporting",
            "emoji": "\U0001f4ca",  # chart
            "color": "cyan",
            "description": "Tracks, analyzes, and interprets SEO performance using analytics, Search Console, log files, and rank-tracking tools; conducts A/B testing and attribution modeling.",
            "skills": ["analytics", "search-console", "log-analysis", "rank-tracking", "ab-testing"],
        },
        "voice-search": {
            "name": "Voice Search Specialist",
            "role": "Voice & Conversational SEO",
            "emoji": "\U0001f399\ufe0f",  # microphone
            "color": "magenta",
            "description": "Focuses on conversational long-tail queries, NLP, FAQ and speakable schema markup, featured snippet targeting, and voice assistant traffic optimization.",
            "skills": ["voice-queries", "faq-schema", "featured-snippets", "nlp-optimization", "conversational-content"],
        },
        "mobile-pwa": {
            "name": "Mobile & PWA SEO Specialist",
            "role": "Mobile-First & PWA Optimization",
            "emoji": "\U0001f4f1",  # mobile phone
            "color": "green",
            "description": "Ensures mobile-first indexing compliance, fast loading on variable networks, responsive design, PWA installability and manifest signals, offline content discoverability.",
            "skills": ["mobile-first", "responsive-design", "pwa-manifest", "offline-seo", "amp-optimization"],
        },
    }

    @classmethod
    def get_all(cls) -> List[SEOAgent]:
        """Get all registered agents."""
        return [
            SEOAgent(id=aid, **data)
            for aid, data in cls.AGENTS.items()
        ]

    @classmethod
    def get(cls, agent_id: str) -> Optional[SEOAgent]:
        """Get a specific agent by ID."""
        data = cls.AGENTS.get(agent_id)
        if data:
            return SEOAgent(id=agent_id, **data)
        return None

    @classmethod
    def get_by_role(cls, role_keyword: str) -> List[SEOAgent]:
        """Find agents by role keyword."""
        results = []
        for aid, data in cls.AGENTS.items():
            if role_keyword.lower() in data["role"].lower() or \
               role_keyword.lower() in data["name"].lower():
                results.append(SEOAgent(id=aid, **data))
        return results

    @classmethod
    def list_ids(cls) -> List[str]:
        return list(cls.AGENTS.keys())

    @classmethod
    def count(cls) -> int:
        return len(cls.AGENTS)
