"""
SEO SWARM - Content Analyzer Engine
Content quality analysis: readability, keyword density, heading structure,
and text statistics using pure Python (no external NLP dependencies).
"""

from __future__ import annotations

import re
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ContentAnalysis:
    """Result of content analysis from ContentAnalyzer.analyze()."""

    # Readability
    readability_score: float = 0.0  # Flesch-Kincaid Reading Ease (0-100)
    grade_level: float = 0.0  # Flesch-Kincaid Grade Level
    reading_ease_label: str = "N/A"  # "Very Easy" through "Very Confusing"

    # Word & sentence statistics
    word_count: int = 0
    sentence_count: int = 0
    avg_sentence_length: float = 0.0
    avg_word_length: float = 0.0
    syllable_count: int = 0

    # Keyword analysis
    keyword: Optional[str] = None
    keyword_density: float = 0.0  # percentage
    keyword_count: int = 0
    keyword_variations: List[str] = field(default_factory=list)

    # Heading analysis
    heading_stats: Dict[str, int] = field(default_factory=dict)

    # Image analysis
    image_count: int = 0
    images_with_alt: int = 0
    images_missing_alt: int = 0
    alt_text_score: float = 0.0  # 0-100

    # Additional metrics
    character_count: int = 0
    paragraph_count: int = 0
    estimated_reading_time_minutes: float = 0.0

    # Overall content score estimate (0-100)
    content_score: float = 0.0

    # Recommendations
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the analysis result to a dictionary.

        Returns:
            Dictionary with all analysis fields.
        """
        return {
            "readability_score": round(self.readability_score, 1),
            "grade_level": round(self.grade_level, 1),
            "reading_ease_label": self.reading_ease_label,
            "word_count": self.word_count,
            "sentence_count": self.sentence_count,
            "avg_sentence_length": round(self.avg_sentence_length, 1),
            "avg_word_length": round(self.avg_word_length, 2),
            "syllable_count": self.syllable_count,
            "keyword": self.keyword,
            "keyword_density": round(self.keyword_density, 2),
            "keyword_count": self.keyword_count,
            "heading_stats": self.heading_stats,
            "image_count": self.image_count,
            "images_with_alt": self.images_with_alt,
            "images_missing_alt": self.images_missing_alt,
            "alt_text_score": round(self.alt_text_score, 1),
            "character_count": self.character_count,
            "paragraph_count": self.paragraph_count,
            "estimated_reading_time_minutes": round(self.estimated_reading_time_minutes, 1),
            "content_score": round(self.content_score, 1),
            "recommendations": self.recommendations,
        }


class ContentAnalyzer:
    """Analyze text content for SEO-relevant quality metrics.

    Provides Flesch-Kincaid readability scores, keyword density analysis,
    heading structure checks, and image alt-text coverage. All computations
    use pure Python with no external NLP dependencies.

    Usage:
        analyzer = ContentAnalyzer()
        result = analyzer.analyze(text, keyword="SEO tips")
        print(f"Readability: {result.readability_score}, Grade: {result.grade_level}")
    """

    # Reading ease label mapping
    EASE_LABELS: List[Tuple[float, float, str]] = [
        (90.0, 100.0, "Very Easy"),
        (80.0, 90.0, "Easy"),
        (70.0, 80.0, "Fairly Easy"),
        (60.0, 70.0, "Standard"),
        (50.0, 60.0, "Fairly Difficult"),
        (30.0, 50.0, "Difficult"),
        (0.0, 30.0, "Very Confusing"),
    ]

    # Common English vowels
    VOWELS = set("aeiouAEIOU")

    def analyze(self, text: str, keyword: Optional[str] = None) -> ContentAnalysis:
        """Perform comprehensive content analysis.

        Args:
            text: The full text content to analyze (can include HTML or be plain text).
            keyword: Optional target keyword for density analysis.

        Returns:
            ContentAnalysis dataclass with all computed metrics.
        """
        # Strip HTML tags for text analysis, but keep headings for heading stats
        plain_text = self._strip_html(text)
        heading_stats = self._extract_heading_stats(text)

        # Word and sentence counts
        word_count = self._count_words(plain_text)
        sentence_count = self._count_sentences(plain_text)
        char_count = len(plain_text)
        paragraph_count = self._count_paragraphs(plain_text)

        # Syllables and readability
        syllable_count = self._count_syllables(plain_text)
        readability_score = self._flesch_reading_ease(
            word_count, sentence_count, syllable_count
        )
        grade_level = self._flesch_kincaid_grade(
            word_count, sentence_count, syllable_count
        )
        ease_label = self._get_ease_label(readability_score)

        # Average lengths
        avg_sentence_length = word_count / max(sentence_count, 1)
        avg_word_length = char_count / max(word_count, 1)

        # Estimated reading time (average reading speed: 238 words/min)
        reading_time = word_count / 238.0

        # Keyword analysis
        kw_density = 0.0
        kw_count = 0
        kw_variations: List[str] = []
        if keyword:
            kw_lower = keyword.lower().strip()
            kw_count = plain_text.lower().count(kw_lower)
            kw_density = (kw_count / max(word_count, 1)) * 100.0
            kw_variations = self._find_keyword_variations(plain_text, kw_lower)

        # Image alt text analysis
        img_data = self._analyze_images(text)
        image_count = img_data["total"]
        images_with_alt = img_data["with_alt"]
        images_missing_alt = img_data["missing_alt"]
        alt_score = (images_with_alt / max(image_count, 1)) * 100.0 if image_count > 0 else 100.0

        # Overall content score estimate (weighted composite)
        content_score = self._calculate_content_score(
            word_count=word_count,
            sentence_count=sentence_count,
            readability=readability_score,
            keyword_density=kw_density,
            alt_text_score=alt_score,
            heading_stats=heading_stats,
        )

        # Build recommendations
        recommendations = self._build_content_recommendations(
            word_count=word_count,
            sentence_count=sentence_count,
            readability=readability_score,
            grade_level=grade_level,
            keyword=keyword,
            keyword_density=kw_density,
            alt_score=alt_score,
            images_missing_alt=images_missing_alt,
            heading_stats=heading_stats,
        )

        return ContentAnalysis(
            readability_score=readability_score,
            grade_level=grade_level,
            reading_ease_label=ease_label,
            word_count=word_count,
            sentence_count=sentence_count,
            avg_sentence_length=avg_sentence_length,
            avg_word_length=avg_word_length,
            syllable_count=syllable_count,
            keyword=keyword or "",
            keyword_density=kw_density,
            keyword_count=kw_count,
            keyword_variations=kw_variations,
            heading_stats=heading_stats,
            image_count=image_count,
            images_with_alt=images_with_alt,
            images_missing_alt=images_missing_alt,
            alt_text_score=alt_score,
            character_count=char_count,
            paragraph_count=paragraph_count,
            estimated_reading_time_minutes=reading_time,
            content_score=content_score,
            recommendations=recommendations,
        )

    # ------------------------------------------------------------------
    # Counting helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _strip_html(text: str) -> str:
        """Remove HTML tags and decode common entities, returning plain text.

        Args:
            text: Raw HTML or text content.

        Returns:
            Plain text with HTML removed and entities decoded.
        """
        # Remove script and style blocks
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        # Decode common HTML entities
        entities = {
            '&amp;': '&', '&lt;': '<', '&gt;': '>',
            '&quot;': '"', '&#39;': "'", '&apos;': "'",
            '&nbsp;': ' ', '&mdash;': '—', '&ndash;': '–',
        }
        for entity, char in entities.items():
            text = text.replace(entity, char)
        # Collapse whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    @staticmethod
    def _count_words(text: str) -> int:
        """Count words in text."""
        return len(re.findall(r"[A-Za-z0-9]+(?:['\u2019][A-Za-z]+)?", text))

    @staticmethod
    def _count_sentences(text: str) -> int:
        """Count sentences using punctuation boundaries."""
        # Match sentence-ending punctuation followed by spaces/newlines/end-of-string
        sentences = re.findall(r'[.!?]+(?:\s+|$)', text)
        return max(len(sentences), 1)

    @staticmethod
    def _count_paragraphs(text: str) -> int:
        """Count paragraphs by double newlines."""
        paragraphs = re.split(r'\n\s*\n', text.strip())
        return max(len([p for p in paragraphs if p.strip()]), 1)

    @staticmethod
    def _count_syllables(text: str) -> int:
        """Estimate syllable count using vowel-group heuristic.

        Args:
            text: Plain text content.

        Returns:
            Estimated syllable count.
        """
        words = re.findall(r"[A-Za-z]+", text.lower())
        count = 0
        for word in words:
            word_count = ContentAnalyzer._syllables_in_word(word)
            count += max(word_count, 1)
        return count

    @staticmethod
    def _syllables_in_word(word: str) -> int:
        """Count syllables in a single word.

        Rules:
            - Count vowel groups (consecutive vowels = 1 syllable).
            - Silent 'e' at end reduces count by 1.
            - Always at least 1 syllable.

        Args:
            word: A single word string.

        Returns:
            Syllable count.
        """
        word = word.lower().strip()
        if len(word) <= 2:
            return 1

        # Count vowel groups
        syllables = 0
        prev_vowel = False
        for ch in word:
            is_vowel = ch in ContentAnalyzer.VOWELS
            if is_vowel and not prev_vowel:
                syllables += 1
            prev_vowel = is_vowel

        # Silent e rule
        if word.endswith('e') and len(word) > 2:
            # Check the characters before 'e'
            if word[-2] not in ContentAnalyzer.VOWELS:
                syllables = max(syllables - 1, 1)

        # Words ending in 'le' preceded by consonant add a syllable
        if word.endswith('le') and len(word) > 2 and word[-3] not in ContentAnalyzer.VOWELS:
            syllables += 1

        return max(syllables, 1)

    # ------------------------------------------------------------------
    # Readability formulas
    # ------------------------------------------------------------------

    @staticmethod
    def _flesch_reading_ease(word_count: int, sentence_count: int, syllable_count: int) -> float:
        """Calculate Flesch-Kincaid Reading Ease score.

        Score range: 0-100 (higher = easier to read).

        Formula: 206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)

        Args:
            word_count: Total word count.
            sentence_count: Total sentence count.
            syllable_count: Total syllable count.

        Returns:
            Reading ease score clamped to [0, 100].
        """
        if word_count == 0:
            return 100.0
        sent = max(sentence_count, 1)
        asl = word_count / sent  # average sentence length
        asw = syllable_count / word_count  # average syllables per word
        score = 206.835 - (1.015 * asl) - (84.6 * asw)
        return max(0.0, min(100.0, score))

    @staticmethod
    def _flesch_kincaid_grade(word_count: int, sentence_count: int, syllable_count: int) -> float:
        """Calculate Flesch-Kincaid Grade Level.

        Indicates the US school grade level needed to understand the text.

        Formula: 0.39 * (words/sentences) + 11.8 * (syllables/words) - 15.59

        Args:
            word_count: Total word count.
            sentence_count: Total sentence count.
            syllable_count: Total syllable count.

        Returns:
            Grade level (e.g., 8.5 = 8th grade).
        """
        if word_count == 0:
            return 0.0
        sent = max(sentence_count, 1)
        asl = word_count / sent
        asw = syllable_count / word_count
        grade = (0.39 * asl) + (11.8 * asw) - 15.59
        return max(0.0, round(grade, 1))

    @classmethod
    def _get_ease_label(cls, score: float) -> str:
        """Get human-readable label for a Flesch Reading Ease score.

        Args:
            score: Flesch Reading Ease score (0-100).

        Returns:
            Label like "Standard", "Easy", etc.
        """
        for low, high, label in cls.EASE_LABELS:
            if low <= score < high:
                return label
        return "Very Confusing"

    # ------------------------------------------------------------------
    # Keyword analysis
    # ------------------------------------------------------------------

    @staticmethod
    def _find_keyword_variations(text: str, keyword: str) -> List[str]:
        """Find keyword variations (e.g., plural forms, stemming variants) in text.

        Args:
            text: Plain text content.
            keyword: Lowercase keyword to search for.

        Returns:
            List of unique keyword variations found in the text.
        """
        words = re.findall(r"[A-Za-z]+", text.lower())
        variations: List[str] = []
        kw_len = len(keyword)

        for w in set(words):
            if w == keyword:
                variations.append(w)
            elif keyword in w and len(w) <= kw_len + 4:
                variations.append(w)
        return sorted(set(variations))

    # ------------------------------------------------------------------
    # Heading structure
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_heading_stats(html: str) -> Dict[str, int]:
        """Extract counts of H1-H6 tags from HTML content.

        Args:
            html: Raw HTML or text with heading markup.

        Returns:
            Dictionary mapping heading tag names (h1-h6) to counts.
        """
        stats: Dict[str, int] = {}
        for i in range(1, 7):
            tag = f"h{i}"
            count_open = len(re.findall(rf'<{tag}[\s>]', html, re.IGNORECASE))
            # Also count self-closing or implicit headings from markdown (# style)
            count_md = len(re.findall(rf'(?m)^{"#" * i}\s', html))
            stats[tag] = count_open + count_md
        return stats

    # ------------------------------------------------------------------
    # Image analysis
    # ------------------------------------------------------------------

    @staticmethod
    def _analyze_images(html: str) -> Dict[str, Any]:
        """Count images and check for alt text presence.

        Args:
            html: Raw HTML content.

        Returns:
            Dictionary with total, with_alt, and missing_alt counts.
        """
        img_tags = re.findall(r'<img[^>]+>', html, re.IGNORECASE)
        total = len(img_tags)
        with_alt = 0
        for tag in img_tags:
            if re.search(r'\balt\s*=\s*["\']', tag, re.IGNORECASE):
                with_alt += 1
        return {
            "total": total,
            "with_alt": with_alt,
            "missing_alt": total - with_alt,
        }

    # ------------------------------------------------------------------
    # Content score & recommendations
    # ------------------------------------------------------------------

    @staticmethod
    def _calculate_content_score(
        word_count: int,
        sentence_count: int,
        readability: float,
        keyword_density: float,
        alt_text_score: float,
        heading_stats: Dict[str, int],
    ) -> float:
        """Calculate an overall content quality score (0-100).

        Factors:
            - Word count adequacy (at least 300 words for SEO)
            - Readability score
            - Keyword density in optimal range (1-3%)
            - Alt text coverage
            - H1 presence

        Args:
            word_count: Total words.
            sentence_count: Total sentences.
            readability: Flesch Reading Ease score.
            keyword_density: Keyword density percentage.
            alt_text_score: Alt text coverage score (0-100).
            heading_stats: Dict of heading tag counts.

        Returns:
            Composite content score (0-100).
        """
        score = 0.0

        # Word count (ideal: 300+ for SEO, diminishing returns after 2000)
        if word_count >= 300:
            score += 25
        elif word_count >= 100:
            score += word_count / 300 * 25
        else:
            score += word_count / 100 * 10

        # Readability (target: 60-70 for web content)
        if 60 <= readability <= 80:
            score += 25
        elif 50 <= readability < 60:
            score += 20
        elif readability > 80:
            score += 15  # Too simple for some topics
        else:
            score += readability / 100 * 15

        # Keyword density (ideal: 1-3%)
        if keyword_density > 0:
            if 1.0 <= keyword_density <= 3.0:
                score += 20
            elif 0.5 <= keyword_density < 1.0 or 3.0 < keyword_density <= 5.0:
                score += 12
            elif keyword_density > 5.0:
                score += 5  # Possible keyword stuffing
            else:
                score += keyword_density / 1.0 * 8
        else:
            score += 10  # No keyword target provided

        # Alt text
        score += alt_text_score / 100 * 15

        # Heading structure (H1 presence)
        h1_count = heading_stats.get("h1", 0)
        if h1_count == 1:
            score += 15
        elif h1_count > 1:
            score += 8
        else:
            score += 3

        return max(0.0, min(100.0, score))

    @staticmethod
    def _build_content_recommendations(
        word_count: int,
        sentence_count: int,
        readability: float,
        grade_level: float,
        keyword: Optional[str],
        keyword_density: float,
        alt_score: float,
        images_missing_alt: int,
        heading_stats: Dict[str, int],
    ) -> List[str]:
        """Build actionable content recommendations.

        Returns:
            List of recommendation strings.
        """
        recs: List[str] = []

        if word_count < 300:
            recs.append(
                f"Increase content length to at least 300 words (current: {word_count}). "
                "Longer content tends to rank better."
            )
        if sentence_count < 10 and word_count > 50:
            recs.append("Break up long sentences to improve readability.")

        if readability < 50:
            recs.append(
                f"Content is difficult to read (score: {readability:.1f}). "
                "Simplify language and shorten sentences for better engagement."
            )
        elif readability > 80 and word_count > 200:
            recs.append(
                f"Content may be too simple (score: {readability:.1f}). "
                "Consider adding more substantive detail for advanced readers."
            )

        if grade_level > 12:
            recs.append(
                f"Grade level {grade_level:.1f} is above high-school level. "
                "Aim for 8th-10th grade reading level for broader accessibility."
            )

        if keyword and keyword_density > 0:
            if keyword_density > 4.0:
                recs.append(
                    f"Keyword density is high ({keyword_density:.1f}%). "
                    "This may trigger keyword stuffing penalties. Aim for 1-3%."
                )
            elif keyword_density < 0.5:
                recs.append(
                    f"Keyword density is low ({keyword_density:.1f}%). "
                    "Consider adding more natural keyword mentions."
                )

        if images_missing_alt > 0:
            recs.append(
                f"{images_missing_alt} image(s) missing alt text. "
                "Add descriptive alt attributes for accessibility and SEO."
            )

        h1_count = heading_stats.get("h1", 0)
        if h1_count == 0:
            recs.append("Missing H1 heading. Add a single descriptive H1 tag.")
        elif h1_count > 1:
            recs.append(
                f"Multiple H1 tags found ({h1_count}). Use exactly one H1 per page."
            )

        h2_count = heading_stats.get("h2", 0)
        if h2_count == 0 and word_count > 200:
            recs.append("Consider adding H2 subheadings to structure your content.")

        return recs


# ------------------------------------------------------------------
# Runnable test (python -m seo_swarm.content_analyzer.engine)
# ------------------------------------------------------------------
if __name__ == "__main__":
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head><title>SEO Tips for Beginners</title></head>
    <body>
        <h1>The Ultimate SEO Guide for 2026</h1>
        <p>Search engine optimization is the practice of increasing the quantity
        and quality of traffic to your website through organic search engine results.
        SEO is essential for any business that wants to be found online. By optimizing
        your site for search engines, you can attract more visitors, generate leads,
        and increase revenue.</p>

        <h2>Why SEO Matters</h2>
        <p>SEO is important because it helps your website rank higher in search results.
        When people search for terms related to your business, you want to appear at the
        top. Studies show that the first result gets about 30% of all clicks, while the
        tenth result gets less than 3%.</p>

        <h2>On-Page SEO Best Practices</h2>
        <p>On-page SEO refers to the optimization of individual web pages. This includes
        optimizing your title tags, meta descriptions, and content. Make sure your keyword
        appears in the title, first paragraph, and throughout your content naturally.</p>

        <h3>Title Tag Optimization</h3>
        <p>Your title tag is one of the most important on-page SEO factors. It should
        include your primary keyword and be between 50-60 characters long.</p>

        <h2>Technical SEO Fundamentals</h2>
        <p>Technical SEO ensures search engines can crawl and index your site effectively.
        This includes having a clean site architecture, fast loading speeds, and a
        mobile-friendly design.</p>

        <img src="seo-chart.png" alt="SEO ranking factors chart">
        <img src="diagram.jpg" alt="">
        <img src="photo.png">

        <p>In conclusion, SEO is a long-term strategy that requires consistent effort.
        Focus on creating high-quality content, building relevant backlinks, and ensuring
        your technical foundation is solid.</p>
    </body>
    </html>
    """

    analyzer = ContentAnalyzer()
    result = analyzer.analyze(sample_html, keyword="SEO")

    print("=" * 60)
    print("  CONTENT ANALYSIS REPORT")
    print("=" * 60)
    print(f"  Readability Score:     {result.readability_score:.1f} ({result.reading_ease_label})")
    print(f"  Grade Level:          {result.grade_level:.1f}")
    print(f"  Words:                {result.word_count}")
    print(f"  Sentences:            {result.sentence_count}")
    print(f"  Avg Sentence Length:  {result.avg_sentence_length:.1f} words")
    print(f"  Avg Word Length:      {result.avg_word_length:.2f} chars")
    print(f"  Syllables:            {result.syllable_count}")
    print(f"  Paragraphs:           {result.paragraph_count}")
    print(f"  Estimated Read Time:  {result.estimated_reading_time_minutes:.1f} min")
    print("-" * 60)
    print(f"  Keyword:              '{result.keyword}'")
    print(f"  Keyword Count:        {result.keyword_count}")
    print(f"  Keyword Density:      {result.keyword_density:.2f}%")
    if result.keyword_variations:
        print(f"  Variations:           {', '.join(result.keyword_variations[:5])}")
    print("-" * 60)
    print(f"  Heading Stats:        {result.heading_stats}")
    print(f"  Images:               {result.image_count} total, "
          f"{result.images_with_alt} with alt, "
          f"{result.images_missing_alt} missing alt")
    print(f"  Alt Text Score:       {result.alt_text_score:.1f}%")
    print("-" * 60)
    print(f"  Content Score:        {result.content_score:.1f}/100")
    print(f"  Recommendations ({len(result.recommendations)}):")
    for rec in result.recommendations:
        print(f"    \u2022 {rec}")
    print("=" * 60)

    # Test to_dict
    d = result.to_dict()
    print("\n  Dict keys:", sorted(d.keys()))
