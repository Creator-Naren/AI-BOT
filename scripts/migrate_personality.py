import sqlite3
from pathlib import Path

db_path = Path(__file__).resolve().parent.parent / "instance" / "chatbot.db"
if not db_path.exists():
    print("No database found at instance/chatbot.db; nothing to migrate.")
    raise SystemExit(1)

conn = sqlite3.connect(db_path)
tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
if "user_preference" not in tables:
    print("user_preference table not found; nothing to migrate")
    conn.close()
    raise SystemExit(0)

columns = [row[1] for row in conn.execute("PRAGMA table_info(user_preference)")]
if "personality" not in columns:
    conn.execute("ALTER TABLE user_preference ADD COLUMN personality TEXT DEFAULT ''")
    conn.commit()
    print("Migrated: added personality column to user_preference")
else:
    print("Column already present; nothing to do")
conn.close()
