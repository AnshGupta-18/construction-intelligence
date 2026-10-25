
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "construction.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():
    with get_connection() as conn:
        # Construction project tasks
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                duration INTEGER NOT NULL,
                priority TEXT NOT NULL,
                start_date TEXT NOT NULL,
                status TEXT DEFAULT 'Not Started',
                predecessor TEXT
            )
        """)

        # Construction cost items
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cost_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                material_cost REAL DEFAULT 0,
                labour_cost REAL DEFAULT 0,
                equipment_cost REAL DEFAULT 0,
                contingency REAL DEFAULT 0,
                total_cost REAL DEFAULT 0
            )
        """)

        # Add predecessor column to existing databases
        columns = [
            row[1]
            for row in conn.execute("PRAGMA table_info(tasks)")
        ]

        if "predecessor" not in columns:
            conn.execute(
                "ALTER TABLE tasks ADD COLUMN predecessor TEXT"
            )


if __name__ == "__main__":
    initialize_database()
    print(f"Database initialized successfully: {DB_PATH}")
