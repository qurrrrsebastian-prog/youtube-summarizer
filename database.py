"""database.py — SQLite persistence for the YouTube Summarizer.
Author: Avatar Putra Sigit | GitHub: qurrrrsebastian-prog
"""
import os
import sqlite3
from datetime import datetime

import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "app.db")


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection with row access by name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create tables. Call once at app start."""
    conn = get_connection()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, video_url TEXT,
            video_title TEXT, channel_name TEXT, duration TEXT, summary TEXT,
            key_insights TEXT, actionable_takeaways TEXT, mode TEXT);
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, user TEXT,
            action TEXT, details TEXT);
        """
    )
    conn.commit()
    conn.close()


def add_log(action: str, details: str = "", user: str = "anonymous") -> None:
    """Append an entry to the audit log."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO audit_log (timestamp, user, action, details) VALUES (?, ?, ?, ?)",
        (datetime.now().isoformat(timespec="seconds"), user, action, details),
    )
    conn.commit()
    conn.close()


def add_summary(video_url: str, video_title: str, channel_name: str, duration: str,
                summary: str, key_insights: str, actionable_takeaways: str,
                mode: str) -> int:
    """Persist a summary and return its row id."""
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO summaries
           (timestamp, video_url, video_title, channel_name, duration, summary,
            key_insights, actionable_takeaways, mode)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (datetime.now().isoformat(timespec="seconds"), video_url, video_title,
         channel_name, duration, summary, key_insights, actionable_takeaways, mode),
    )
    conn.commit()
    rid = cur.lastrowid
    conn.close()
    return rid


def get_summaries(limit: int = 60) -> pd.DataFrame:
    """Return saved summaries, newest first."""
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM summaries ORDER BY id DESC LIMIT ?", conn, params=[limit])
    conn.close()
    return df


def get_summary(summary_id: int):
    """Return one summary as a dict, or None."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM summaries WHERE id = ?", (summary_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_summary(summary_id: int) -> None:
    """Delete a summary by id."""
    conn = get_connection()
    conn.execute("DELETE FROM summaries WHERE id = ?", (summary_id,))
    conn.commit()
    conn.close()


def clear_summaries() -> None:
    """Delete all summaries."""
    conn = get_connection()
    conn.execute("DELETE FROM summaries")
    conn.commit()
    conn.close()
