"""
SEO SWARM - JSON-LD Schema Markup Generator
Generate valid JSON-LD structured data for 10+ schema types.
Zero external dependencies — stdlib json module only.
"""

import json
from typing import Dict, Any, List, Optional


class SchemaGenerator:
    """Generate and validate JSON-LD schema.org structured data markup.

    Supports: Organization, WebSite, WebPage, Article, FAQ, Product,
    LocalBusiness, BreadcrumbList, Person, Event.

    Output is a ready-to-embed JSON-LD script tag string.
    """

    # Registry of supported schema types with their @type
    SCHEMA_TYPES = {
        "organization": "Organization",
        "website": "WebSite",
        "webpage": "WebPage",
        "article": "Article",
        "faq": "FAQPage",
        "product": "Product",
        "localbusiness": "LocalBusiness",
        "breadcrumblist": "BreadcrumbList",
        "person": "Person",
        "event": "Event",
    }

    # Default values per schema type
    DEFAULTS: Dict[str, Dict[str, Any]] = {
        "organization": {
            "name": "Example Organization",
            "url": "https://example.com",
        },
        "website": {
            "name": "Example Website",
            "url": "https://example.com",
        },
        "webpage": {
            "name": "Example Page",
            "url": "https://example.com/page",
        },
        "article": {
            "headline": "Example Article Title",
            "author": {"@type": "Person", "name": "Author Name"},
            "datePublished": "2025-01-01",
        },
        "faq": {
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": "Example question?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "Example answer.",
                    },
                },
            ],
        },
        "product": {
            "name": "Example Product",
            "description": "Product description.",
            "offers": {
                "@type": "Offer",
                "price": "0.00",
                "priceCurrency": "USD",
            },
        },
        "localbusiness": {
            "name": "Example Business",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "123 Main St",
                "addressLocality": "City",
                "addressRegion": "State",
                "postalCode": "12345",
                "addressCountry": "US",
            },
        },
        "breadcrumblist": {
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "Home",
                    "item": "https://example.com/",
                },
            ],
        },
        "person": {
            "name": "Jane Doe",
        },
        "event": {
            "name": "Example Event",
            "startDate": "2025-12-31T20:00:00",
            "location": {
                "@type": "Place",
                "name": "Venue Name",
                "address": "123 Main St, City",
            },
        },
    }

    def list_types(self) -> List[str]:
        """Return available schema type names (keys)."""
        return sorted(self.SCHEMA_TYPES.keys())

    def generate(self, schema_type: str, data: Optional[Dict[str, Any]] = None) -> str:
        """Generate a JSON-LD string for a single schema type.

        Args:
            schema_type: One of the keys from SCHEMA_TYPES (case-insensitive).
            data: Optional dict of properties to merge with defaults.

        Returns:
            A JSON-LD string suitable for embedding in a <script> tag.

        Example:
            gen = SchemaGenerator()
            jsonld = gen.generate("organization", {"name": "Acme Inc"})
        """
        stype = schema_type.lower()
        if stype not in self.SCHEMA_TYPES:
            available = ", ".join(self.SCHEMA_TYPES.keys())
            raise ValueError(
                f"Unknown schema type '{schema_type}'. Available: {available}"
            )

        # Start with defaults, then merge user data
        defaults = json.loads(json.dumps(self.DEFAULTS[stype]))
        merged = self._deep_merge(defaults, data or {})

        jsonld = {
            "@context": "https://schema.org",
            "@type": self.SCHEMA_TYPES[stype],
            **merged,
        }

        return json.dumps(jsonld, indent=2, ensure_ascii=False)

    def generate_all(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Generate all applicable schema types from a common data dict.

        Args:
            data: Dict with optional keys like 'name', 'url', 'description',
                  'logo', 'address', 'sameAs', 'founder', 'foundingDate',
                  'products', 'articles', 'events', etc.
                  Also supports nested keys: 'person', 'localbusiness',
                  'faq' to pass type-specific overrides.

        Returns:
            Dict mapping schema type keys to JSON-LD strings.
        """
        d = data or {}
        result: Dict[str, str] = {}

        # Organization
        org_data = {"name": d.get("name", ""), "url": d.get("url", "")}
        if d.get("logo"):
            org_data["logo"] = d["logo"]
        if d.get("sameAs"):
            org_data["sameAs"] = d["sameAs"]
        if d.get("description"):
            org_data["description"] = d["description"]
        if d.get("founder"):
            org_data["founder"] = d["founder"]
        # Merge any organization-specific overrides
        if "organization" in d:
            org_data = self._deep_merge(org_data, d["organization"])
        result["organization"] = self.generate("organization", org_data)

        # Website
        ws_data = {"name": d.get("name", ""), "url": d.get("url", "")}
        if d.get("description"):
            ws_data["description"] = d["description"]
        if "website" in d:
            ws_data = self._deep_merge(ws_data, d["website"])
        result["website"] = self.generate("website", ws_data)

        # WebPage
        wp_data = {
            "name": d.get("name", ""),
            "url": d.get("url", ""),
        }
        if d.get("description"):
            wp_data["description"] = d["description"]
        if "webpage" in d:
            wp_data = self._deep_merge(wp_data, d["webpage"])
        result["webpage"] = self.generate("webpage", wp_data)

        # LocalBusiness (if address info is provided)
        if d.get("address"):
            lb_data = {"name": d.get("name", ""), "address": d["address"]}
            if d.get("url"):
                lb_data["url"] = d["url"]
            if "localbusiness" in d:
                lb_data = self._deep_merge(lb_data, d["localbusiness"])
            result["localbusiness"] = self.generate("localbusiness", lb_data)

        # BreadcrumbList
        if d.get("breadcrumbs"):
            bc_data = {"itemListElement": d["breadcrumbs"]}
            if "breadcrumblist" in d:
                bc_data = self._deep_merge(bc_data, d["breadcrumblist"])
            result["breadcrumblist"] = self.generate("breadcrumblist", bc_data)

        # Person
        if d.get("person") or d.get("founder"):
            person_data = d.get("person") or d.get("founder") or {}
            if isinstance(person_data, str):
                person_data = {"name": person_data}
            result["person"] = self.generate("person", person_data)

        # Product(s)
        if d.get("products"):
            for i, product in enumerate(d["products"]):
                key = f"product_{i}" if len(d["products"]) > 1 else "product"
                result[key] = self.generate("product", product)

        # Article(s)
        if d.get("articles"):
            for i, article in enumerate(d["articles"]):
                key = f"article_{i}" if len(d["articles"]) > 1 else "article"
                result[key] = self.generate("article", article)

        # Event(s)
        if d.get("events"):
            for i, event in enumerate(d["events"]):
                key = f"event_{i}" if len(d["events"]) > 1 else "event"
                result[key] = self.generate("event", event)

        # FAQ
        if d.get("faq"):
            faq_data = {"mainEntity": []}
            for qa in d["faq"]:
                if isinstance(qa, dict):
                    faq_data["mainEntity"].append({
                        "@type": "Question",
                        "name": qa.get("question", qa.get("name", "")),
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": qa.get("answer", qa.get("text", "")),
                        },
                    })
            result["faq"] = self.generate("faq", faq_data)

        return result

    def validate(self, jsonld_str: str) -> Dict[str, Any]:
        """Validate a JSON-LD string.

        Checks:
          - Valid JSON
          - @context is "https://schema.org"
          - @type is present and non-empty

        Args:
            jsonld_str: The JSON-LD string to validate.

        Returns:
            Dict with 'valid' (bool) and 'errors' (list of strings).
        """
        errors: List[str] = []

        # Parse JSON
        try:
            data = json.loads(jsonld_str)
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON: {e}")
            return {"valid": False, "errors": errors}

        if not isinstance(data, dict):
            errors.append("JSON-LD must be a JSON object (dict)")
            return {"valid": False, "errors": errors}

        # Check @context
        context = data.get("@context", "")
        if context != "https://schema.org":
            errors.append(
                f"@context must be 'https://schema.org', got '{context}'"
            )

        # Check @type
        schema_type = data.get("@type", "")
        if not schema_type:
            errors.append("Missing required @type field")

        # Check for known @type
        known_types = set(self.SCHEMA_TYPES.values())
        if schema_type and schema_type not in known_types:
            errors.append(
                f"Unknown @type '{schema_type}'. "
                f"Known types: {', '.join(sorted(known_types))}"
            )

        return {"valid": len(errors) == 0, "errors": errors}

    def _deep_merge(
        self, base: Dict[str, Any], override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Recursively merge override into base."""
        result = dict(base)
        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result


# ---------------------------------------------------------------------------
# Runnable test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    gen = SchemaGenerator()

    print("=" * 60)
    print(" SCHEMA TYPES AVAILABLE")
    print("=" * 60)
    print(", ".join(gen.list_types()))

    print("\n" + "=" * 60)
    print(" 1. Organization")
    print("=" * 60)
    org = gen.generate("organization", {"name": "Acme Corp", "url": "https://acme.com"})
    print(org)

    print("\n" + "=" * 60)
    print(" 2. BreadcrumbList")
    print("=" * 60)
    bc = gen.generate("breadcrumblist", {
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://example.com/"},
            {"@type": "ListItem", "position": 2, "name": "Products", "item": "https://example.com/products"},
            {"@type": "ListItem", "position": 3, "name": "Widget X", "item": "https://example.com/products/widget-x"},
        ]
    })
    print(bc)

    print("\n" + "=" * 60)
    print(" 3. FAQ")
    print("=" * 60)
    faq = gen.generate("faq", {
        "mainEntity": [
            {
                "@type": "Question",
                "name": "What is your return policy?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "30-day money-back guarantee."
                }
            },
            {
                "@type": "Question",
                "name": "Do you ship internationally?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Yes, we ship worldwide."
                }
            }
        ]
    })
    print(faq)

    print("\n" + "=" * 60)
    print(" 4. generate_all() - Full site schema")
    print("=" * 60)
    all_schemas = gen.generate_all({
        "name": "Acme Corp",
        "url": "https://acme.com",
        "description": "Leading provider of widgets.",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "123 Main St",
            "addressLocality": "New York",
            "addressRegion": "NY",
            "postalCode": "10001",
            "addressCountry": "US",
        },
        "breadcrumbs": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://acme.com/"},
            {"@type": "ListItem", "position": 2, "name": "About", "item": "https://acme.com/about"},
        ],
        "faq": [
            {"question": "What is ACME?", "answer": "A leading widget maker."},
        ],
    })
    for key, value in all_schemas.items():
        print(f"\n--- {key} ---")
        print(value)

    print("\n" + "=" * 60)
    print(" 5. Validation")
    print("=" * 60)
    valid_result = gen.validate(org)
    print(f"Valid org schema: {valid_result}")

    # Test invalid
    bad = '{"@context": "https://wrong.org", "name": "test"}'
    invalid_result = gen.validate(bad)
    print(f"Invalid schema: {invalid_result}")

    print("\n" + "=" * 60)
    print(" ALL TESTS COMPLETE")
    print("=" * 60)
