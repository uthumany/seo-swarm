"""
SEO SWARM - Health Monitor Engine
Continuous SEO health tracking with alerting and trend analysis.
"""

import time
import sqlite3
import json
import uuid
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple


@dataclass
class HealthSnapshot:
    """A single point-in-time health snapshot."""
    snapshot_id: str
    target: str
    timestamp: float
    scores: Dict[str, float]         # metric → score
    total_issues: int
    status: str                       # healthy, warning, critical


@dataclass
class Alert:
    """SEO health alert."""
    severity: str                     # critical, warning, info
    message: str
    metric: str
    threshold: float
    current_value: float
    target: str
    snapshot_id: str
    created_at: float = field(default_factory=time.time)


class HealthMonitor:
    """Monitor SEO health over time and raise alerts on threshold breaches."""

    # Default alert thresholds
    DEFAULT_THRESHOLDS: Dict[str, Dict[str, float]] = {
        "overall_score":      {"warning": 70, "critical": 50},
        "broken_pages":       {"warning": 5,  "critical": 20},
        "mobile_score":       {"warning": 60, "critical": 40},
        "performance_score":  {"warning": 60, "critical": 40},
        "meta_completeness":  {"warning": 70, "critical": 50},
        "schema_coverage":    {"warning": 60, "critical": 30},
        "ranking_position":   {"warning": 20, "critical": 50},   # higher = worse
        "page_speed":         {"warning": 60, "critical": 40},
        "ssl_valid":          {"warning": 1,  "critical": 1},    # boolean: 0=ok, 1=broken
    }

    def __init__(self, db_path: Optional[str] = None, thresholds: Optional[Dict] = None):
        if db_path is None:
            db_dir = Path.home() / ".seo-swarm" / "monitor"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = db_dir / "health.db"

        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.thresholds = thresholds or self.DEFAULT_THRESHOLDS
        self._init_db()

    def _init_db(self):
        """Initialize health monitoring tables."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                snapshot_id TEXT PRIMARY KEY,
                target TEXT NOT NULL,
                timestamp REAL NOT NULL,
                scores TEXT NOT NULL,         -- JSON dict
                total_issues INTEGER DEFAULT 0,
                status TEXT DEFAULT 'healthy',
                created_at REAL
            )
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_snapshots_target
            ON snapshots(target, timestamp)
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id TEXT NOT NULL,
                target TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                metric TEXT NOT NULL,
                threshold REAL,
                current_value REAL,
                created_at REAL,
                FOREIGN KEY (snapshot_id) REFERENCES snapshots(snapshot_id)
            )
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_alerts_target
            ON alerts(target, created_at)
        """)
        self.conn.commit()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def take_snapshot(self, target: str, scores: Dict[str, float]) -> str:
        """Record a health snapshot and evaluate alerts.

        Returns the snapshot_id.
        """
        snapshot_id = str(uuid.uuid4())
        now = time.time()

        # Count issues from scores (lower is worse, except ranking_position/broken_pages)
        total_issues = 0
        for metric, value in scores.items():
            th = self.thresholds.get(metric, {})
            if metric in ("ranking_position", "broken_pages", "ssl_valid"):
                if th.get("critical") is not None and value >= th["critical"]:
                    total_issues += 9
                elif th.get("warning") is not None and value >= th["warning"]:
                    total_issues += 3
            else:
                if th.get("critical") is not None and value <= th["critical"]:
                    total_issues += 9
                elif th.get("warning") is not None and value <= th["warning"]:
                    total_issues += 3

        # Overall status
        if total_issues >= 18:
            status = "critical"
        elif total_issues >= 6:
            status = "warning"
        else:
            status = "healthy"

        self.conn.execute(
            """INSERT INTO snapshots (snapshot_id, target, timestamp, scores,
                                      total_issues, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (snapshot_id, target, now, json.dumps(scores), total_issues, status, now),
        )

        # Evaluate and store alerts
        self._evaluate_alerts(snapshot_id, target, scores, now)

        self.conn.commit()
        return snapshot_id

    def _evaluate_alerts(self, snapshot_id: str, target: str,
                         scores: Dict[str, float], timestamp: float):
        """Check scores against thresholds and create alert rows."""
        for metric, value in scores.items():
            th = self.thresholds.get(metric)
            if th is None:
                continue

            if metric in ("ranking_position", "broken_pages", "ssl_valid"):
                # Higher values are worse
                if th.get("critical") is not None and value >= th["critical"]:
                    severity = "critical"
                elif th.get("warning") is not None and value >= th["warning"]:
                    severity = "warning"
                else:
                    continue
            else:
                # Lower values are worse
                if th.get("critical") is not None and value <= th["critical"]:
                    severity = "critical"
                elif th.get("warning") is not None and value <= th["warning"]:
                    severity = "warning"
                else:
                    continue

            used_threshold = th.get(severity, 0)
            message = (
                f"[{severity.upper()}] {metric} is {value} "
                f"(threshold: {severity} at {used_threshold})"
            )
            self.conn.execute(
                """INSERT INTO alerts
                   (snapshot_id, target, severity, message, metric, threshold, current_value, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (snapshot_id, target, severity, message, metric, used_threshold, value, timestamp),
            )

    def get_history(self, target: str, days: int = 30) -> List[HealthSnapshot]:
        """Retrieve health snapshots for a target over the given number of days."""
        cutoff = time.time() - days * 86400
        rows = self.conn.execute(
            """SELECT snapshot_id, target, timestamp, scores, total_issues, status
               FROM snapshots
               WHERE target = ? AND timestamp >= ?
               ORDER BY timestamp ASC""",
            (target, cutoff),
        ).fetchall()

        return [
            HealthSnapshot(
                snapshot_id=row["snapshot_id"],
                target=row["target"],
                timestamp=row["timestamp"],
                scores=json.loads(row["scores"]),
                total_issues=row["total_issues"],
                status=row["status"],
            )
            for row in rows
        ]

    def check_alerts(self, target: str, days: int = 7) -> List[Alert]:
        """Retrieve recent alerts for a target."""
        cutoff = time.time() - days * 86400
        rows = self.conn.execute(
            """SELECT snapshot_id, target, severity, message, metric,
                      threshold, current_value, created_at
               FROM alerts
               WHERE target = ? AND created_at >= ?
               ORDER BY created_at DESC""",
            (target, cutoff),
        ).fetchall()

        return [
            Alert(
                severity=row["severity"],
                message=row["message"],
                metric=row["metric"],
                threshold=row["threshold"],
                current_value=row["current_value"],
                target=row["target"],
                snapshot_id=row["snapshot_id"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def get_trend_data(self, target: str, metric: str, days: int = 30) -> List[Tuple[float, float]]:
        """Return (timestamp, value) pairs for a metric over time.

        Useful for feeding into charting/visualization libraries.
        """
        cutoff = time.time() - days * 86400
        rows = self.conn.execute(
            """SELECT timestamp, scores FROM snapshots
               WHERE target = ? AND timestamp >= ?
               ORDER BY timestamp ASC""",
            (target, cutoff),
        ).fetchall()

        data: List[Tuple[float, float]] = []
        for row in rows:
            scores = json.loads(row["scores"])
            if metric in scores:
                data.append((row["timestamp"], scores[metric]))
        return data

    def get_summary(self, target: str) -> Dict[str, Any]:
        """Return a high-level health summary for a target."""
        latest = self.conn.execute(
            """SELECT * FROM snapshots
               WHERE target = ?
               ORDER BY timestamp DESC LIMIT 1"""
        , (target,)).fetchone()

        if not latest:
            return {"target": target, "status": "no_data"}

        alert_count = self.conn.execute(
            "SELECT COUNT(*) AS cnt FROM alerts WHERE target = ?", (target,)
        ).fetchone()["cnt"]

        # Weekly snapshot count
        week_ago = time.time() - 7 * 86400
        week_count = self.conn.execute(
            "SELECT COUNT(*) AS cnt FROM snapshots WHERE target = ? AND timestamp >= ?",
            (target, week_ago),
        ).fetchone()["cnt"]

        scores = json.loads(latest["scores"])
        return {
            "target": target,
            "latest_snapshot_id": latest["snapshot_id"],
            "latest_status": latest["status"],
            "latest_scores": scores,
            "total_issues": latest["total_issues"],
            "total_alerts": alert_count,
            "snapshots_this_week": week_count,
            "last_updated": latest["timestamp"],
        }

    def close(self):
        """Close the database connection."""
        self.conn.close()

    def clear(self, target: Optional[str] = None):
        """Remove health data. If target is given, only clear that target."""
        if target:
            self.conn.execute("DELETE FROM alerts WHERE target = ?", (target,))
            self.conn.execute("DELETE FROM snapshots WHERE target = ?", (target,))
        else:
            self.conn.execute("DELETE FROM alerts")
            self.conn.execute("DELETE FROM snapshots")
        self.conn.commit()
