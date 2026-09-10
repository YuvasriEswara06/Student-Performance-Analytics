# 🎓 Academic Student Portal & Biometric Analytics MVP

A modern, local-first Academic Student Portal MVP built with **Python**, **Streamlit**, and **SQLite**. Designed with strict separation of concerns, zero-hardcoding database architecture (except syllabus), permanent biometric face enrollment, live IoT phone camera verification (DroidCam / Webcam), institutional attendance compliance, an internal marks portal scaled strictly to 100 marks, and an AI personalized study roadmap with conditional logic and an active-recall mini-quiz loop.

---

## 🏛️ Architecture & Project Structure

The project follows a clean, modular layer separation ready for local development or cloud deployment:

```
Student-Performance-Analytics/
├── app.py                     # Main Streamlit UI, navigation, IoT verification, and layouts
├── database.py                # SQLite (portal.db) schema creation, seeding, queries, and transactions
├── biometrics.py              # Pure Python (PIL + NumPy) biometric vision comparison engine
├── syllabus.py                # Course curriculum dictionary and active-recall question bank
├── ai_engine.py               # Pedagogical AI engine with Amazon Bedrock (boto3) hooks & local fallback
├── registered_faces/          # Permanent disk storage for enrolled biometric ID photos
├── portal.db                  # Local SQLite database (auto-seeded on first run)
├── requirements.txt           # Dependency specifications
└── README.md                  # Comprehensive documentation and run guide
```

---

## 🔑 Key Features & Architectural Compliance

### 1. Zero Hardcoding Policy (Except Syllabus)
- All student profiles, attendance records, internal assessment marks, and day-wise verification logs are dynamically stored and queried from `portal.db`.
- **Only** the course syllabus hierarchy (`syllabus.py`) is structured as a Python dictionary.

### 2. Biometric Face Enrollment & Permanent Storage
- **Permanent ID Photo Storage:** Uploaded student reference photos are permanently preserved both on disk (`registered_faces/<student_id>.jpg`) and inside SQLite `students.photo_data`.
- **Enrolled Profile:** Seeded initially with **Yuvasri Eswara (`21BCE1001`)** with full academic and attendance records.
- **Dynamic Student Registration:** Add new students (e.g. **A Jenita Roselin**) on the fly via the sidebar with instant camera snapshot or photo upload, auto-enrolling them into active semester courses.

### 3. Live IoT Camera Biometric Verification (DroidCam & Webcam)
- **Wi-Fi Phone Camera Integration:** Streams live frames from phone cameras running DroidCam (`http://<ip>:<port>/video`).
- **Automatic Upright Portrait Alignment:** Automatically rotates landscape phone frames 90° counter-clockwise and crops them to vertical $3:4$ portrait frames centered on the face.
- **Biometric Matching Engine:** Zero external C-dependencies, utilizing normalized structural block vectors, 3-channel color histogram correlation, and Laplacian edge contour matching to compute authentic confidence scores.
- **Audited Check-In:** Attendance is incremented in SQLite and logged with exact device name, timestamp, and confidence score.

### 4. Module 1: Student Dashboard
- Metric cards: Overall Attendance % (color-coded for safety), CGPA (out of 10.00), Credits Earned (out of 160.0), and Registered Course Count.
- Biometric Digital ID Card previewing the student's official registered face.
- University Spotlight Announcements feed synced dynamically from the database.
- Direct Faculty Proctor Message card with counseling notes.

### 5. Module 2: Course Attendance Portal
- Strict adherence to attendance standards with **NO Slot column**:
  - Columns: `#`, `Course Code & Title`, `Course Type`, `Faculty Name`, `Attended`, `Total`, `Percentage`, `Status / Remarks`.
  - Prominent visual debarment warnings for courses with attendance `< 75%`.
  - Minimum attendance recovery calculator (classes needed) and safe bunk count.
- **Day-Wise Attendance Log Drill-Down**: Inspect past lecture dates, slots, attendance status (`Present` / `Absent`), and verification sensors.
- **Live Biometric Face Check-in**: Compares live camera snapshot against the enrolled reference ID photo.

### 6. Module 3: Exam & Marks Portal
- Semester selector dropdown dynamically querying distinct semesters from SQLite.
- Internal assessment grid strictly scaled to a **100-mark total**:
  - `Mid-1`: Out of 30
  - `Mid-2`: Out of 30
  - `Assignment`: Out of 40
  - `Total`: Out of 100
  - `Grade / Status`
- Interactive historical performance trend line charts powered by **Altair** with benchmark guidelines at 75% and 90%.

### 7. Module 4: AI Personalized Learning & Study Roadmap
- Select enrolled subject and target exam (Mid-1, Mid-2, Finals / FAT).
- **Conditional Logic Engine**:
  - **Mid-1 Completed only:** Automatically activates a *Retrospective Remedial Recovery Plan* strictly focusing on **Modules 1 & 2**, diagnosing conceptual deficits, and providing target score formulas to achieve an 'A' grade.
  - **Mid-1 & Mid-2 Completed:** Automatically executes a *Comparative Trend Analysis* (calculating score delta, growth velocity, and consistency) paired with forward-looking prep for finals focusing on high-weightage **Modules 3, 4, and 5**.
  - **Pre-Mid-1 / New Student:** Cold-start orientation mode focusing on foundational lecture scope.
- **Active-Recall Mini-Quiz Loop**:
  - Interactive **Active-Recall Mini-Quiz Verification Box** for roadmap tasks.
  - Provides instant verification with correct/incorrect feedback, pedagogical rationale, and persists score in SQLite `task_progress`.
- **Amazon Bedrock Cloud Integration Hooks**:
  - Wired with `boto3` for Amazon Bedrock runtime (Claude 3 Haiku / Titan).
  - Automatically falls back seamlessly to the local pedagogical intelligence engine when running offline without AWS credentials.

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.9+ (tested on Python 3.14)
- `pip`

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
streamlit run app.py
```
Open your browser and navigate to `http://localhost:8501`.

---

## 📱 DroidCam Phone Setup (Optional for IoT Mode)
1. Install **DroidCam** on your Android/iOS phone and connect to the same Wi-Fi as your computer.
2. Open DroidCam on your phone and note the **WiFi IP** (e.g. `192.168.0.3`) and **Port** (`4747`).
3. In the portal under **Course Attendance Portal**, enter the IP and port, keep your phone upright, and click **"Capture & Verify Face from Phone Camera"**.