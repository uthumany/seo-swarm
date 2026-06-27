"""
SEO SWARM - Memory Engine
Self-improving local + cloud memory with persistent storage.
"""

import json
import time
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional


class MemoryEngine:
    """Hybrid memory system: local SQLite + cloud-ready architecture."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_dir = Path.home() / ".seo-swarm" / "memory"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = db_dir / "memory.db"

        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(self.db_path))
        self._init_db()

    def _init_db(self):
        """Initialize memory tables."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                category TEXT DEFAULT 'general',
                score REAL DEFAULT 0.0,
                access_count INTEGER DEFAULT 0,
                created_at REAL,
                updated_at REAL,
                UNIQUE(key)
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS learnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern TEXT NOT NULL,
                insight TEXT,
                confidence REAL DEFAULT 0.5,
                source TEXT,
                created_at REAL
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE,
                agent_id TEXT,
                target TEXT,
                result TEXT,
                duration REAL,
                created_at REAL
            )
        """)
        self.conn.commit()

    def save(self, key: str, value: str, category: str = "general", score: float = 1.0):
        """Save a memory entry."""
        now = time.time()
        self.conn.execute("""
            INSERT INTO memory (key, value, category, score, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value=excluded.value, score=excluded.score,
                updated_at=excluded.updated_at,
                access_count=access_count + 1
        """, (key, value, category, score, now, now))
        self.conn.commit()

    def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search memory by query."""
        cursor = self.conn.execute("""
            SELECT key, value, category, score, access_count, updated_at
            FROM memory
            WHERE key LIKE ? OR value LIKE ?
            ORDER BY score DESC, access_count DESC
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", limit))

        results = []
        for row in cursor:
            results.append({
                "key": row[0], "value": row[1], "category": row[2],
                "score": row[3], "access_count": row[4], "updated_at": row[5],
            })
            # Update access count
            self.conn.execute("UPDATE memory SET access_count = access_count + 1 WHERE key = ?", (row[0],))
        self.conn.commit()
        return results

    def learn(self, pattern: str, insight: str, confidence: float = 0.5, source: str = "agent"):
        """Record a learning/insight."""
        self.conn.execute("""
            INSERT INTO learnings (pattern, insight, confidence, source, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (pattern, insight, confidence, source, time.time()))
        self.conn.commit()

    def get_learnings(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent learnings."""
        cursor = self.conn.execute("""
            SELECT pattern, insight, confidence, source, created_at
            FROM learnings ORDER BY created_at DESC LIMIT ?
        """, (limit,))
        return [
            {"pattern": r[0], "insight": r[1], "confidence": r[2],
             "source": r[3], "created_at": r[4]}
            for r in cursor
        ]

    def log_session(self, agent_id: str, target: str, result: Dict[str, Any], duration: float):
        """Log an agent session."""
        import uuid
        sid = str(uuid.uuid4())[:8]
        self.conn.execute("""
            INSERT INTO sessions (session_id, agent_id, target, result, duration, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (sid, agent_id, target, json.dumps(result, default=str), duration, time.time()))
        self.conn.commit()

    def stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        mem_count = self.conn.execute("SELECT COUNT(*) FROM memory").fetchone()[0]
        learn_count = self.conn.execute("SELECT COUNT(*) FROM learnings").fetchone()[0]
        sess_count = self.conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        return {
            "total_memories": mem_count,
            "total_learnings": learn_count,
            "total_sessions": sess_count,
            "db_size_kb": self.db_path.stat().st_size // 1024 if self.db_path.exists() else 0,
        }

    def close(self):
        """Close database connection."""
        self.conn.close()

    def clear(self):
        """Clear all memory (dangerous - use with caution)."""
        self.conn.execute("DELETE FROM memory")
        self.conn.execute("DELETE FROM learnings")
        self.conn.commit()
