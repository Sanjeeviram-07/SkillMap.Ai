"""
services/db_service.py — Centralized SQLite database layer.

Handles:
  - users table (with auth_provider, created_at)
  - quiz_history table (per-user quiz attempt tracking)
"""

import sqlite3
import bcrypt
import json
from datetime import datetime

DB_PATH = "users.db"


# ─── Schema ──────────────────────────────────────────────────────────────────

def init_db():
    """Create tables if they don't exist and migrate old schema if needed."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # ── users table ──
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            domain TEXT DEFAULT '',
            auth_provider TEXT DEFAULT 'email',
            created_at TEXT DEFAULT (datetime('now'))
        )
    ''')

    # ── Migrate: add missing columns to old users table ──
    existing_cols = {row[1] for row in c.execute("PRAGMA table_info(users)").fetchall()}
    if "auth_provider" not in existing_cols:
        c.execute("ALTER TABLE users ADD COLUMN auth_provider TEXT DEFAULT 'email'")
    if "created_at" not in existing_cols:
        c.execute("ALTER TABLE users ADD COLUMN created_at TEXT DEFAULT ''")

    # ── quiz_history table ──
    c.execute('''
        CREATE TABLE IF NOT EXISTS quiz_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            topic TEXT NOT NULL,
            difficulty TEXT NOT NULL DEFAULT 'Mixed',
            total_questions INTEGER NOT NULL,
            correct_answers INTEGER NOT NULL,
            accuracy REAL NOT NULL DEFAULT 0.0,
            weak_topics TEXT DEFAULT '[]',
            attempted_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()


# ─── Password helpers ────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


# ─── User CRUD ───────────────────────────────────────────────────────────────

def _user_row_to_dict(row) -> dict | None:
    """Convert a raw sqlite row to a clean user dict."""
    if not row:
        return None
    return {
        "id": row[0],
        "name": row[1],
        "email": row[2],
        "domain": row[4] or "",
        "auth_provider": row[5] if len(row) > 5 else "email",
    }


def signup_user(name: str, email: str, password: str, domain: str = "") -> tuple[bool, str]:
    """Register a new user with email/password."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (name, email, password_hash, domain, auth_provider, created_at) VALUES (?,?,?,?,?,?)",
            (name, email, hash_password(password), domain, "email", datetime.now().isoformat()),
        )
        conn.commit()
        conn.close()
        return True, "Account created successfully! Please Sign In."
    except sqlite3.IntegrityError:
        return False, "Email already exists. Please Sign In."
    except Exception as e:
        return False, f"An error occurred: {e}"


def login_user(email: str, password: str) -> tuple[bool, dict | str]:
    """Authenticate with email/password. Returns (success, user_dict | error_msg)."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = c.fetchone()
    conn.close()

    if row and row[3] and check_password(password, row[3]):
        return True, _user_row_to_dict(row)
    return False, "Invalid email or password."


def get_or_create_google_user(email: str, name: str) -> dict | None:
    """
    For Google OAuth: find existing user by email, or create a new one.
    Returns a user dict.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = c.fetchone()

    if not row:
        c.execute(
            "INSERT INTO users (name, email, password_hash, domain, auth_provider, created_at) VALUES (?,?,?,?,?,?)",
            (name, email, None, "", "google", datetime.now().isoformat()),
        )
        conn.commit()
        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = c.fetchone()

    conn.close()
    return _user_row_to_dict(row)


# ─── Quiz History ────────────────────────────────────────────────────────────

def save_quiz_attempt(
    user_id: int,
    topic: str,
    difficulty: str,
    total_questions: int,
    correct_answers: int,
    accuracy: float,
    weak_topics: list[str] | None = None,
) -> int:
    """Save a completed quiz attempt. Returns the new row ID."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """INSERT INTO quiz_history
           (user_id, topic, difficulty, total_questions, correct_answers, accuracy, weak_topics, attempted_at)
           VALUES (?,?,?,?,?,?,?,?)""",
        (
            user_id,
            topic,
            difficulty,
            total_questions,
            correct_answers,
            round(accuracy, 1),
            json.dumps(weak_topics or []),
            datetime.now().isoformat(),
        ),
    )
    row_id = c.lastrowid
    conn.commit()
    conn.close()
    return row_id


def get_quiz_history(user_id: int, limit: int = 50) -> list[dict]:
    """Fetch quiz history for a user, latest first."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """SELECT id, topic, difficulty, total_questions, correct_answers,
                  accuracy, weak_topics, attempted_at
           FROM quiz_history
           WHERE user_id = ?
           ORDER BY attempted_at DESC
           LIMIT ?""",
        (user_id, limit),
    )
    rows = c.fetchall()
    conn.close()

    history = []
    for r in rows:
        history.append({
            "id": r[0],
            "topic": r[1],
            "difficulty": r[2],
            "total_questions": r[3],
            "correct_answers": r[4],
            "accuracy": r[5],
            "weak_topics": json.loads(r[6]) if r[6] else [],
            "attempted_at": r[7],
        })
    return history


def get_quiz_stats(user_id: int) -> dict:
    """Aggregate quiz statistics for a user."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        "SELECT COUNT(*), AVG(accuracy) FROM quiz_history WHERE user_id = ?",
        (user_id,),
    )
    row = c.fetchone()
    total_quizzes = row[0] or 0
    avg_accuracy = round(row[1], 1) if row[1] else 0.0

    # Weakest topics: topics with lowest average accuracy (min 1 attempt)
    c.execute(
        """SELECT topic, AVG(accuracy) as avg_acc, COUNT(*) as cnt
           FROM quiz_history WHERE user_id = ?
           GROUP BY topic
           HAVING cnt >= 1
           ORDER BY avg_acc ASC
           LIMIT 3""",
        (user_id,),
    )
    weak_topics = [{"topic": r[0], "avg_accuracy": round(r[1], 1), "attempts": r[2]} for r in c.fetchall()]

    conn.close()
    return {
        "total_quizzes": total_quizzes,
        "avg_accuracy": avg_accuracy,
        "weak_topics": weak_topics,
    }
