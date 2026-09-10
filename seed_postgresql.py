"""
seed_postgresql.py - Data Seed and Migration Script for PostgreSQL / Amazon RDS
Exports canonical academic state from SQLite or seeds a fresh PostgreSQL database.
Can be executed against local PostgreSQL (via docker-compose) or AWS RDS for PostgreSQL.
"""

import os
import sys
import sqlite3
from typing import Optional

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False


def get_pg_connection(database_url: str):
    """Establishes connection to PostgreSQL database."""
    if not HAS_PSYCOPG2:
        raise ImportError("psycopg2 package is required for PostgreSQL operation. Install via pip install psycopg2-binary.")
    return psycopg2.connect(database_url)


def migrate_sqlite_to_postgresql(sqlite_db_path: str, pg_url: str) -> None:
    """Migrates existing SQLite database state directly into PostgreSQL."""
    if not os.path.exists(sqlite_db_path):
        print(f"[ERROR] SQLite database file not found at: {sqlite_db_path}")
        sys.exit(1)

    print(f"[INFO] Connecting to SQLite: {sqlite_db_path}")
    sqlite_conn = sqlite3.connect(sqlite_db_path)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()

    print(f"[INFO] Connecting to PostgreSQL...")
    pg_conn = get_pg_connection(pg_url)
    pg_cursor = pg_conn.cursor()

    # Read and apply schema_postgresql.sql
    schema_path = os.path.join(os.path.dirname(__file__), "schema_postgresql.sql")
    if os.path.exists(schema_path):
        print(f"[INFO] Executing PostgreSQL DDL schema: {schema_path}")
        with open(schema_path, "r", encoding="utf-8") as f:
            pg_cursor.execute(f.read())
        pg_conn.commit()

    # Table migration order (honoring foreign keys)
    tables = [
        ("academic_timeline", ["term_name", "start_date", "end_date", "reference_date", "total_weeks"]),
        ("course_offerings", ["course_code", "course_title", "course_type", "faculty_name", "weekly_sessions", "classes_conducted", "credits"]),
        ("students", ["student_id", "name", "proctor_message", "spotlight_news", "photo_data"]),
        ("student_enrollments", ["student_id", "course_code", "enrollment_date", "effective_start_date", "classes_applicable", "classes_attended"]),
        ("transcript_history", ["student_id", "semester", "gpa", "credits"]),
        ("assessment_instances", ["student_id", "course_code", "name", "type", "max_marks", "achieved_marks", "date"]),
        ("attendance_logs", ["student_id", "course_code", "date", "time_slot", "status", "verification_method", "timestamp"]),
        ("task_progress", ["student_id", "course_code", "task_id", "completed", "quiz_score", "last_updated"])
    ]

    for table_name, columns in tables:
        sqlite_cursor.execute(f"SELECT {', '.join(columns)} FROM {table_name}")
        rows = sqlite_cursor.fetchall()
        if not rows:
            print(f"[INFO] No records in SQLite for table: {table_name}")
            continue

        placeholders = ", ".join(["%s"] * len(columns))
        col_names = ", ".join(columns)
        insert_sql = f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})"

        values_list = [[r[c] for c in columns] for r in rows]
        pg_cursor.executemany(insert_sql, values_list)
        print(f"[SUCCESS] Migrated {len(values_list)} records into PostgreSQL table: {table_name}")

    pg_conn.commit()
    sqlite_conn.close()
    pg_conn.close()
    print("[SUCCESS] SQLite to PostgreSQL migration completed successfully.")


if __name__ == "__main__":
    db_url = os.getenv("RDS_DATABASE_URL") or os.getenv("DATABASE_URL")
    sqlite_path = os.getenv("SQLITE_PATH", os.path.join(os.path.dirname(__file__), "portal.db"))

    if not db_url:
        print("[NOTICE] RDS_DATABASE_URL environment variable is not set.")
        print("Example usage: RDS_DATABASE_URL='postgresql://postgres:postgres@localhost:5432/portal_db' python seed_postgresql.py")
        sys.exit(0)

    migrate_sqlite_to_postgresql(sqlite_path, db_url)
