"""
database.py - SQLite Database Management Layer for Academic Student Portal
Implements Zero Hardcoding Policy for profiles, attendance, and marks.
Handles canonical Academic World Specification, schema initialization, seeding,
dynamic querying, and transactional updates.
"""

import sqlite3
import datetime
import base64
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

import biometrics

DB_FILE = Path(__file__).parent / "portal.db"
PHOTO_DIR = Path(__file__).parent / "registered_faces"
PHOTO_DIR.mkdir(exist_ok=True)


def get_db_connection() -> sqlite3.Connection:
    """Creates a database connection with dictionary-like row access."""
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row
    return conn


def calculate_academic_week(start_date_str: str, ref_date_str: str) -> int:
    """Derives current academic week number from start date and reference date."""
    d_start = datetime.date.fromisoformat(start_date_str)
    d_ref = datetime.date.fromisoformat(ref_date_str)
    days = (d_ref - d_start).days
    return (days // 7) + 1 if days >= 0 else 1


def calculate_classes_needed(attended: int, applicable: int, target_pct: float = 75.0) -> int:
    """
    Calculates consecutive classes a student must attend to reach target_pct (75%).
    Formula: ceil((0.75 * applicable - attended) / 0.25)
    """
    if applicable == 0:
        return 0
    current_pct = (attended / applicable) * 100.0
    if current_pct >= target_pct:
        return 0
    import math
    needed = math.ceil((0.75 * applicable - attended) / 0.25)
    return max(0, needed)


def calculate_safe_skips(attended: int, applicable: int, target_pct: float = 75.0) -> int:
    """
    Calculates safe leaves remaining while maintaining >= target_pct (75%).
    Formula: floor((attended - 0.75 * applicable) / 0.75)
    """
    if applicable == 0:
        return 0
    current_pct = (attended / applicable) * 100.0
    if current_pct < target_pct:
        return 0
    import math
    skips = math.floor((attended - 0.75 * applicable) / 0.75)
    return max(0, skips)


def calculate_transcript_cgpa(transcript_records: List[Tuple[float, int]]) -> float:
    """Computes dynamic credit-weighted CGPA across past semester GPAs."""
    if not transcript_records:
        return 0.0
    total_weighted_points = sum(gpa * credits for gpa, credits in transcript_records)
    total_credits = sum(credits for _, credits in transcript_records)
    if total_credits == 0:
        return 0.0
    return round(total_weighted_points / total_credits, 2)


def calculate_overall_attendance(enrollment_records: List[Tuple[int, int]]) -> float:
    """Computes class-count weighted total overall attendance percentage."""
    tot_attended = sum(att for att, _ in enrollment_records)
    tot_applicable = sum(app for _, app in enrollment_records)
    if tot_applicable == 0:
        return 0.0
    return round((tot_attended / tot_applicable) * 100.0, 1)


def init_db(force_reseed: bool = False) -> None:
    """Initializes the SQLite database tables and seeds them if empty or forced."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if force_reseed:
        cursor.execute("DROP TABLE IF EXISTS task_progress")
        cursor.execute("DROP TABLE IF EXISTS attendance_logs")
        cursor.execute("DROP TABLE IF EXISTS assessment_instances")
        cursor.execute("DROP TABLE IF EXISTS transcript_history")
        cursor.execute("DROP TABLE IF EXISTS student_enrollments")
        cursor.execute("DROP TABLE IF EXISTS course_offerings")
        cursor.execute("DROP TABLE IF EXISTS academic_timeline")
        cursor.execute("DROP TABLE IF EXISTS students")

    # 1. Academic Timeline Table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS academic_timeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term_name TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            reference_date TEXT NOT NULL,
            total_weeks INTEGER NOT NULL
        )
        """
    )

    # 2. Course Offerings Table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS course_offerings (
            course_code TEXT PRIMARY KEY,
            course_title TEXT NOT NULL,
            course_type TEXT NOT NULL,
            faculty_name TEXT NOT NULL,
            weekly_sessions INTEGER NOT NULL,
            classes_conducted INTEGER NOT NULL,
            credits INTEGER NOT NULL
        )
        """
    )

    # 3. Students Table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            proctor_message TEXT,
            spotlight_news TEXT,
            photo_data TEXT
        )
        """
    )

    # 4. Student Enrollments Table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS student_enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            course_code TEXT NOT NULL,
            enrollment_date TEXT NOT NULL,
            effective_start_date TEXT NOT NULL,
            classes_applicable INTEGER NOT NULL,
            classes_attended INTEGER NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            FOREIGN KEY (course_code) REFERENCES course_offerings(course_code),
            UNIQUE(student_id, course_code)
        )
        """
    )

    # 5. Transcript History Table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS transcript_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            semester TEXT NOT NULL,
            gpa REAL NOT NULL,
            credits INTEGER NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
        """
    )

    # 6. Assessment Instances Table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS assessment_instances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            course_code TEXT NOT NULL,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            max_marks REAL NOT NULL,
            achieved_marks REAL,
            date TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
        """
    )

    # 7. Attendance Logs Table
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

    # 8. Task Progress Table
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
    """Seeds database according to the Canonical Academic World Specification."""
    cursor = conn.cursor()

    # 1. Academic Timeline (Semester 5, Fall 2026)
    cursor.execute(
        """
        INSERT INTO academic_timeline (term_name, start_date, end_date, reference_date, total_weeks)
        VALUES ('Semester 5 (Fall 2026 Academic Session)', '2026-07-20', '2026-10-23', '2026-09-10', 14)
        """
    )

    # 2. Course Offerings & Conducted Classes (Week 8)
    courses = [
        ("CSE3002", "Database Management Systems", "Theory", "Prof. M. Anitha", 3, 21, 4),
        ("CSE3003", "Computer Networks", "Lab", "Dr. S. Vijay", 3, 20, 3),
        ("CSE3006", "VLSI System Design", "Theory", "Dr. R. Kulkarni", 3, 18, 4),
        ("CSE3007", "Artificial Intelligence & Machine Learning", "Theory", "Dr. A. Sharma", 3, 22, 4),
        ("CSE3004", "Cloud Computing Architecture", "Theory", "Dr. P. Suresh", 3, 19, 4),
    ]
    cursor.executemany(
        """
        INSERT INTO course_offerings (course_code, course_title, course_type, faculty_name, weekly_sessions, classes_conducted, credits)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        courses
    )

    # 3. Seed Students
    # Student 1: Yuvasri Eswara (Established 3rd-Year Student)
    yuvasri_saved_photo = PHOTO_DIR / "21BCE1001.jpg"
    if yuvasri_saved_photo.exists():
        yuvasri_avatar_bytes = yuvasri_saved_photo.read_bytes()
    else:
        yuvasri_avatar_bytes = biometrics.generate_default_avatar("Yuvasri Eswara")
        yuvasri_saved_photo.write_bytes(yuvasri_avatar_bytes)
    yuvasri_photo_b64 = base64.b64encode(yuvasri_avatar_bytes).decode("utf-8")

    # Student 2: Jenita Roselin (Newly Enrolled Onboarding Persona)
    jenita_saved_photo = PHOTO_DIR / "24BLC1033.jpg"
    if jenita_saved_photo.exists():
        jenita_avatar_bytes = jenita_saved_photo.read_bytes()
    else:
        jenita_avatar_bytes = biometrics.generate_default_avatar("A Jenita Roselin")
        jenita_saved_photo.write_bytes(jenita_avatar_bytes)
    jenita_photo_b64 = base64.b64encode(jenita_avatar_bytes).decode("utf-8")

    students_data = [
        (
            "21BCE1001",
            "Yuvasri Eswara",
            "Yuvasri is maintaining exceptional academic standing across all computer science subjects. Nominated for Undergraduate Research Fellowship in Distributed Systems.",
            "Academic Excellence Award: Yuvasri Eswara achieved 1st Rank in Advanced Distributed Systems! | IEEE Conference paper submission deadline is April 12th.",
            yuvasri_photo_b64
        ),
        (
            "24BLC1033",
            "A Jenita Roselin",
            "Welcome to the academic semester! Maintain continuous attendance above 75% for exam clearance.",
            "Student Orientation Completed: Official registration confirmed on Sept 8, 2026.",
            jenita_photo_b64
        )
    ]
    cursor.executemany(
        """
        INSERT INTO students (student_id, name, proctor_message, spotlight_news, photo_data)
        VALUES (?, ?, ?, ?, ?)
        """,
        students_data
    )

    # 4. Student Enrollments
    # Yuvasri: Enrolled July 20, 2026 (Applicable = Conducted)
    yuvasri_enrollments = [
        ("21BCE1001", "CSE3002", "2026-07-20", "2026-07-20", 21, 18),  # 85.7%
        ("21BCE1001", "CSE3003", "2026-07-20", "2026-07-20", 20, 16),  # 80.0%
        ("21BCE1001", "CSE3006", "2026-07-20", "2026-07-20", 18, 12),  # 66.7% (Shortage)
        ("21BCE1001", "CSE3007", "2026-07-20", "2026-07-20", 22, 20),  # 90.9%
        ("21BCE1001", "CSE3004", "2026-07-20", "2026-07-20", 19, 14),  # 73.7% (Shortage)
    ]
    # Jenita: Enrolled Sept 8, 2026 (Effective Sept 11, 2026 -> Applicable = 0)
    jenita_enrollments = [
        ("24BLC1033", "CSE3002", "2026-09-08", "2026-09-11", 0, 0),
        ("24BLC1033", "CSE3003", "2026-09-08", "2026-09-11", 0, 0),
        ("24BLC1033", "CSE3006", "2026-09-08", "2026-09-11", 0, 0),
        ("24BLC1033", "CSE3007", "2026-09-08", "2026-09-11", 0, 0),
        ("24BLC1033", "CSE3004", "2026-09-08", "2026-09-11", 0, 0),
    ]
    cursor.executemany(
        """
        INSERT INTO student_enrollments (student_id, course_code, enrollment_date, effective_start_date, classes_applicable, classes_attended)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        yuvasri_enrollments + jenita_enrollments
    )

    # 5. Transcript History (Yuvasri Sem 1-4)
    transcript_data = [
        ("21BCE1001", "Fall Semester 2024 (Sem 1)", 8.72, 22),
        ("21BCE1001", "Winter Semester 2024-25 (Sem 2)", 9.01, 23),
        ("21BCE1001", "Fall Semester 2025 (Sem 3)", 8.65, 23),
        ("21BCE1001", "Winter Semester 2025-26 (Sem 4)", 8.12, 22),
    ]
    cursor.executemany(
        """
        INSERT INTO transcript_history (student_id, semester, gpa, credits)
        VALUES (?, ?, ?, ?)
        """,
        transcript_data
    )

    # 6. Assessment Instances
    yuvasri_marks = [
        ("21BCE1001", "CSE3002", "CAT-1 (Internal Assessment 1)", "CAT-1", 50.0, 43.0, "2026-08-28"),
        ("21BCE1001", "CSE3002", "Assignment 1 - ER & SQL Modeling", "Assignment", 10.0, 9.0, "2026-09-02"),
        ("21BCE1001", "CSE3002", "CAT-2 (Internal Assessment 2)", "CAT-2", 50.0, None, "2026-10-05"),
        ("21BCE1001", "CSE3002", "FAT (Final Assessment Test)", "FAT", 100.0, None, "2026-10-20"),

        ("21BCE1001", "CSE3003", "CAT-1 (Internal Assessment 1)", "CAT-1", 50.0, 40.0, "2026-08-28"),
        ("21BCE1001", "CSE3003", "Assignment 1 - CRC & Packet Tracing", "Assignment", 10.0, 8.5, "2026-09-02"),
        ("21BCE1001", "CSE3003", "CAT-2 (Internal Assessment 2)", "CAT-2", 50.0, None, "2026-10-05"),
        ("21BCE1001", "CSE3003", "FAT (Final Assessment Test)", "FAT", 100.0, None, "2026-10-20"),

        ("21BCE1001", "CSE3006", "CAT-1 (Internal Assessment 1)", "CAT-1", 50.0, 33.5, "2026-08-28"),
        ("21BCE1001", "CSE3006", "Assignment 1 - CMOS Logic Synthesis", "Assignment", 10.0, 7.0, "2026-09-02"),
        ("21BCE1001", "CSE3006", "CAT-2 (Internal Assessment 2)", "CAT-2", 50.0, None, "2026-10-05"),
        ("21BCE1001", "CSE3006", "FAT (Final Assessment Test)", "FAT", 100.0, None, "2026-10-20"),

        ("21BCE1001", "CSE3007", "CAT-1 (Internal Assessment 1)", "CAT-1", 50.0, 45.5, "2026-08-28"),
        ("21BCE1001", "CSE3007", "Assignment 1 - Search & Neural Nets", "Assignment", 10.0, 9.5, "2026-09-02"),
        ("21BCE1001", "CSE3007", "CAT-2 (Internal Assessment 2)", "CAT-2", 50.0, None, "2026-10-05"),
        ("21BCE1001", "CSE3007", "FAT (Final Assessment Test)", "FAT", 100.0, None, "2026-10-20"),

        ("21BCE1001", "CSE3004", "CAT-1 (Internal Assessment 1)", "CAT-1", 50.0, 37.0, "2026-08-28"),
        ("21BCE1001", "CSE3004", "Assignment 1 - AWS IAM & S3 Design", "Assignment", 10.0, 8.0, "2026-09-02"),
        ("21BCE1001", "CSE3004", "CAT-2 (Internal Assessment 2)", "CAT-2", 50.0, None, "2026-10-05"),
        ("21BCE1001", "CSE3004", "FAT (Final Assessment Test)", "FAT", 100.0, None, "2026-10-20"),
    ]

    jenita_marks = [
        ("24BLC1033", "CSE3002", "CAT-1 (Internal Assessment 1)", "CAT-1", 50.0, None, "2026-08-28"),
        ("24BLC1033", "CSE3002", "CAT-2 (Internal Assessment 2)", "CAT-2", 50.0, None, "2026-10-05"),
        ("24BLC1033", "CSE3002", "FAT (Final Assessment Test)", "FAT", 100.0, None, "2026-10-20"),
        ("24BLC1033", "CSE3003", "CAT-1 (Internal Assessment 1)", "CAT-1", 50.0, None, "2026-08-28"),
        ("24BLC1033", "CSE3006", "CAT-1 (Internal Assessment 1)", "CAT-1", 50.0, None, "2026-08-28"),
        ("24BLC1033", "CSE3007", "CAT-1 (Internal Assessment 1)", "CAT-1", 50.0, None, "2026-08-28"),
        ("24BLC1033", "CSE3004", "CAT-1 (Internal Assessment 1)", "CAT-1", 50.0, None, "2026-08-28"),
    ]

    cursor.executemany(
        """
        INSERT INTO assessment_instances (student_id, course_code, name, type, max_marks, achieved_marks, date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        yuvasri_marks + jenita_marks
    )

    # 7. Seed Attendance Logs
    sample_dates = [
        ("2026-09-02", "09:00 - 09:50"),
        ("2026-09-03", "10:00 - 10:50"),
        ("2026-09-04", "11:00 - 11:50"),
        ("2026-09-07", "14:00 - 15:40"),
        ("2026-09-09", "09:00 - 09:50")
    ]
    log_records = []
    for dt, slot in sample_dates:
        log_records.append((
            "21BCE1001", "CSE3002", dt, slot, "Present", "IoT Edge Camera Node (Biometric Match: 99.4%)", f"{dt} 08:59:45"
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
# Query & Data Access API
# -------------------------------------------------------------

def get_academic_timeline() -> Dict[str, Any]:
    """Fetches the canonical academic timeline state."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM academic_timeline LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        res = dict(row)
        res["current_week"] = calculate_academic_week(res["start_date"], res["reference_date"])
        return res
    return {
        "term_name": "Semester 5 (Fall 2026 Academic Session)",
        "start_date": "2026-07-20",
        "end_date": "2026-10-23",
        "reference_date": "2026-09-10",
        "total_weeks": 14,
        "current_week": 8
    }


def get_student_profiles() -> List[Dict[str, Any]]:
    """Returns list of student profiles for the sidebar profile switcher."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT student_id, name, photo_data FROM students ORDER BY student_id ASC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_student_by_id(student_id: str) -> Optional[Dict[str, Any]]:
    """Fetches full profile details for a student."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    res = dict(row)

    # Compute dynamic CGPA from transcript history
    transcript = get_student_transcript(student_id)
    if transcript:
        cgpa_val = calculate_transcript_cgpa([(t["gpa"], t["credits"]) for t in transcript])
        res["cgpa"] = cgpa_val
        res["credits_earned"] = sum(t["credits"] for t in transcript)
        res["has_history"] = True
    else:
        res["cgpa"] = None
        res["credits_earned"] = 0
        res["has_history"] = False

    return res


def get_student_transcript(student_id: str) -> List[Dict[str, Any]]:
    """Fetches past semester transcript history for CGPA calculations."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transcript_history WHERE student_id = ? ORDER BY id ASC", (student_id,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_student_photo_bytes(student_id: str) -> bytes:
    """Returns photo bytes loading permanently from disk or SQLite."""
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
    """Updates official reference photo permanently."""
    photo_file = PHOTO_DIR / f"{student_id}.jpg"
    photo_file.write_bytes(photo_bytes)

    photo_b64 = base64.b64encode(photo_bytes).decode("utf-8")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE students SET photo_data = ? WHERE student_id = ?", (photo_b64, student_id))
    conn.commit()
    conn.close()
    return True


def create_student(
    student_id: str,
    name: str,
    proctor_message: Optional[str] = None,
    spotlight_news: Optional[str] = None,
    photo_bytes: Optional[bytes] = None
) -> Dict[str, Any]:
    """
    Registers a new student onboarding profile.
    Sets enrollment_date to Sept 8, 2026 (effective Sept 11, 2026 -> 0 applicable classes).
    No fake CGPA or attendance synthesized.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    if photo_bytes is None:
        photo_bytes = biometrics.generate_default_avatar(name)

    photo_file = PHOTO_DIR / f"{student_id}.jpg"
    photo_file.write_bytes(photo_bytes)

    photo_b64 = base64.b64encode(photo_bytes).decode("utf-8")

    default_proctor = proctor_message or f"Welcome {name}! Maintain regular attendance above 75% once classes commence."
    default_news = spotlight_news or "Academic Notice: Student registration and course onboarding confirmed."

    cursor.execute(
        """
        INSERT INTO students (student_id, name, proctor_message, spotlight_news, photo_data)
        VALUES (?, ?, ?, ?, ?)
        """,
        (student_id, name, default_proctor, default_news, photo_b64)
    )

    # Fetch available courses
    cursor.execute("SELECT course_code FROM course_offerings")
    courses = [r["course_code"] for r in cursor.fetchall()]

    for c_code in courses:
        cursor.execute(
            """
            INSERT INTO student_enrollments (student_id, course_code, enrollment_date, effective_start_date, classes_applicable, classes_attended)
            VALUES (?, ?, '2026-09-08', '2026-09-11', 0, 0)
            """,
            (student_id, c_code)
        )

        # Pending future assessments
        cursor.execute(
            """
            INSERT INTO assessment_instances (student_id, course_code, name, type, max_marks, achieved_marks, date)
            VALUES (?, ?, 'CAT-1 (Internal Assessment 1)', 'CAT-1', 50.0, NULL, '2026-08-28')
            """,
            (student_id, c_code)
        )

    conn.commit()
    conn.close()

    return {"student_id": student_id, "name": name, "courses_enrolled": len(courses)}


def get_student_attendance(student_id: str) -> List[Dict[str, Any]]:
    """
    Fetches attendance records for a student and computes metrics dynamically.
    Adheres strictly to the attendance shortage and safe leaves formulas.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT e.course_code, c.course_title, c.course_type, c.faculty_name, c.classes_conducted,
               e.enrollment_date, e.effective_start_date, e.classes_applicable, e.classes_attended
        FROM student_enrollments e
        JOIN course_offerings c ON e.course_code = c.course_code
        WHERE e.student_id = ?
        ORDER BY e.course_code ASC
        """,
        (student_id,)
    )
    records = []
    for row in cursor.fetchall():
        item = dict(row)
        attended = item["classes_attended"]
        applicable = item["classes_applicable"]
        conducted = item["classes_conducted"]

        item["classes_absent"] = max(0, applicable - attended)

        if applicable == 0:
            item["percentage"] = None
            item["status_type"] = "NEWLY_ENROLLED"
            item["status_remark"] = "— | No attendance recorded since enrollment"
            item["is_alert"] = False
            item["safe_skips"] = 0
            item["classes_needed"] = 0
        else:
            pct = round((attended / applicable) * 100.0, 1)
            item["percentage"] = pct

            if pct < 75.0:
                needed = calculate_classes_needed(attended, applicable)
                item["status_type"] = "SHORTAGE"
                item["status_remark"] = f"Shortage ({pct}%) - Need {needed} consecutive class(es)"
                item["is_alert"] = True
                item["safe_skips"] = 0
                item["classes_needed"] = needed
            elif pct < 80.0:
                item["status_type"] = "MONITOR"
                item["status_remark"] = f"Monitor ({pct}%) - Borderline standing"
                item["is_alert"] = False
                item["safe_skips"] = 0
                item["classes_needed"] = 0
            else:
                skips = calculate_safe_skips(attended, applicable)
                item["status_type"] = "SAFE"
                item["status_remark"] = f"Safe ({pct}%) - Safe to miss {skips} class(es)"
                item["is_alert"] = False
                item["safe_skips"] = skips
                item["classes_needed"] = 0

        records.append(item)

    conn.close()
    return records


def get_assessment_status(
    assessment_date_str: str,
    ref_date_str: str,
    enrollment_date_str: str,
    achieved_marks: Optional[float]
) -> str:
    """Determines realistic assessment state machine status."""
    if enrollment_date_str > assessment_date_str:
        return "NOT_APPLICABLE"
    if assessment_date_str > ref_date_str:
        return "UPCOMING"
    if achieved_marks is not None:
        return "PUBLISHED"
    return "PENDING_EVALUATION"


def get_student_assessments(student_id: str) -> List[Dict[str, Any]]:
    """Fetches assessment instances with dynamic state machine resolution."""
    timeline = get_academic_timeline()
    ref_date = timeline["reference_date"]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT a.id, a.course_code, c.course_title, a.name, a.type, a.max_marks, a.achieved_marks, a.date,
               e.enrollment_date
        FROM assessment_instances a
        JOIN course_offerings c ON a.course_code = c.course_code
        JOIN student_enrollments e ON a.student_id = e.student_id AND a.course_code = e.course_code
        WHERE a.student_id = ?
        ORDER BY a.course_code ASC, a.date ASC
        """,
        (student_id,)
    )

    records = []
    for row in cursor.fetchall():
        item = dict(row)
        status = get_assessment_status(
            assessment_date_str=item["date"],
            ref_date_str=ref_date,
            enrollment_date_str=item["enrollment_date"],
            achieved_marks=item["achieved_marks"]
        )
        item["status"] = status
        records.append(item)

    conn.close()
    return records


def get_attendance_logs(student_id: str, course_code: str) -> List[Dict[str, Any]]:
    """Fetches day-wise drill-down attendance logs."""
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
    """Records confirmed biometric attendance incrementing applicable & attended."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE student_enrollments
        SET classes_applicable = classes_applicable + 1,
            classes_attended = classes_attended + 1
        WHERE student_id = ? AND course_code = ?
        """,
        (student_id, course_code)
    )

    cursor.execute(
        """
        UPDATE course_offerings
        SET classes_conducted = classes_conducted + 1
        WHERE course_code = ?
        """,
        (course_code,)
    )

    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    time_slot = f"{now.strftime('%H:00')} - {now.strftime('%H:50')}"
    method_str = f"{device_name} (Confidence: {confidence_pct:.1f}%)"

    cursor.execute(
        """
        INSERT INTO attendance_logs (student_id, course_code, date, time_slot, status, verification_method, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (student_id, course_code, date_str, time_slot, "Present", method_str, f"{date_str} {time_str}")
    )

    conn.commit()

    cursor.execute(
        "SELECT classes_attended, classes_applicable FROM student_enrollments WHERE student_id = ? AND course_code = ?",
        (student_id, course_code)
    )
    updated = cursor.fetchone()
    conn.close()

    return {
        "student_id": student_id,
        "course_code": course_code,
        "attended": updated["classes_attended"] if updated else 0,
        "total": updated["classes_applicable"] if updated else 0,
        "timestamp": f"{date_str} {time_str}",
        "confidence_pct": confidence_pct
    }


def get_task_progress(student_id: str, course_code: str) -> Dict[str, Dict[str, Any]]:
    """Returns dict of task_id -> progress record."""
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
    """Updates task completion and quiz score."""
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
