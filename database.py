"""
SQLite Database Module for AI Internship Finder
================================================
Provides all database operations for users, profiles, interview sessions,
and chat messages. Uses Python's built-in sqlite3 — zero setup required.

The database file (internai.db) is created automatically in the project root.
"""

import os
import sqlite3
import json
import uuid
import time
from datetime import datetime

def _resolve_db_path():
    """
    Resolve SQLite location with priority:
    1) explicit env override (SQLITE_DB_PATH or DB_PATH_SQLITE)
    2) Render persistent disk default (/var/data/internai.db)
    3) local project file fallback
    """
    explicit = (os.getenv("SQLITE_DB_PATH", "").strip()
                or os.getenv("DB_PATH_SQLITE", "").strip())
    if explicit:
        return explicit

    if os.getenv("RENDER") and os.path.isdir("/var/data"):
        return "/var/data/internai.db"

    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'internai.db')


DB_PATH = _resolve_db_path()
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
if os.getenv("RENDER") and not DB_PATH.startswith("/var/data"):
    print("[WARN] SQLite is not using /var/data. User accounts may reset on Render restarts.")
SQLITE_TIMEOUT_SECONDS = float(os.getenv("SQLITE_TIMEOUT_SECONDS", "30"))
SQLITE_BUSY_TIMEOUT_MS = int(os.getenv("SQLITE_BUSY_TIMEOUT_MS", str(int(SQLITE_TIMEOUT_SECONDS * 1000))))
DB_RETRY_ATTEMPTS = int(os.getenv("DB_RETRY_ATTEMPTS", "5"))


def _get_conn():
    """Get a database connection with row_factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH, timeout=SQLITE_TIMEOUT_SECONDS)
    conn.row_factory = sqlite3.Row
    conn.execute(f"PRAGMA busy_timeout={SQLITE_BUSY_TIMEOUT_MS}")
    conn.execute("PRAGMA journal_mode=WAL")       # Better concurrent read performance
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _run_db_op(func, retries=DB_RETRY_ATTEMPTS, base_delay=0.05):
    """Retry transient SQLite lock/busy errors for better multi-user stability."""
    attempt = 0
    while True:
        try:
            return func()
        except sqlite3.OperationalError as ex:
            msg = str(ex).lower()
            if ("locked" not in msg and "busy" not in msg) or attempt >= retries:
                raise
            time.sleep(base_delay * (2 ** attempt))
            attempt += 1


def init_db():
    """Create all tables if they don't exist."""
    conn = _get_conn()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id              TEXT PRIMARY KEY,
            email           TEXT UNIQUE NOT NULL,
            full_name       TEXT DEFAULT '',
            password_hash   TEXT NOT NULL,
            token           TEXT DEFAULT '',
            target_role     TEXT DEFAULT 'Software Engineer',
            session_id      TEXT DEFAULT '',
            extracted_skills TEXT DEFAULT '[]',
            extracted_role  TEXT DEFAULT 'Software Engineer',
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id         TEXT PRIMARY KEY,
            phone           TEXT DEFAULT '',
            dob             TEXT DEFAULT '',
            location        TEXT DEFAULT '',
            college         TEXT DEFAULT '',
            degree          TEXT DEFAULT '',
            year_of_study   TEXT DEFAULT '',
            experience_years INTEGER DEFAULT 0,
            linkedin        TEXT DEFAULT '',
            github          TEXT DEFAULT '',
            portfolio       TEXT DEFAULT '',
            bio             TEXT DEFAULT '',
            skills_json     TEXT DEFAULT '[]',
            avatar_data     TEXT DEFAULT '',
            updated_at      TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS interview_sessions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         TEXT DEFAULT '',
            date            TEXT DEFAULT '',
            difficulty      TEXT DEFAULT 'Medium',
            role            TEXT DEFAULT '',
            skills_used     TEXT DEFAULT '[]',
            total_questions INTEGER DEFAULT 0,
            correct_count   INTEGER DEFAULT 0,
            wrong_count     INTEGER DEFAULT 0,
            unanswered_count INTEGER DEFAULT 0,
            accuracy_percent INTEGER DEFAULT 0,
            confidence      INTEGER DEFAULT 0,
            created_at      TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS chat_messages (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         TEXT DEFAULT '',
            session_id      TEXT NOT NULL DEFAULT 'default',
            role            TEXT NOT NULL DEFAULT 'user',
            content         TEXT DEFAULT '',
            created_at      TEXT DEFAULT (datetime('now'))
        );
    """)

    conn.commit()
    conn.close()
    print(f"[DB] SQLite database ready at: {DB_PATH}")


# ──────────────────────────────────────────────
#  USER CRUD
# ──────────────────────────────────────────────

def create_user(email, password_hash, full_name='', target_role='Software Engineer',
                session_id='', extracted_skills=None, extracted_role='Software Engineer'):
    """Create a new user. Returns the user dict or None if email already exists."""
    user_id = str(uuid.uuid4())
    token = _generate_token()
    skills_json = json.dumps(extracted_skills or [])

    def _op():
        conn = _get_conn()
        try:
            conn.execute(
                """INSERT INTO users (id, email, full_name, password_hash, token,
                   target_role, session_id, extracted_skills, extracted_role)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, email, full_name, password_hash, token,
                 target_role, session_id, skills_json, extracted_role)
            )
            conn.commit()

            # Also create an empty profile row
            conn.execute(
                "INSERT OR IGNORE INTO user_profiles (user_id) VALUES (?)",
                (user_id,)
            )
            conn.commit()

            return _row_to_user_dict(conn.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
            ).fetchone())
        finally:
            conn.close()

    try:
        return _run_db_op(_op)
    except sqlite3.IntegrityError:
        return None  # email already exists


def get_user_by_email(email):
    """Fetch a user by email. Returns dict or None."""
    conn = _get_conn()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return _row_to_user_dict(row) if row else None


def get_user_by_token(token):
    """Fetch a user by their auth token. Returns dict or None."""
    if not token:
        return None
    conn = _get_conn()
    row = conn.execute("SELECT * FROM users WHERE token = ?", (token,)).fetchone()
    conn.close()
    return _row_to_user_dict(row) if row else None


def get_user_by_id(user_id):
    """Fetch a user by their ID. Returns dict or None."""
    conn = _get_conn()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return _row_to_user_dict(row) if row else None


def update_user(user_id, **kwargs):
    """Update user fields. Pass field names as keyword arguments."""
    if not kwargs:
        return
    # Map Python-friendly names to DB columns
    field_map = {
        'full_name': 'full_name',
        'fullName': 'full_name',
        'password_hash': 'password_hash',
        'token': 'token',
        'target_role': 'target_role',
        'session_id': 'session_id',
        'extracted_skills': 'extracted_skills',
        'extractedSkills': 'extracted_skills',
        'extracted_role': 'extracted_role',
        'extractedRole': 'extracted_role',
    }

    sets = []
    values = []
    for key, val in kwargs.items():
        col = field_map.get(key, key)
        if col == 'extracted_skills' and isinstance(val, list):
            val = json.dumps(val)
        sets.append(f"{col} = ?")
        values.append(val)

    sets.append("updated_at = datetime('now')")
    values.append(user_id)

    def _op():
        conn = _get_conn()
        try:
            conn.execute(f"UPDATE users SET {', '.join(sets)} WHERE id = ?", values)
            conn.commit()
        finally:
            conn.close()

    _run_db_op(_op)


def refresh_user_token(user_id):
    """Generate a new token for the user. Returns the new token."""
    new_token = _generate_token()
    def _op():
        conn = _get_conn()
        try:
            conn.execute("UPDATE users SET token = ?, updated_at = datetime('now') WHERE id = ?",
                         (new_token, user_id))
            conn.commit()
        finally:
            conn.close()

    _run_db_op(_op)
    return new_token


def update_user_password(email, new_password_hash):
    """Update a user's password by email."""
    def _op():
        conn = _get_conn()
        try:
            conn.execute(
                "UPDATE users SET password_hash = ?, updated_at = datetime('now') WHERE email = ?",
                (new_password_hash, email)
            )
            conn.commit()
        finally:
            conn.close()

    _run_db_op(_op)


# ──────────────────────────────────────────────
#  USER PROFILES
# ──────────────────────────────────────────────

def save_profile(user_id, profile_data):
    """Save or update user profile. profile_data is a dict."""
    def _op():
        conn = _get_conn()
        try:
            # Ensure profile row exists
            conn.execute("INSERT OR IGNORE INTO user_profiles (user_id) VALUES (?)", (user_id,))

            fields = {
                'phone': profile_data.get('phone', ''),
                'dob': profile_data.get('dob', ''),
                'location': profile_data.get('location', ''),
                'college': profile_data.get('college', ''),
                'degree': profile_data.get('degree', ''),
                'year_of_study': profile_data.get('year', profile_data.get('year_of_study', '')),
                'experience_years': _safe_int(profile_data.get('exp', profile_data.get('experience_years', 0))),
                'linkedin': profile_data.get('linkedin', ''),
                'github': profile_data.get('github', ''),
                'portfolio': profile_data.get('portfolio', ''),
                'bio': profile_data.get('bio', ''),
                'skills_json': json.dumps(profile_data.get('skills', [])) if isinstance(profile_data.get('skills'), list) else profile_data.get('skills_json', '[]'),
                'avatar_data': profile_data.get('avatar', profile_data.get('avatar_data', '')),
            }

            set_clause = ', '.join(f"{k} = ?" for k in fields)
            values = list(fields.values()) + [user_id]

            conn.execute(
                f"UPDATE user_profiles SET {set_clause}, updated_at = datetime('now') WHERE user_id = ?",
                values
            )
            conn.commit()
        finally:
            conn.close()

    _run_db_op(_op)


def get_profile(user_id):
    """Get user profile as a dict. Returns empty dict if not found."""
    conn = _get_conn()
    row = conn.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    if not row:
        return {}

    profile = dict(row)
    # Parse skills_json back into a list
    try:
        profile['skills'] = json.loads(profile.get('skills_json', '[]'))
    except (json.JSONDecodeError, TypeError):
        profile['skills'] = []
    return profile


# ──────────────────────────────────────────────
#  INTERVIEW SESSIONS
# ──────────────────────────────────────────────

def save_interview_session(user_id, session_data):
    """Save an interview session result. Returns the session ID."""
    def _op():
        conn = _get_conn()
        try:
            cursor = conn.execute(
                """INSERT INTO interview_sessions
                   (user_id, date, difficulty, role, skills_used,
                    total_questions, correct_count, wrong_count, unanswered_count,
                    accuracy_percent, confidence)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    user_id,
                    session_data.get('date', datetime.now().strftime('%Y-%m-%d')),
                    session_data.get('difficulty', 'Medium'),
                    session_data.get('role', ''),
                    json.dumps(session_data.get('skills', [])),
                    session_data.get('total_questions', session_data.get('questions', 0)),
                    session_data.get('correct_count', session_data.get('correct', 0)),
                    session_data.get('wrong_count', session_data.get('wrong', 0)),
                    session_data.get('unanswered_count', 0),
                    session_data.get('accuracy_percent', session_data.get('score', 0)),
                    session_data.get('confidence', 0),
                )
            )
            session_id = cursor.lastrowid
            conn.commit()
            return session_id
        finally:
            conn.close()

    return _run_db_op(_op)


def get_interview_history(user_id, limit=20):
    """Get interview history for a user, newest first."""
    conn = _get_conn()
    rows = conn.execute(
        """SELECT * FROM interview_sessions
           WHERE user_id = ?
           ORDER BY created_at DESC
           LIMIT ?""",
        (user_id, limit)
    ).fetchall()
    conn.close()

    history = []
    for row in rows:
        entry = dict(row)
        try:
            entry['skills'] = json.loads(entry.get('skills_used', '[]'))
        except (json.JSONDecodeError, TypeError):
            entry['skills'] = []
        history.append(entry)
    return history


# ──────────────────────────────────────────────
#  CHAT MESSAGES
# ──────────────────────────────────────────────

def save_chat_message(session_id, role, content, user_id=''):
    """Save a chat message."""
    def _op():
        conn = _get_conn()
        try:
            conn.execute(
                """INSERT INTO chat_messages (user_id, session_id, role, content)
                   VALUES (?, ?, ?, ?)""",
                (user_id, session_id, role, content)
            )
            conn.commit()
        finally:
            conn.close()

    _run_db_op(_op)


def get_chat_messages(session_id, limit=50):
    """Get chat messages for a session, oldest first."""
    conn = _get_conn()
    rows = conn.execute(
        """SELECT role, content FROM chat_messages
           WHERE session_id = ?
           ORDER BY created_at ASC
           LIMIT ?""",
        (session_id, limit)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


# ──────────────────────────────────────────────
#  HELPERS
# ──────────────────────────────────────────────

def _generate_token():
    """Generate a secure random token."""
    import secrets
    return secrets.token_hex(32)


def _safe_int(val):
    """Safely convert a value to int."""
    if isinstance(val, int):
        return val
    try:
        # Handle strings like "2 years"
        import re
        nums = re.findall(r'\d+', str(val))
        return int(nums[0]) if nums else 0
    except (ValueError, IndexError):
        return 0


def _row_to_user_dict(row):
    """Convert a sqlite3.Row to a user dict with parsed skills."""
    if not row:
        return None
    user = dict(row)
    # Parse extracted_skills from JSON string to list
    try:
        user['extractedSkills'] = json.loads(user.get('extracted_skills', '[]'))
    except (json.JSONDecodeError, TypeError):
        user['extractedSkills'] = []
    # Add convenience aliases
    user['_id'] = user.get('id', '')
    user['fullName'] = user.get('full_name', '')
    user['extractedRole'] = user.get('extracted_role', 'Software Engineer')
    return user


def user_to_safe_dict(user):
    """Return user dict without sensitive fields (password_hash)."""
    if not user:
        return {}
    safe = dict(user)
    safe.pop('password_hash', None)
    safe.pop('password', None)
    return safe


# ── Initialize the database on module import ──
init_db()
