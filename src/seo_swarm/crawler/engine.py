"""
SEO SWARM - Crawler Engine
Real HTTP web crawler using only urllib/ssl (stdlib — no requests library).
Respects robots.txt, extracts on-page SEO data, and supports configurable
crawl depth with parallel fetching.
"""

from __future__ import annotations

import concurrent.futures
import re
import ssl
import time
import urllib.parse
import urllib.request
import urllib.robotparser
from collections import deque
from dataclasses import dataclass, field
from http.client import HTTPResponse
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from urllib.error import HTTPError, URLError


@dataclass
class OnPageData:
    """Structured on-page SEO data extracted from a single URL."""

    url: str
    status_code: int = 0
    title: str = ""
    title_length: int = 0
    meta_description: str = ""
    meta_description_length: int = 0
    meta_keywords: str = ""
    canonical_url: str = ""
    og_title: str = ""
    og_description: str = ""
    og_image: str = ""
    twitter_card: str = ""
    h1: List[str] = field(default_factory=list)
    h2: List[str] = field(default_factory=list)
    h3: List[str] = field(default_factory=list)
    h4: List[str] = field(default_factory=list)
    h5: List[str] = field(default_factory=list)
    h6: List[str] = field(default_factory=list)
    links: List[Dict[str, str]] = field(default_factory=list)
    internal_links: int = 0
    external_links: int = 0
    images: List[Dict[str, str]] = field(default_factory=list)
    images_with_alt: int = 0
    images_missing_alt: int = 0
    word_count: int = 0
    content_type: str = ""
    load_time_ms: float = 0.0
    error: str = ""

    @property
    def h1_count(self) -> int:
        return len(self.h1)

    @property
    def h2_count(self) -> int:
        return len(self.h2)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "url": self.url,
            "status_code": self.status_code,
            "title": self.title,
            "title_length": self.title_length,
            "meta_description": self.meta_description,
            "meta_description_length": self.meta_description_length,
            "meta_keywords": self.meta_keywords,
            "canonical_url": self.canonical_url,
            "og_title": self.og_title,
            "og_description": self.og_description,
            "og_image": self.og_image,
            "twitter_card": self.twitter_card,
            "h1": self.h1,
            "h2": self.h2,
            "h3": self.h3,
            "h4": self.h4,
            "h5": self.h5,
            "h6": self.h6,
            "h1_count": self.h1_count,
            "h2_count": self.h2_count,
            "links": self.links,
            "internal_links": self.internal_links,
            "external_links": self.external_links,
            "images": self.images,
            "images_with_alt": self.images_with_alt,
            "images_missing_alt": self.images_missing_alt,
            "word_count": self.word_count,
            "content_type": self.content_type,
            "load_time_ms": round(self.load_time_ms, 1),
            "error": self.error,
        }


@dataclass
class CrawlResult:
    """Complete crawl result from CrawlerEngine.crawl()."""

    start_url: str
    pages_crawled: int = 0
    pages: List[OnPageData] = field(default_factory=list)
    total_links_found: int = 0
    broken_links: List[Dict[str, Any]] = field(default_factory=list)
    robots_txt_found: bool = False
    sitemap_found: bool = False
    uses_https: bool = False
    total_duration: float = 0.0
    errors: List[str] = field(default_factory=list)
    crawl_depth_reached: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "start_url": self.start_url,
            "pages_crawled": self.pages_crawled,
            "pages": [p.to_dict() for p in self.pages],
            "total_links_found": self.total_links_found,
            "broken_links": self.broken_links,
            "robots_txt_found": self.robots_txt_found,
            "sitemap_found": self.sitemap_found,
            "uses_https": self.uses_https,
            "total_duration": round(self.total_duration, 2),
            "errors": self.errors,
            "crawl_depth_reached": self.crawl_depth_reached,
        }


class CrawlerEngine:
    """Real HTTP web crawler using stdlib urllib with robots.txt compliance.

    Crawls websites respecting robots.txt directives, extracts on-page SEO
    data (titles, meta tags, headings, links, images), and supports configurable
    crawl depth and max pages with parallel fetching via concurrent.futures.

    Usage:
        engine = CrawlerEngine(user_agent="SEO-Swarm/1.0", timeout=10)
        result = engine.crawl("https://example.com", max_pages=20, max_depth=2)
        for page in result.pages:
            print(page.title, page.meta_description)
    """

    DEFAULT_USER_AGENT = "SEO-Swarm/1.0 (SEO analysis crawler; +https://github.com/uthumany/seo-swarm)"
    DEFAULT_TIMEOUT = 15
    DEFAULT_MAX_WORKERS = 5

    def __init__(
        self,
        user_agent: str = DEFAULT_USER_AGENT,
        timeout: int = DEFAULT_TIMEOUT,
        max_workers: int = DEFAULT_MAX_WORKERS,
        respect_robots: bool = True,
        verify_ssl: bool = True,
    ):
        """Initialize the crawler engine.

        Args:
            user_agent: User-Agent header string to send with requests.
            timeout: Request timeout in seconds.
            max_workers: Maximum number of parallel fetch workers.
            respect_robots: If True, check and respect robots.txt before crawling.
            verify_ssl: If True, validate SSL certificates. Set to False for
                        problematic self-signed certs (use with caution).
        """
        self.user_agent = user_agent
        self.timeout = timeout
        self.max_workers = max_workers
        self.respect_robots = respect_robots
        self.verify_ssl = verify_ssl
        self._robot_parsers: Dict[str, urllib.robotparser.RobotFileParser] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def crawl(
        self,
        url: str,
        max_pages: int = 50,
        max_depth: int = 3,
    ) -> CrawlResult:
        """Crawl a website starting from the given URL.

        Crawls breadth-first within the same domain, respecting configurable
        depth and page limits. Extracts on-page SEO data from each page and
        collects broken links.

        Args:
            url: Starting URL (must include scheme, e.g., https://example.com).
            max_pages: Maximum number of pages to crawl.
            max_depth: Maximum crawl depth (0 = only the start URL).

        Returns:
            CrawlResult with all crawled pages, link data, and diagnostics.
        """
        start_time = time.time()
        url = self._normalize_url(url)
        parsed_start = urllib.parse.urlparse(url)
        domain = parsed_start.netloc.lower()
        scheme = parsed_start.scheme

        result = CrawlResult(
            start_url=url,
            uses_https=scheme == "https",
        )

        # Check robots.txt
        if self.respect_robots:
            result.robots_txt_found = self._fetch_robots_txt(scheme, domain)
            if result.robots_txt_found and not self._robots_allowed(url):
                result.errors.append(f"robots.txt disallows crawling: {url}")
                result.total_duration = time.time() - start_time
                return result

        # Breadth-first crawl
        visited: Set[str] = set()
        queue: deque = deque()
        queue.append((url, 0))  # (url, depth)
        broken_links: List[Dict[str, Any]] = []
        all_pages: List[OnPageData] = []
        total_links = 0

        # Fetch start page
        onpage = self.extract_onpage(url)
        if onpage.error:
            result.errors.append(f"Failed to fetch start URL {url}: {onpage.error}")
            result.total_duration = time.time() - start_time
            return result

        visited.add(url)
        all_pages.append(onpage)
        total_links += len(onpage.links)

        # Collect same-domain links for deeper crawling
        for link_info in onpage.links:
            href = link_info.get("href", "")
            full_url = urllib.parse.urljoin(url, href)
            parsed = urllib.parse.urlparse(full_url)
            if parsed.netloc.lower() == domain and full_url not in visited:
                queue.append((full_url, 1))

        depth_reached = 0

        # Crawl remaining pages (breadth-first with parallelism within each depth level)
        while queue and len(all_pages) < max_pages:
            # Collect URLs at current depth
            current_batch: List[Tuple[str, int]] = []
            while queue and len(current_batch) < self.max_workers:
                next_url, depth = queue.popleft()
                if next_url not in visited and depth <= max_depth:
                    current_batch.append((next_url, depth))
                    visited.add(next_url)
                    depth_reached = max(depth_reached, depth)

            if not current_batch:
                # All URLs at current depth exhausted — fetch next depth
                if queue:
                    next_url, depth = queue.popleft()
                    if next_url not in visited and depth <= max_depth:
                        current_batch.append((next_url, depth))
                        visited.add(next_url)
                        depth_reached = max(depth_reached, depth)
                else:
                    break

            # Fetch batch in parallel
            urls_to_fetch = [u for u, _ in current_batch]
            if not urls_to_fetch:
                break

            with concurrent.futures.ThreadPoolExecutor(
                max_workers=min(self.max_workers, len(urls_to_fetch))
            ) as executor:
                futures_map = {
                    executor.submit(self.extract_onpage, u): (u, d)
                    for u, d in current_batch
                }
                for future in concurrent.futures.as_completed(futures_map):
                    batch_url, batch_depth = futures_map[future]
                    try:
                        page_data = future.result()
                    except Exception as e:
                        broken_links.append({
                            "url": batch_url, "status": "error", "error": str(e),
                        })
                        continue

                    if page_data.error:
                        broken_links.append({
                            "url": batch_url,
                            "status": page_data.status_code,
                            "error": page_data.error,
                        })
                        continue

                    if page_data.status_code >= 400:
                        broken_links.append({
                            "url": batch_url,
                            "status": page_data.status_code,
                            "error": f"HTTP {page_data.status_code}",
                        })

                    all_pages.append(page_data)
                    total_links += len(page_data.links)

                    # Enqueue same-domain links for next depth
                    if batch_depth < max_depth and len(all_pages) + len(queue) < max_pages:
                        for link_info in page_data.links:
                            href = link_info.get("href", "")
                            full_url = urllib.parse.urljoin(batch_url, href)
                            parsed = urllib.parse.urlparse(full_url)
                            if parsed.netloc.lower() == domain and full_url not in visited:
                                queue.append((full_url, batch_depth + 1))

                    # Stop if we've hit the page limit
                    if len(all_pages) >= max_pages:
                        break

        result.pages_crawled = len(all_pages)
        result.pages = all_pages
        result.total_links_found = total_links
        result.broken_links = broken_links
        result.crawl_depth_reached = depth_reached
        result.total_duration = time.time() - start_time

        return result

    def extract_onpage(self, url: str) -> OnPageData:
        """Extract on-page SEO data from a single URL.

        Fetches the page content and parses out: title, meta description,
        meta keywords, OG tags, Twitter card, canonical URL, all heading tags
        (h1-h6), links (with internal/external classification), and images
        (with alt text status).

        Args:
            url: Full URL to extract data from.

        Returns:
            OnPageData with all extracted SEO elements.
        """
        data = OnPageData(url=url)

        # Respect robots.txt per-URL
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc.lower()
        if self.respect_robots and hasattr(self, "_robot_parsers"):
            robot_parser = self._robot_parsers.get(domain)
            if robot_parser and not robot_parser.can_fetch(self.user_agent, url):
                data.error = "Disallowed by robots.txt"
                return data

        start = time.time()
        try:
            html = self._fetch_url(url)
            data.status_code = html.get("status_code", 200)
            data.content_type = html.get("content_type", "")
            data.load_time_ms = (time.time() - start) * 1000

            raw = html.get("body", "")

            # Title
            title_match = re.search(
                r'<title[^>]*>(.*?)</title>', raw, re.IGNORECASE | re.DOTALL
            )
            if title_match:
                data.title = self._clean_text(title_match.group(1))
                data.title_length = len(data.title)

            # Meta description
            desc_match = re.search(
                r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)["\']',
                raw, re.IGNORECASE,
            )
            if not desc_match:
                desc_match = re.search(
                    r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+name=["\']description["\']',
                    raw, re.IGNORECASE,
                )
            if desc_match:
                data.meta_description = desc_match.group(1).strip()
                data.meta_description_length = len(data.meta_description)

            # Meta keywords
            kw_match = re.search(
                r'<meta[^>]+name=["\']keywords["\'][^>]+content=["\']([^"\']*)["\']',
                raw, re.IGNORECASE,
            )
            if not kw_match:
                kw_match = re.search(
                    r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+name=["\']keywords["\']',
                    raw, re.IGNORECASE,
                )
            if kw_match:
                data.meta_keywords = kw_match.group(1).strip()

            # Canonical URL
            can_match = re.search(
                r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']*)["\']',
                raw, re.IGNORECASE,
            )
            if not can_match:
                can_match = re.search(
                    r'<link[^>]+href=["\']([^"\']*)["\'][^>]+rel=["\']canonical["\']',
                    raw, re.IGNORECASE,
                )
            if can_match:
                data.canonical_url = urllib.parse.urljoin(url, can_match.group(1))

            # OG tags
            data.og_title = self._extract_meta(raw, "og:title")
            data.og_description = self._extract_meta(raw, "og:description")
            data.og_image = self._extract_meta(raw, "og:image")

            # Twitter card
            data.twitter_card = self._extract_meta(raw, "twitter:card")

            # Headings
            for level in range(1, 7):
                tag = f"h{level}"
                headings = re.findall(
                    rf'<{tag}[^>]*>(.*?)</{tag}>', raw, re.IGNORECASE | re.DOTALL
                )
                cleaned = [self._clean_text(h) for h in headings if self._clean_text(h)]
                setattr(data, tag, cleaned)

            # Links
            data.links = self._extract_links(raw, url)
            domain = parsed.netloc.lower()
            for link in data.links:
                href = link.get("href", "")
                if href.startswith("#") or href.startswith("javascript:"):
                    continue
                full = urllib.parse.urljoin(url, href)
                link_parsed = urllib.parse.urlparse(full)
                if link_parsed.netloc.lower() == domain or not link_parsed.netloc:
                    data.internal_links += 1
                else:
                    data.external_links += 1

            # Images
            data.images = self._extract_images(raw, url)
            data.images_with_alt = sum(1 for img in data.images if img.get("alt"))
            data.images_missing_alt = len(data.images) - data.images_with_alt

            # Word count (rough)
            text = re.sub(r'<[^>]+>', ' ', raw)
            data.word_count = len(re.findall(r'\b\w+\b', text))

        except HTTPError as e:
            data.status_code = e.code
            data.error = f"HTTP {e.code}: {e.reason}"
        except URLError as e:
            data.error = f"URL Error: {e.reason}"
        except Exception as e:
            data.error = str(e)
        finally:
            data.load_time_ms = (time.time() - start) * 1000

        return data

    # ------------------------------------------------------------------
    # HTTP helpers
    # ------------------------------------------------------------------

    def _fetch_url(self, url: str) -> Dict[str, Any]:
        """Fetch a URL and return status, headers, and body.

        Args:
            url: Full URL to fetch.

        Returns:
            Dictionary with 'status_code', 'content_type', 'headers', and 'body'.
        """
        headers = {"User-Agent": self.user_agent}

        context = None
        if not self.verify_ssl:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=self.timeout, context=context) as response:
            body = response.read()
            # Attempt to decode
            content_type = response.headers.get("Content-Type", "")
            charset = self._parse_charset(content_type)
            try:
                text = body.decode(charset or "utf-8", errors="replace")
            except (UnicodeDecodeError, LookupError):
                text = body.decode("latin-1", errors="replace")

            return {
                "status_code": response.getcode(),
                "content_type": content_type,
                "headers": dict(response.headers),
                "body": text,
            }

    @staticmethod
    def _parse_charset(content_type: str) -> Optional[str]:
        """Extract charset from Content-Type header."""
        match = re.search(r'charset=([\w-]+)', content_type, re.IGNORECASE)
        return match.group(1) if match else None

    # ------------------------------------------------------------------
    # Robots.txt
    # ------------------------------------------------------------------

    def _fetch_robots_txt(self, scheme: str, domain: str) -> bool:
        """Fetch and parse robots.txt for the domain.

        Args:
            scheme: URL scheme (http/https).
            domain: Domain to fetch robots.txt from.

        Returns:
            True if robots.txt was successfully fetched and parsed.
        """
        robots_url = f"{scheme}://{domain}/robots.txt"
        try:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            self._robot_parsers[domain] = rp
            return True
        except Exception:
            return False

    def _robots_allowed(self, url: str) -> bool:
        """Check if a URL is allowed by the domain's robots.txt.

        Args:
            url: URL to check.

        Returns:
            True if allowed, False if disallowed or robots.txt not available.
        """
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc.lower()
        rp = self._robot_parsers.get(domain)
        if rp is None:
            return True  # No robots.txt — allow by default
        return rp.can_fetch(self.user_agent, url)

    # ------------------------------------------------------------------
    # Extraction helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_meta(html: str, property_name: str) -> str:
        """Extract a meta tag by property or name attribute.

        Args:
            html: Raw HTML content.
            property_name: The 'property' or 'name' attribute value (e.g., 'og:title').

        Returns:
            Content value of the matching meta tag, or empty string.
        """
        patterns = [
            rf'<meta[^>]+(?:property|name)=["\']{re.escape(property_name)}["\'][^>]+content=["\']([^"\']*)["\']',
            rf'<meta[^>]+content=["\']([^"\']*)["\'][^>]+(?:property|name)=["\']{re.escape(property_name)}["\']',
        ]
        for pat in patterns:
            match = re.search(pat, html, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return ""

    @staticmethod
    def _extract_links(html: str, base_url: str) -> List[Dict[str, str]]:
        """Extract all anchor links from HTML.

        Args:
            html: Raw HTML content.
            base_url: Base URL for resolving relative links.

        Returns:
            List of dictionaries with 'href', 'text', 'rel', and 'type' keys.
        """
        links: List[Dict[str, str]] = []
        # Match <a> tags with href
        anchor_pattern = re.compile(
            r'<a\s[^>]*?href\s*=\s*["\']([^"\']*)["\'][^>]*?>(.*?)</a>',
            re.IGNORECASE | re.DOTALL,
        )
        for match in anchor_pattern.finditer(html):
            href = match.group(1).strip()
            text = CrawlerEngine._clean_text(match.group(2))
            # Extract rel attribute
            rel_match = re.search(
                r'rel\s*=\s*["\']([^"\']*)["\']',
                match.group(0), re.IGNORECASE,
            )
            rel = rel_match.group(1) if rel_match else ""

            # Classify link type
            link_type = "internal"
            if href.startswith(("http://", "https://")):
                parsed_base = urllib.parse.urlparse(base_url)
                parsed_href = urllib.parse.urlparse(href)
                if parsed_href.netloc.lower() != parsed_base.netloc.lower():
                    link_type = "external"
            elif href.startswith(("mailto:", "tel:", "javascript:", "#")):
                link_type = "special"

            links.append({
                "href": href,
                "text": text,
                "rel": rel,
                "type": link_type,
            })
        return links

    @staticmethod
    def _extract_images(html: str, base_url: str) -> List[Dict[str, str]]:
        """Extract image tags with alt text from HTML.

        Args:
            html: Raw HTML content.
            base_url: Base URL for resolving relative image paths.

        Returns:
            List of dictionaries with 'src', 'alt', and 'full_url' keys.
        """
        images: List[Dict[str, str]] = []
        img_pattern = re.compile(
            r'<img\s[^>]*?src\s*=\s*["\']([^"\']*)["\'][^>]*>',
            re.IGNORECASE,
        )
        for match in img_pattern.finditer(html):
            src = match.group(1).strip()
            # Extract alt attribute from the full tag
            alt_match = re.search(
                r'alt\s*=\s*["\']([^"\']*)["\']',
                match.group(0), re.IGNORECASE,
            )
            alt = alt_match.group(1).strip() if alt_match else ""
            images.append({
                "src": src,
                "alt": alt,
                "full_url": urllib.parse.urljoin(base_url, src),
            })
        return images

    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean extracted text: strip tags, decode entities, collapse whitespace.

        Args:
            text: Raw text possibly containing HTML fragments.

        Returns:
            Cleaned plain text.
        """
        # Remove remaining inline HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Decode common entities
        entities = {
            '&amp;': '&', '&lt;': '<', '&gt;': '>',
            '&quot;': '"', '&#39;': "'", '&apos;': "'",
            '&nbsp;': ' ', '&mdash;': '—', '&ndash;': '–',
            '&#x27;': "'",
        }
        for entity, char in entities.items():
            text = text.replace(entity, char)
        # Collapse whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    @staticmethod
    def _normalize_url(url: str) -> str:
        """Ensure URL has a scheme; default to https if missing.

        Args:
            url: URL string, possibly without scheme.

        Returns:
            URL with scheme.
        """
        url = url.strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        return url


# ------------------------------------------------------------------
# Runnable test (python -m seo_swarm.crawler.engine)
# ------------------------------------------------------------------
if __name__ == "__main__":
    engine = CrawlerEngine(timeout=10)

    print("=" * 60)
    print("  CRAWLER ENGINE TEST")
    print("=" * 60)

    # Test 1: Single page extraction
    print("\n[Test 1] Single page extraction")
    print("-" * 40)
    try:
        onpage = engine.extract_onpage("https://httpbin.org/html")
        print(f"  URL:            {onpage.url}")
        print(f"  Status:         {onpage.status_code}")
        print(f"  Title:          {onpage.title[:80] if onpage.title else 'N/A'}...")
        print(f"  Title Length:   {onpage.title_length}")
        print(f"  Meta Desc:      {onpage.meta_description[:80] if onpage.meta_description else 'N/A'}...")
        print(f"  Meta Desc Len:  {onpage.meta_description_length}")
        print(f"  H1 Count:       {onpage.h1_count}")
        print(f"  H2 Count:       {onpage.h2_count}")
        print(f"  Internal Links: {onpage.internal_links}")
        print(f"  External Links: {onpage.external_links}")
        print(f"  Images:         {len(onpage.images)} ({onpage.images_with_alt} with alt)")
        print(f"  Load Time:      {onpage.load_time_ms:.1f} ms")
        if onpage.error:
            print(f"  Error:          {onpage.error}")
    except Exception as e:
        print(f"  Extraction failed (network may be unavailable): {e}")
        # Fallback: demo with simulated data
        print("  (Showing simulated extraction for offline demo)")
        onpage = OnPageData(
            url="https://httpbin.org/html",
            status_code=200,
            title="Herman Melville - Moby-Dick",
            title_length=26,
            meta_description="A sample HTML page for testing purposes.",
            meta_description_length=42,
            h1=["Moby-Dick"],
            h2=["Chapter 1", "Chapter 2", "Notes"],
            links=[
                {"href": "/", "text": "Home", "rel": "", "type": "internal"},
                {"href": "/about", "text": "About", "rel": "", "type": "internal"},
            ],
            internal_links=2,
            external_links=0,
            images=[{"src": "cover.jpg", "alt": "Book cover", "full_url": "https://httpbin.org/cover.jpg"}],
            images_with_alt=1,
            images_missing_alt=0,
            word_count=250,
            load_time_ms=320.5,
        )
        print(f"  Title:          {onpage.title}")
        print(f"  H1:             {onpage.h1}")
        print(f"  Word Count:     {onpage.word_count}")

    # Test 2: OnPageData to_dict
    print("\n[Test 2] OnPageData.to_dict()")
    print("-" * 40)
    d = onpage.to_dict()
    for k in sorted(d.keys()):
        if k not in ("links", "images", "h1", "h2", "h3", "h4", "h5", "h6"):
            print(f"  {k}: {d[k]}")

    # Test 3: Crawl (limited test)
    print("\n[Test 3] Crawl test")
    print("-" * 40)
    try:
        result = engine.crawl("https://httpbin.org", max_pages=3, max_depth=1)
        print(f"  Start URL:       {result.start_url}")
        print(f"  Pages Crawled:   {result.pages_crawled}")
        print(f"  Total Links:     {result.total_links_found}")
        print(f"  Broken Links:    {len(result.broken_links)}")
        print(f"  Robots.txt:      {result.robots_txt_found}")
        print(f"  HTTPS:           {result.uses_https}")
        print(f"  Duration:        {result.total_duration:.2f}s")
        print(f"  Depth Reached:   {result.crawl_depth_reached}")
        print(f"  Errors:          {result.errors}")
        print("\n  Crawled pages:")
        for p in result.pages[:3]:
            print(f"    - {p.url} [{p.status_code}] {p.title[:50]}...")
    except Exception as e:
        print(f"  Crawl failed (network may be unavailable): {e}")
        print("  (Engine is ready for use when network is available)")

    print("\n" + "=" * 60)
    print("  Crawler engine test complete.")
