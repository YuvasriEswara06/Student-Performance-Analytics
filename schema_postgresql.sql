-- schema_postgresql.sql
-- Production PostgreSQL DDL schema matching the Canonical Academic World Specification.
-- Supports Amazon RDS for PostgreSQL deployments.

DROP TABLE IF EXISTS task_progress CASCADE;
DROP TABLE IF EXISTS attendance_logs CASCADE;
DROP TABLE IF EXISTS assessment_instances CASCADE;
DROP TABLE IF EXISTS transcript_history CASCADE;
DROP TABLE IF EXISTS student_enrollments CASCADE;
DROP TABLE IF EXISTS course_offerings CASCADE;
DROP TABLE IF EXISTS academic_timeline CASCADE;
DROP TABLE IF EXISTS students CASCADE;

-- 1. Academic Timeline Table
CREATE TABLE academic_timeline (
    id SERIAL PRIMARY KEY,
    term_name VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    reference_date DATE NOT NULL,
    total_weeks INTEGER NOT NULL
);

-- 2. Course Offerings Table
CREATE TABLE course_offerings (
    course_code VARCHAR(50) PRIMARY KEY,
    course_title VARCHAR(255) NOT NULL,
    course_type VARCHAR(50) NOT NULL,
    faculty_name VARCHAR(255) NOT NULL,
    weekly_sessions INTEGER NOT NULL,
    classes_conducted INTEGER NOT NULL,
    credits INTEGER NOT NULL
);

-- 3. Students Table
CREATE TABLE students (
    student_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    proctor_message TEXT,
    spotlight_news TEXT,
    photo_data TEXT
);

-- 4. Student Enrollments Table
CREATE TABLE student_enrollments (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    course_code VARCHAR(50) NOT NULL REFERENCES course_offerings(course_code) ON DELETE CASCADE,
    enrollment_date DATE NOT NULL,
    effective_start_date DATE NOT NULL,
    classes_applicable INTEGER NOT NULL DEFAULT 0,
    classes_attended INTEGER NOT NULL DEFAULT 0,
    UNIQUE(student_id, course_code)
);

-- 5. Transcript History Table
CREATE TABLE transcript_history (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    semester VARCHAR(255) NOT NULL,
    gpa REAL NOT NULL,
    credits INTEGER NOT NULL
);

-- 6. Assessment Instances Table
CREATE TABLE assessment_instances (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    course_code VARCHAR(50) NOT NULL REFERENCES course_offerings(course_code) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    max_marks REAL NOT NULL,
    achieved_marks REAL,
    date DATE NOT NULL
);

-- 7. Attendance Logs Table
CREATE TABLE attendance_logs (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    course_code VARCHAR(50) NOT NULL REFERENCES course_offerings(course_code) ON DELETE CASCADE,
    date DATE NOT NULL,
    time_slot VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    verification_method TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 8. Task Progress Table
CREATE TABLE task_progress (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    course_code VARCHAR(50) NOT NULL REFERENCES course_offerings(course_code) ON DELETE CASCADE,
    task_id VARCHAR(100) NOT NULL,
    completed INTEGER NOT NULL DEFAULT 0,
    quiz_score REAL,
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, course_code, task_id)
);
