"""
SEO SWARM - Rank Tracker Engine
Keyword position tracking with SQLite storage and trend analysis.
"""

import time
import random
import sqlite3
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class PositionEntry:
    """Single keyword position data point."""
    keyword: str
    url: str
    position: int
    search_engine: str
    date: str
    previous_position: Optional[int] = None
    change: Optional[int] = None
    trend: str = "stable"  # up, down, stable


class RankTracker:
    """Track keyword rankings over time with SQLite persistence."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_dir = Path.home() / ".seo-swarm" / "tracker"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = db_dir / "rankings.db"

        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        """Initialize rankings tables."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS rankings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT NOT NULL,
                url TEXT NOT NULL,
                position INTEGER NOT NULL,
                search_engine TEXT DEFAULT 'google',
                date TEXT NOT NULL,
                created_at REAL
            )
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_rankings_keyword
            ON rankings(keyword, date)
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_rankings_url
            ON rankings(url)
        """)
        self.conn.commit()

    def _simulate_position(self, keyword: str, url: str) -> int:
        """Generate a deterministic-but-variable position estimate for a keyword/url pair.

        In production this would query a real search API (Google, Bing, etc.).
        The simulation uses a hash of keyword+url to produce stable base positions
        that vary slightly over time.
        """
        seed = hashlib.md5(f"{keyword}:{url}".encode()).hexdigest()
        base = int(seed[:8], 16) % 100 + 1
        noise = int(time.time() // 86400) % 7  # daily variation 0-6
        return max(1, min(100, base + (noise - 3)))

    def _derive_trend(self, current: int, previous: Optional[int]) -> str:
        """Derive position trend indicator."""
        if previous is None:
            return "stable"
        if current < previous:
            return "up"       # lower number = better rank
        elif current > previous:
            return "down"
        return "stable"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def track(self, keyword: str, url: str, search_engine: str = "google") -> Dict[str, Any]:
        """Record a keyword position and return the current estimate.

        Returns a dict with keyword, url, position, date, search_engine,
        previous_position, change, and trend.
        """
        position = self._simulate_position(keyword, url)
        date = time.strftime("%Y-%m-%d")

        # Look up the most recent previous position
        prev = self.conn.execute(
            """SELECT position FROM rankings
               WHERE keyword = ? AND url = ? AND search_engine = ?
               ORDER BY date DESC LIMIT 1""",
            (keyword, url, search_engine),
        ).fetchone()

        previous_position = prev["position"] if prev else None
        change = (previous_position - position) if previous_position is not None else None
        trend = self._derive_trend(position, previous_position)

        # Persist
        self.conn.execute(
            """INSERT INTO rankings (keyword, url, position, search_engine, date, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (keyword, url, position, search_engine, date, time.time()),
        )
        self.conn.commit()

        return {
            "keyword": keyword,
            "url": url,
            "position": position,
            "date": date,
            "search_engine": search_engine,
            "previous_position": previous_position,
            "change": change,
            "trend": trend,
        }

    def get_history(self, keyword: str, days: int = 30) -> List[Dict[str, Any]]:
        """Retrieve position history for a keyword over the given number of days."""
        cutoff_date = time.strftime("%Y-%m-%d", time.localtime(time.time() - days * 86400))
        rows = self.conn.execute(
            """SELECT keyword, url, position, search_engine, date
               FROM rankings
               WHERE keyword LIKE ? AND date >= ?
               ORDER BY date ASC""",
            (f"%{keyword}%", cutoff_date),
        ).fetchall()

        results = []
        prev_pos = None
        for row in rows:
            pos = row["position"]
            trend = self._derive_trend(pos, prev_pos)
            results.append({
                "keyword": row["keyword"],
                "url": row["url"],
                "position": pos,
                "search_engine": row["search_engine"],
                "date": row["date"],
                "trend": trend,
            })
            prev_pos = pos
        return results

    def get_trends(self) -> Dict[str, Any]:
        """Return top gainers and top losers based on most recent position changes."""
        rows = self.conn.execute(
            """SELECT keyword, url, position, date,
                       LAG(position) OVER (PARTITION BY keyword, url ORDER BY date) AS prev_position
               FROM rankings
               WHERE date >= date('now', '-7 days')
               ORDER BY date DESC"""
        ).fetchall()

        changes: Dict[str, Dict] = {}
        for row in rows:
            key = row["keyword"]
            if key not in changes and row["prev_position"] is not None:
                diff = row["prev_position"] - row["position"]  # positive = gain
                changes[key] = {
                    "keyword": key,
                    "url": row["url"],
                    "current_position": row["position"],
                    "previous_position": row["prev_position"],
                    "change": diff,
                    "trend": "up" if diff > 0 else ("down" if diff < 0 else "stable"),
                }

        sorted_changes = sorted(
            changes.values(), key=lambda x: x["change"], reverse=True
        )

        top_gainers = [c for c in sorted_changes if c["change"] > 0][:10]
        top_losers = [c for c in sorted_changes if c["change"] < 0][:10]
        top_losers.sort(key=lambda x: x["change"])  # most negative first
        stable = [c for c in sorted_changes if c["change"] == 0][:10]

        return {
            "top_gainers": top_gainers,
            "top_losers": top_losers,
            "stable": stable,
            "total_tracked": len(changes),
        }

    def get_summary(self) -> Dict[str, Any]:
        """Return aggregate summary: total keywords, avg position, best/worst."""
        count_row = self.conn.execute(
            "SELECT COUNT(DISTINCT keyword) AS cnt FROM rankings"
        ).fetchone()
        total_keywords = count_row["cnt"] if count_row else 0

        avg_row = self.conn.execute(
            "SELECT AVG(position) AS avg_pos FROM rankings"
        ).fetchone()
        avg_position = round(avg_row["avg_pos"], 1) if avg_row["avg_pos"] else 0.0

        # Most recent position per keyword for best/worst
        latest = self.conn.execute(
            """SELECT keyword, position FROM rankings
               WHERE (keyword, date) IN (
                   SELECT keyword, MAX(date) FROM rankings GROUP BY keyword
               )
               ORDER BY position ASC"""
        ).fetchall()

        best = {"keyword": latest[0]["keyword"], "position": latest[0]["position"]} if latest else None
        worst = {"keyword": latest[-1]["keyword"], "position": latest[-1]["position"]} if latest else None

        # URL-level grouping
        url_row = self.conn.execute(
            "SELECT COUNT(DISTINCT url) AS cnt FROM rankings"
        ).fetchone()
        total_urls = url_row["cnt"] if url_row else 0

        if count_row:
            search_engine_counts = {}
            engine_rows = self.conn.execute(
                "SELECT search_engine, COUNT(*) AS cnt FROM rankings GROUP BY search_engine"
            ).fetchall()
            for r in engine_rows:
                search_engine_counts[r["search_engine"]] = r["cnt"]

        return {
            "total_keywords": total_keywords,
            "total_urls": total_urls,
            "average_position": avg_position,
            "best_ranking": best,
            "worst_ranking": worst,
            "search_engines": search_engine_counts if count_row else {},
        }

    def close(self):
        """Close the database connection."""
        self.conn.close()

    def clear(self):
        """Remove all ranking data."""
        self.conn.execute("DELETE FROM rankings")
        self.conn.commit()
