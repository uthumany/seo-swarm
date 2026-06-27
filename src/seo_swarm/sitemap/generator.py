"""
SEO SWARM - XML Sitemap Generator
Generate and validate XML sitemaps per sitemaps.org protocol.
Uses xml.etree.ElementTree from the standard library only.
"""

import os
from datetime import datetime, timezone
from typing import Dict, Any, List
from xml.etree import ElementTree as ET


class SitemapGenerator:
    """Generate and validate XML sitemaps (sitemaps.org protocol).

    Supports:
      - <urlset> with <url> entries: loc, lastmod, changefreq, priority
      - <sitemapindex> with <sitemap> entries
      - Validation of existing sitemap files
    """

    # Valid changefreq values per sitemaps.org
    VALID_CHANGEFREQ = {
        "always", "hourly", "daily", "weekly", "monthly", "yearly", "never",
    }

    # XML namespace
    NS = "http://www.sitemaps.org/schemas/sitemap/0.9"

    # Enhanced (image/video) namespace
    NS_IMAGE = "http://www.google.com/schemas/sitemap-image/1.1"

    def __init__(self):
        self.errors: List[str] = []

    # ------------------------------------------------------------------
    # URL-level helpers
    # ------------------------------------------------------------------
    def _build_url_element(self, entry: Dict[str, Any]) -> ET.Element:
        """Build a single <url> element from a dict.

        Expected keys: loc (required), lastmod, changefreq, priority.
        """
        url_el = ET.Element("url")

        loc = ET.SubElement(url_el, "loc")
        loc.text = str(entry["loc"])

        if "lastmod" in entry and entry["lastmod"]:
            lm = ET.SubElement(url_el, "lastmod")
            lm.text = self._normalize_lastmod(entry["lastmod"])

        if "changefreq" in entry and entry["changefreq"]:
            cf = entry["changefreq"].lower()
            if cf in self.VALID_CHANGEFREQ:
                el = ET.SubElement(url_el, "changefreq")
                el.text = cf

        if "priority" in entry and entry["priority"] is not None:
            p = float(entry["priority"])
            p = max(0.0, min(1.0, p))
            el = ET.SubElement(url_el, "priority")
            el.text = f"{p:.1f}"

        return url_el

    def _build_sitemap_element(self, entry: Dict[str, Any]) -> ET.Element:
        """Build a single <sitemap> element for a sitemapindex.

        Expected keys: loc (required), lastmod (optional).
        """
        sm_el = ET.Element("sitemap")

        loc = ET.SubElement(sm_el, "loc")
        loc.text = str(entry["loc"])

        if "lastmod" in entry and entry["lastmod"]:
            lm = ET.SubElement(sm_el, "lastmod")
            lm.text = self._normalize_lastmod(entry["lastmod"])

        return sm_el

    def _normalize_lastmod(self, value) -> str:
        """Normalize lastmod to W3C Datetime format (ISO 8601)."""
        if isinstance(value, datetime):
            return value.isoformat()
        # If already a string, return as-is (caller's responsibility)
        return str(value)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def generate(self, urls: List[dict], output_path: str) -> str:
        """Generate a <urlset> sitemap XML file.

        Args:
            urls: List of dicts, each with keys:
                  loc (required), lastmod, changefreq, priority.
            output_path: File path to write the XML sitemap.

        Returns:
            Absolute path to the generated file.

        Example:
            gen = SitemapGenerator()
            gen.generate([
                {"loc": "https://example.com/", "priority": 1.0, "changefreq": "daily"},
            ], "sitemap.xml")
        """
        urlset = ET.Element("urlset", xmlns=self.NS)
        for entry in urls:
            urlset.append(self._build_url_element(entry))

        tree = ET.ElementTree(urlset)
        ET.indent(tree, space="  ")

        output_path = os.path.abspath(output_path)
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        tree.write(output_path, encoding="utf-8", xml_declaration=True)

        return output_path

    def generate_index(
        self, sitemap_urls: List[str], output_path: str
    ) -> str:
        """Generate a <sitemapindex> XML file pointing to child sitemaps.

        Args:
            sitemap_urls: List of sitemap URL strings or dicts with 'loc'
                          and optional 'lastmod'.
            output_path: File path to write the sitemap index.

        Returns:
            Absolute path to the generated file.
        """
        sitemapindex = ET.Element("sitemapindex", xmlns=self.NS)
        for item in sitemap_urls:
            if isinstance(item, str):
                entry = {"loc": item}
            else:
                entry = item
            sitemapindex.append(self._build_sitemap_element(entry))

        tree = ET.ElementTree(sitemapindex)
        ET.indent(tree, space="  ")

        output_path = os.path.abspath(output_path)
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        tree.write(output_path, encoding="utf-8", xml_declaration=True)

        return output_path

    def validate(self, sitemap_path: str) -> Dict[str, Any]:
        """Validate an existing sitemap XML file.

        Checks:
          - File exists and is readable
          - Well-formed XML
          - Correct namespace (urlset or sitemapindex)
          - Required <loc> elements present
          - Valid changefreq values
          - Priority in 0.0–1.0 range

        Args:
            sitemap_path: Path to the sitemap file to validate.

        Returns:
            Dict with keys 'valid' (bool) and 'errors' (list of strings).
        """
        self.errors = []

        # Check file exists
        if not os.path.isfile(sitemap_path):
            self.errors.append(f"File not found: {sitemap_path}")
            return {"valid": False, "errors": self.errors}

        # Parse XML
        try:
            tree = ET.parse(sitemap_path)
            root = tree.getroot()
        except ET.ParseError as e:
            self.errors.append(f"XML parse error: {e}")
            return {"valid": False, "errors": self.errors}

        # Check namespace (handle default namespace via Clark notation)
        tag = root.tag
        is_urlset = tag == f"{{{self.NS}}}urlset" or tag == "urlset"
        is_index = tag == f"{{{self.NS}}}sitemapindex" or tag == "sitemapindex"

        if not is_urlset and not is_index:
            self.errors.append(
                f"Root element must be <urlset> or <sitemapindex> "
                f"in namespace {self.NS}. Found: {tag}"
            )
            return {"valid": False, "errors": self.errors}

        # Validate child elements
        if is_urlset:
            self._validate_urlset(root)
        else:
            self._validate_sitemapindex(root)

        return {
            "valid": len(self.errors) == 0,
            "errors": self.errors,
        }

    def _find_elem(self, parent: ET.Element, tag: str, ns: str) -> Optional[ET.Element]:
        """Safely find a child element with or without namespace."""
        el = parent.find(f"{ns}{tag}")
        if el is not None:
            return el
        return parent.find(tag)

    def _validate_urlset(self, root: ET.Element) -> None:
        """Validate <urlset> children."""
        ns = f"{{{self.NS}}}"

        urls = root.findall(f"{ns}url")
        if not urls:
            urls = root.findall("url")

        if not urls:
            self.errors.append("No <url> elements found in <urlset>")
            return

        for idx, url_el in enumerate(urls, 1):
            # Check <loc> present
            loc_el = self._find_elem(url_el, "loc", ns)
            if loc_el is None or not (loc_el.text or "").strip():
                self.errors.append(f"url #{idx}: missing or empty <loc>")

            # Check <changefreq> if present
            cf_el = self._find_elem(url_el, "changefreq", ns)
            if cf_el is not None and cf_el.text and cf_el.text.strip():
                if cf_el.text.strip().lower() not in self.VALID_CHANGEFREQ:
                    self.errors.append(
                        f"url #{idx}: invalid changefreq '{cf_el.text}'"
                    )

            # Check <priority> if present
            p_el = self._find_elem(url_el, "priority", ns)
            if p_el is not None and p_el.text and p_el.text.strip():
                try:
                    p = float(p_el.text.strip())
                    if p < 0.0 or p > 1.0:
                        self.errors.append(
                            f"url #{idx}: priority {p} out of range (0.0-1.0)"
                        )
                except ValueError:
                    self.errors.append(
                        f"url #{idx}: invalid priority value '{p_el.text}'"
                    )

    def _validate_sitemapindex(self, root: ET.Element) -> None:
        """Validate <sitemapindex> children."""
        ns = f"{{{self.NS}}}"

        sitemaps = root.findall(f"{ns}sitemap")
        if not sitemaps:
            sitemaps = root.findall("sitemap")

        if not sitemaps:
            self.errors.append("No <sitemap> elements found in <sitemapindex>")
            return

        for idx, sm_el in enumerate(sitemaps, 1):
            loc_el = self._find_elem(sm_el, "loc", ns)
            if loc_el is None or not (loc_el.text or "").strip():
                self.errors.append(f"sitemap #{idx}: missing or empty <loc>")


# ---------------------------------------------------------------------------
# Runnable test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import tempfile

    gen = SitemapGenerator()
    tmpdir = tempfile.mkdtemp(prefix="seo_swarm_sitemap_test_")
    print(f"Test directory: {tmpdir}")

    # ---- Generate a urlset sitemap ----
    urls = [
        {
            "loc": "https://example.com/",
            "lastmod": "2025-06-27",
            "changefreq": "daily",
            "priority": 1.0,
        },
        {
            "loc": "https://example.com/about",
            "lastmod": "2025-06-20",
            "changefreq": "weekly",
            "priority": 0.8,
        },
        {
            "loc": "https://example.com/products",
            "lastmod": "2025-06-27T10:00:00",
            "changefreq": "daily",
            "priority": 0.9,
        },
        {
            "loc": "https://example.com/contact",
            "changefreq": "monthly",
            "priority": 0.5,
        },
    ]

    out = gen.generate(urls, os.path.join(tmpdir, "sitemap.xml"))
    print(f"\nGenerated: {out}")

    # Read back and display
    with open(out, "r", encoding="utf-8") as f:
        print("\n--- sitemap.xml content ---")
        print(f.read())

    # ---- Validate ----
    result = gen.validate(out)
    print(f"\nValidation: valid={result['valid']}, errors={result['errors']}")

    # ---- Generate a sitemap index ----
    child_sitemaps = [
        {"loc": "https://example.com/sitemap-posts.xml", "lastmod": "2025-06-27"},
        {"loc": "https://example.com/sitemap-pages.xml", "lastmod": "2025-06-26"},
    ]
    idx_out = gen.generate_index(child_sitemaps, os.path.join(tmpdir, "sitemap_index.xml"))
    print(f"\nGenerated index: {idx_out}")

    with open(idx_out, "r", encoding="utf-8") as f:
        print("\n--- sitemap_index.xml content ---")
        print(f.read())

    # Validate the index
    idx_result = gen.validate(idx_out)
    print(f"\nIndex validation: valid={idx_result['valid']}, errors={idx_result['errors']}")

    # ---- Test invalid file ----
    bad_result = gen.validate(os.path.join(tmpdir, "nonexistent.xml"))
    print(f"\nMissing file validation: valid={bad_result['valid']}, errors={bad_result['errors']}")

    print("\n" + "=" * 60)
    print(" ALL TESTS COMPLETE")
    print("=" * 60)
