"""
database.py - SQLite Database Management Layer for Academic Student Portal
Implements Zero Hardcoding Policy for profiles, attendance, and marks.
Handles schema initialization, seeding, dynamic querying, and transactional updates.
"""

import sqlite3
import datetime
import base64
from pathlib import Path
from typing import List, Dict, Any, Optional

import biometrics

DB_FILE = Path(__file__).parent / "portal.db"
PHOTO_DIR = Path(__file__).parent / "registered_faces"
PHOTO_DIR.mkdir(exist_ok=True)


def get_db_connection() -> sqlite3.Connection:
    """Creates a database connection with dictionary-like row access."""
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(force_reseed: bool = False) -> None:
    """
    Initializes the SQLite database tables and seeds them if empty
    or if force_reseed is True.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    if force_reseed:
        cursor.execute("DROP TABLE IF EXISTS task_progress")
        cursor.execute("DROP TABLE IF EXISTS attendance_logs")
        cursor.execute("DROP TABLE IF EXISTS marks")
        cursor.execute("DROP TABLE IF EXISTS attendance")
        cursor.execute("DROP TABLE IF EXISTS students")

    # 1. Students Table with biometric reference photo storage
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            cgpa REAL NOT NULL,
            credits_earned INTEGER NOT NULL,
            proctor_message TEXT,
            spotlight_news TEXT,
            photo_data TEXT
        )
        """
    )

    # 2. Attendance Table (Strictly NO Slot column)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            course_code TEXT NOT NULL,
            course_title TEXT NOT NULL,
            course_type TEXT NOT NULL,
            faculty_name TEXT NOT NULL,
            attended_classes INTEGER NOT NULL,
            total_classes INTEGER NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
        """
    )

    # 3. Marks Table (Scaled to 100 marks total: mid_1 /30, mid_2 /30, assignment /40)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            semester TEXT NOT NULL,
            course_code TEXT NOT NULL,
            course_title TEXT NOT NULL,
            credits INTEGER NOT NULL,
            mid_1 REAL,
            mid_2 REAL,
            assignment REAL,
            total REAL,
            grade TEXT,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
        """
    )

    # 4. Attendance Logs Table (Day-wise drill-down & Face-Match verification logs)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS attendance_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            course_code TEXT NOT NULL,
            date TEXT NOT NULL,
            time_slot TEXT NOT NULL,
            status TEXT NOT NULL,
            verification_method TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
        """
    )

    # 5. Roadmap Task Progress Table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS task_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            course_code TEXT NOT NULL,
            task_id TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0,
            quiz_score REAL,
            last_updated TEXT NOT NULL,
            UNIQUE(student_id, course_code, task_id)
        )
        """
    )

    conn.commit()

    # Check if database is already seeded
    cursor.execute("SELECT COUNT(*) as count FROM students")
    count = cursor.fetchone()["count"]
    if count == 0:
        seed_database(conn)

    conn.close()


def seed_database(conn: sqlite3.Connection) -> None:
    """
    Seeds the database with the primary profile: Yuvasri Eswara.
    Additional students (e.g. A Jenita Roselin) can be added via the 'Add Student' UI.
    """
    cursor = conn.cursor()

    # Check if permanent reference photo exists on disk, otherwise generate initial
    yuvasri_saved_photo = PHOTO_DIR / "21BCE1001.jpg"
    if yuvasri_saved_photo.exists():
        yuvasri_avatar_bytes = yuvasri_saved_photo.read_bytes()
    else:
        yuvasri_avatar_bytes = biometrics.generate_default_avatar("Yuvasri Eswara")
        yuvasri_saved_photo.write_bytes(yuvasri_avatar_bytes)
    yuvasri_photo_b64 = base64.b64encode(yuvasri_avatar_bytes).decode("utf-8")

    # 1. Seed Student: Yuvasri Eswara
    students_data = [
        (
            "21BCE1001",
            "Yuvasri Eswara",
            9.42,
            94,
            "Yuvasri is maintaining exceptional academic standing across all computer science subjects. Nominated for Undergraduate Research Fellowship in Distributed Systems.",
            "🏆 Academic Excellence Award: Yuvasri Eswara achieved 1st Rank in Advanced Distributed Systems! | IEEE Conference paper submission deadline is April 12th.",
            yuvasri_photo_b64
        )
    ]
    cursor.executemany(
        """
        INSERT INTO students (student_id, name, cgpa, credits_earned, proctor_message, spotlight_news, photo_data)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        students_data
    )

    # 2. Seed Attendance for Yuvasri (High compliance across all courses)
    attendance_data = [
        ("21BCE1001", "CSE3001", "Software Engineering", "Theory", "Dr. K. Ramesh", 38, 40),
        ("21BCE1001", "CSE3002", "Database Management Systems", "Theory", "Prof. M. Anitha", 37, 40),
        ("21BCE1001", "CSE3003", "Computer Networks", "Lab", "Dr. S. Vijay", 28, 30),
        ("21BCE1001", "CSE3004", "Cloud Computing Architecture", "Theory", "Dr. P. Suresh", 40, 42),
        ("21BCE1001", "CSE3005", "Web Technologies", "Lab", "Prof. N. Deepa", 29, 30),
    ]
    cursor.executemany(
        """
        INSERT INTO attendance (student_id, course_code, course_title, course_type, faculty_name, attended_classes, total_classes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        attendance_data
    )

    # 3. Seed Marks for Yuvasri (Scaled to 100 marks: Mid-1 (30), Mid-2 (30), Assignment (40))
    marks_data = [
        # Current Semester (Winter 2025-26): Both Mid-1 and Mid-2 completed with distinction
        ("21BCE1001", "Winter Semester 2025-26", "CSE3001", "Software Engineering", 4, 28.5, 29.0, 38.0, 95.5, "S"),
        ("21BCE1001", "Winter Semester 2025-26", "CSE3002", "Database Management Systems", 4, 27.0, 28.0, 37.5, 92.5, "S"),
        ("21BCE1001", "Winter Semester 2025-26", "CSE3003", "Computer Networks", 3, 28.0, 27.5, 38.5, 94.0, "S"),
        ("21BCE1001", "Winter Semester 2025-26", "CSE3004", "Cloud Computing Architecture", 4, 26.5, 28.0, 36.5, 91.0, "A"),
        ("21BCE1001", "Winter Semester 2025-26", "CSE3005", "Web Technologies", 3, 29.5, 29.0, 39.5, 98.0, "S"),

        # Past Semester (Fall 2025)
        ("21BCE1001", "Fall Semester 2025", "CSE2001", "Data Structures and Algorithms", 4, 28.5, 29.5, 39.0, 97.0, "S"),
        ("21BCE1001", "Fall Semester 2025", "CSE2002", "Operating Systems", 4, 27.0, 28.0, 37.0, 92.0, "S"),
        ("21BCE1001", "Fall Semester 2025", "CSE2003", "Theory of Computation", 3, 26.0, 27.0, 36.0, 89.0, "A"),
    ]
    cursor.executemany(
        """
        INSERT INTO marks (student_id, semester, course_code, course_title, credits, mid_1, mid_2, assignment, total, grade)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        marks_data
    )

    # 4. Seed Attendance Logs
    sample_dates = [
        ("2026-03-02", "09:00 - 09:50"),
        ("2026-03-03", "10:00 - 10:50"),
        ("2026-03-04", "11:00 - 11:50"),
        ("2026-03-05", "14:00 - 15:40"),
        ("2026-03-06", "08:00 - 08:50"),
        ("2026-03-09", "09:00 - 09:50")
    ]
    log_records = []
    for dt, slot in sample_dates:
        log_records.append((
            "21BCE1001", "CSE3001", dt, slot, "Present", "IoT Edge Camera Node (Biometric Match: 99.4%)", f"{dt} 08:59:45"
        ))

    cursor.executemany(
        """
        INSERT INTO attendance_logs (student_id, course_code, date, time_slot, status, verification_method, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        log_records
    )

    conn.commit()


# -------------------------------------------------------------
# Query & Transaction API
# -------------------------------------------------------------

def get_student_profiles() -> List[Dict[str, Any]]:
    """Returns a list of all student profiles for the switcher."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT student_id, name, cgpa, credits_earned, photo_data FROM students ORDER BY student_id ASC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_student_by_id(student_id: str) -> Optional[Dict[str, Any]]:
    """Fetches full profile details for a given student ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_student_photo_bytes(student_id: str) -> bytes:
    """Returns the decoded reference photo bytes for a student, loading permanently from disk or SQLite."""
    photo_file = PHOTO_DIR / f"{student_id}.jpg"
    if photo_file.exists():
        return photo_file.read_bytes()

    student = get_student_by_id(student_id)
    if student and student.get("photo_data"):
        try:
            raw = base64.b64decode(student["photo_data"])
            photo_file.write_bytes(raw)
            return raw
        except Exception:
            pass
    name = student["name"] if student else "Student"
    default_bytes = biometrics.generate_default_avatar(name)
    photo_file.write_bytes(default_bytes)
    return default_bytes


def update_student_photo(student_id: str, photo_bytes: bytes) -> bool:
    """Updates or enrolls an official biometric reference photo for a student permanently."""
    # 1. Save permanently to disk
    photo_file = PHOTO_DIR / f"{student_id}.jpg"
    photo_file.write_bytes(photo_bytes)

    # 2. Update SQLite
    photo_b64 = base64.b64encode(photo_bytes).decode("utf-8")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE students SET photo_data = ? WHERE student_id = ?",
        (photo_b64, student_id)
    )
    conn.commit()
    conn.close()
    return True


def create_student(
    student_id: str,
    name: str,
    cgpa: float,
    credits_earned: int,
    proctor_message: Optional[str] = None,
    spotlight_news: Optional[str] = None,
    photo_bytes: Optional[bytes] = None
) -> Dict[str, Any]:
    """
    Registers a new student profile and enrolls their reference photo.
    Permanently saves photo to disk and database.
    Automatically enrolls the student into active semester courses with 0 attended classes
    and marks initialized to None (triggers AI Cold-Start Onboarding state).
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    if photo_bytes is None:
        photo_bytes = biometrics.generate_default_avatar(name)

    # Save permanently to disk
    photo_file = PHOTO_DIR / f"{student_id}.jpg"
    photo_file.write_bytes(photo_bytes)

    photo_b64 = base64.b64encode(photo_bytes).decode("utf-8")

    default_proctor = proctor_message or f"Welcome {name}! Maintain regular attendance above 75% to stay eligible for final examinations."
    default_news = spotlight_news or "📢 Academic Notice: Course registration and internal continuous assessment schedules are live."

    cursor.execute(
        """
        INSERT INTO students (student_id, name, cgpa, credits_earned, proctor_message, spotlight_news, photo_data)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (student_id, name, cgpa, credits_earned, default_proctor, default_news, photo_b64)
    )

    # Standard semester course catalog template
    core_courses = [
        ("CSE3001", "Software Engineering", "Theory", "Dr. K. Ramesh", 4, 40),
        ("CSE3002", "Database Management Systems", "Theory", "Prof. M. Anitha", 4, 40),
        ("CSE3003", "Computer Networks", "Lab", "Dr. S. Vijay", 3, 30),
        ("CSE3004", "Cloud Computing Architecture", "Theory", "Dr. P. Suresh", 4, 42),
        ("CSE3005", "Web Technologies", "Lab", "Prof. N. Deepa", 3, 30)
    ]

    for c_code, c_title, c_type, faculty, credits, total_classes in core_courses:
        cursor.execute(
            """
            INSERT INTO attendance (student_id, course_code, course_title, course_type, faculty_name, attended_classes, total_classes)
            VALUES (?, ?, ?, ?, ?, 0, ?)
            """,
            (student_id, c_code, c_title, c_type, faculty, total_classes)
        )

        cursor.execute(
            """
            INSERT INTO marks (student_id, semester, course_code, course_title, credits, mid_1, mid_2, assignment, total, grade)
            VALUES (?, 'Winter Semester 2025-26', ?, ?, ?, NULL, NULL, NULL, NULL, 'In Progress')
            """,
            (student_id, c_code, c_title, credits)
        )

    conn.commit()
    conn.close()

    return {
        "student_id": student_id,
        "name": name,
        "cgpa": cgpa,
        "credits_earned": credits_earned,
        "courses_enrolled": len(core_courses)
    }


def get_student_attendance(student_id: str) -> List[Dict[str, Any]]:
    """
    Fetches attendance records for a student and calculates percentage and remarks.
    Adheres strictly to institutional standards.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, course_code, course_title, course_type, faculty_name,
               attended_classes, total_classes
        FROM attendance
        WHERE student_id = ?
        ORDER BY course_code ASC
        """,
        (student_id,)
    )
    records = []
    for row in cursor.fetchall():
        item = dict(row)
        attended = item["attended_classes"]
        total = item["total_classes"]
        pct = round((attended / total * 100), 2) if total > 0 else 0.0
        item["percentage"] = pct

        if pct < 75.0:
            # Classes needed to reach 75%
            needed = max(0, int((0.75 * total - attended + 0.24) / 0.25))
            item["status_remark"] = f"⚠️ Low Attendance ({pct}%) - Debar Risk! Need {needed} consecutive class(es)"
            item["is_alert"] = True
            item["safe_skips"] = 0
            item["classes_needed"] = needed
        else:
            # Safe skips: (attended) / (total + y) >= 0.75 => y <= (attended - 0.75*total) / 0.75
            skips = max(0, int((attended - 0.75 * total) / 0.75))
            item["status_remark"] = f"✅ Regular ({pct}%) - Safe to miss {skips} class(es)"
            item["is_alert"] = False
            item["safe_skips"] = skips
            item["classes_needed"] = 0

        records.append(item)
    conn.close()
    return records


def get_attendance_logs(student_id: str, course_code: str) -> List[Dict[str, Any]]:
    """Fetches day-wise drill-down attendance logs for a student and course."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT date, time_slot, status, verification_method, timestamp
        FROM attendance_logs
        WHERE student_id = ? AND course_code = ?
        ORDER BY date DESC, timestamp DESC
        LIMIT 20
        """,
        (student_id, course_code)
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def record_face_match_attendance(
    student_id: str,
    course_code: str,
    device_name: str = "IoT Edge Biometric Node",
    confidence_pct: float = 99.4
) -> Dict[str, Any]:
    """
    Records confirmed biometric attendance:
    Increments attended_classes and total_classes in SQLite and logs the verification.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Update attendance table
    cursor.execute(
        """
        UPDATE attendance
        SET attended_classes = attended_classes + 1,
            total_classes = total_classes + 1
        WHERE student_id = ? AND course_code = ?
        """,
        (student_id, course_code)
    )

    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    time_slot = f"{now.strftime('%H:00')} - {now.strftime('%H:50')}"
    method_str = f"{device_name} (Confidence: {confidence_pct:.1f}%)"

    # Insert log entry
    cursor.execute(
        """
        INSERT INTO attendance_logs (student_id, course_code, date, time_slot, status, verification_method, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            student_id,
            course_code,
            date_str,
            time_slot,
            "Present",
            method_str,
            f"{date_str} {time_str}"
        )
    )

    conn.commit()

    # Fetch updated record
    cursor.execute(
        "SELECT attended_classes, total_classes FROM attendance WHERE student_id = ? AND course_code = ?",
        (student_id, course_code)
    )
    updated = cursor.fetchone()
    conn.close()

    return {
        "student_id": student_id,
        "course_code": course_code,
        "attended": updated["attended_classes"] if updated else 0,
        "total": updated["total_classes"] if updated else 0,
        "timestamp": f"{date_str} {time_str}",
        "confidence_pct": confidence_pct
    }


def get_available_semesters(student_id: str) -> List[str]:
    """Returns list of distinct semesters available for the student."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT DISTINCT semester FROM marks WHERE student_id = ? ORDER BY semester DESC",
        (student_id,)
    )
    semesters = [row["semester"] for row in cursor.fetchall()]
    conn.close()
    if not semesters:
        semesters = ["Winter Semester 2025-26"]
    return semesters


def get_student_marks(student_id: str, semester: str) -> List[Dict[str, Any]]:
    """
    Fetches student internal marks for a semester.
    All scores are strictly scaled to 100 marks total (mid_1: 30, mid_2: 30, assignment: 40).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, course_code, course_title, credits, mid_1, mid_2, assignment, total, grade
        FROM marks
        WHERE student_id = ? AND semester = ?
        ORDER BY course_code ASC
        """,
        (student_id, semester)
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_historical_marks_for_student(student_id: str) -> List[Dict[str, Any]]:
    """Returns all marks across all semesters for trend analysis."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT semester, course_code, course_title, mid_1, mid_2, assignment, total, grade
        FROM marks
        WHERE student_id = ?
        ORDER BY semester ASC, course_code ASC
        """,
        (student_id,)
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_task_progress(student_id: str, course_code: str) -> Dict[str, Dict[str, Any]]:
    """Returns dict of task_id -> progress record for the student and course."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT task_id, completed, quiz_score, last_updated
        FROM task_progress
        WHERE student_id = ? AND course_code = ?
        """,
        (student_id, course_code)
    )
    progress = {row["task_id"]: dict(row) for row in cursor.fetchall()}
    conn.close()
    return progress


def update_task_progress(
    student_id: str,
    course_code: str,
    task_id: str,
    completed: bool,
    quiz_score: Optional[float] = None
) -> None:
    """Updates or inserts task completion status and quiz score."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        INSERT INTO task_progress (student_id, course_code, task_id, completed, quiz_score, last_updated)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(student_id, course_code, task_id) DO UPDATE SET
            completed = excluded.completed,
            quiz_score = COALESCE(excluded.quiz_score, task_progress.quiz_score),
            last_updated = excluded.last_updated
        """,
        (student_id, course_code, task_id, 1 if completed else 0, quiz_score, now_str)
    )
    conn.commit()
    conn.close()
