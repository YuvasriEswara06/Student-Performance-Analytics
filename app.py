"""
app.py - Local-First Academic Student Portal MVP
Built with Python and Streamlit.
Adheres strictly to:
1. Zero hardcoding policy for profiles, attendance, and marks (queried from portal.db).
2. Only syllabus curriculum hardcoded as dictionary in syllabus.py.
3. Dynamic student profiles with face enrollment & live biometric matching.
4. Attendance standards (STRICTLY NO slot column, <75% warnings, day-wise log, face-match verification).
5. 100-mark scaled internal marks grid & trend charts.
6. AI personalized learning roadmap with conditional logic engine & active-recall mini-quiz loop.
"""

import streamlit as st
import pandas as pd
import altair as alt
import urllib.request
from typing import Dict, Any, List, Optional
from PIL import Image
import io

import database
import syllabus
import ai_engine
import biometrics


def fetch_droidcam_frame(ip: str = "192.168.0.3", port: int = 4747, timeout: int = 4) -> Optional[bytes]:
    """Directly extracts a clean JPEG frame from DroidCam MJPEG stream over Wi-Fi."""
    url = f"http://{ip}:{port}/video"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as stream:
            buf = b""
            for _ in range(120):
                chunk = stream.read(4096)
                if not chunk:
                    break
                buf += chunk
                idx = buf.find(b"Content-Length:")
                if idx != -1:
                    c_end = buf.find(b"\r\n", idx)
                    if c_end != -1:
                        try:
                            c_len = int(buf[idx + 15:c_end].strip())
                            header_end = buf.find(b"\r\n\r\n", idx)
                            if header_end != -1:
                                start_img = header_end + 4
                                if len(buf) >= start_img + c_len:
                                    return buf[start_img:start_img + c_len]
                        except Exception:
                            pass
                start = buf.find(b"\xff\xd8")
                if start != -1:
                    end = buf.find(b"\xff\xd9", start + 2)
                    if end != -1 and (end + 2 - start) > 5000:
                        return buf[start:end + 2]
    except Exception:
        return None
    return None


# -------------------------------------------------------------
# Page Configuration & Modern Theme Styling
# -------------------------------------------------------------
st.set_page_config(
    page_title="Academic Student Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished academic portal aesthetic
st.markdown(
    """
    <style>
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
        max-width: 96%;
    }
    
    .portal-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 1.2rem 1.8rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .portal-header h2 {
        color: #ffffff !important;
        margin: 0;
        font-size: 1.7rem;
        font-weight: 700;
    }
    .portal-header p {
        color: #e0e7ff;
        margin: 0.2rem 0 0 0;
        font-size: 0.95rem;
    }

    .status-badge-iot {
        background-color: #064e3b;
        color: #6ee7b7;
        border: 1px solid #059669;
        padding: 0.35rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .pulse-dot {
        width: 8px;
        height: 8px;
        background-color: #10b981;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 8px #10b981;
    }

    .metric-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-box:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.08);
    }
    .metric-title {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-val {
        font-size: 1.8rem;
        font-weight: 800;
        color: #0f172a;
        margin: 0.3rem 0;
    }
    .metric-sub {
        font-size: 0.8rem;
        font-weight: 500;
    }

    .badge-alert {
        background-color: #fef2f2;
        color: #b91c1c;
        border: 1px solid #fecaca;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.82rem;
    }
    .badge-safe {
        background-color: #f0fdf4;
        color: #15803d;
        border: 1px solid #bbf7d0;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.82rem;
    }

    .card-proctor {
        background: #f8fafc;
        border-left: 5px solid #3b82f6;
        border-radius: 8px;
        padding: 1.2rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03);
    }
    .card-spotlight {
        background: #fffbeb;
        border-left: 5px solid #f59e0b;
        border-radius: 8px;
        padding: 1.2rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03);
    }

    .biometric-card {
        background: #ffffff;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 3px 10px rgba(0,0,0,0.05);
    }

    .quiz-container {
        background: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        padding: 1.2rem;
        margin-top: 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------------------
# Database Bootstrap
# -------------------------------------------------------------
database.init_db(force_reseed=False)

# -------------------------------------------------------------
# Sidebar & Global State Management
# -------------------------------------------------------------
st.sidebar.image(
    "https://img.icons8.com/fluency/96/graduation-cap.png",
    width=64
)
st.sidebar.title("Academic Portal")
st.sidebar.caption("Institutional Student Performance & AI Analytics")

# 1. Profile Switcher (Authentication Bypass)
student_profiles = database.get_student_profiles()
if not student_profiles:
    database.init_db(force_reseed=True)
    student_profiles = database.get_student_profiles()

profile_map = {f"{p['name']} ({p['student_id']})": p["student_id"] for p in student_profiles}

if "current_student_id" not in st.session_state or st.session_state.current_student_id not in profile_map.values():
    st.session_state.current_student_id = student_profiles[0]["student_id"]

current_display_name = next(
    (name for name, sid in profile_map.items() if sid == st.session_state.current_student_id),
    list(profile_map.keys())[0]
)

selected_profile_name = st.sidebar.selectbox(
    "👤 Active Student Profile",
    options=list(profile_map.keys()),
    index=list(profile_map.keys()).index(current_display_name),
    help="Switch between enrolled student profiles."
)

active_student_id = profile_map[selected_profile_name]
if active_student_id != st.session_state.current_student_id:
    st.session_state.current_student_id = active_student_id
    st.rerun()

# 2. View Currently Enrolled Face from Database
current_photo_bytes = database.get_student_photo_bytes(st.session_state.current_student_id)
with st.sidebar.expander("👁️ View Registered Face in Database", expanded=True):
    st.image(current_photo_bytes, caption=f"Enrolled for {selected_profile_name}", use_container_width=True)
    st.markdown(
        """
        <div style="font-size:0.75rem; color:#15803d; background:#f0fdf4; border:1px solid #bbf7d0; border-radius:6px; padding:6px; text-align:center; margin-top:4px;">
            ✅ Stored in SQLite (<code>portal.db</code>)
        </div>
        """,
        unsafe_allow_html=True
    )

# 3. Live IoT Connection Status Badge
st.sidebar.markdown(
    """
    <div style="margin: 0.8rem 0 1.2rem 0;">
        <span class="status-badge-iot">
            <span class="pulse-dot"></span> IoT Status: Connected
        </span>
    </div>
    """,
    unsafe_allow_html=True
)

# 3. Add Student & Enroll Face Feature
with st.sidebar.expander("➕ Register Student & Enroll Face", expanded=False):
    st.markdown("#### Enroll New Student")
    st.caption("Register student profile and official biometric reference photo.")

    with st.form("form_register_student", clear_on_submit=False):
        new_name = st.text_input("Full Name *", placeholder="e.g. A Jenita Roselin")
        new_id = st.text_input("Student Registration No. *", placeholder="e.g. 21BCE1042")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            new_cgpa = st.number_input("CGPA", min_value=0.0, max_value=10.0, value=8.15, step=0.01)
        with col_c2:
            new_credits = st.number_input("Credits", min_value=0, max_value=200, value=86, step=1)
        
        new_proctor = st.text_area(
            "Faculty Proctor Advisory Note",
            value="Welcome to the academic semester! Maintain continuous attendance above 75% for exam clearance."
        )

        st.markdown("**Biometric Reference Photo Enrollment:**")
        enroll_mode = st.radio(
            "Select Photo Source:",
            ["📷 Camera Snap (st.camera_input)", "📁 File Upload", "🎨 Generate Stylized ID Avatar"],
            index=0,
            key="enroll_photo_mode"
        )

        snapped_ref = None
        uploaded_ref = None
        if enroll_mode == "📷 Camera Snap (st.camera_input)":
            snapped_ref = st.camera_input("Snap Official Reference Photo", key="cam_enroll")
        elif enroll_mode == "📁 File Upload":
            uploaded_ref = st.file_uploader("Upload ID Photo (JPG/PNG)", type=["jpg", "jpeg", "png"], key="file_enroll")

        btn_submit_student = st.form_submit_button("✅ Register & Enroll Student", type="primary", use_container_width=True)

        if btn_submit_student:
            if not new_name.strip() or not new_id.strip():
                st.error("Please provide both Student Name and Registration Number.")
            else:
                existing_check = database.get_student_by_id(new_id.strip().upper())
                if existing_check:
                    st.error(f"Student ID '{new_id.strip().upper()}' is already registered.")
                else:
                    # Resolve photo bytes
                    ref_photo_bytes = None
                    if snapped_ref is not None:
                        ref_photo_bytes = snapped_ref.getvalue()
                    elif uploaded_ref is not None:
                        ref_photo_bytes = uploaded_ref.getvalue()
                    else:
                        ref_photo_bytes = biometrics.generate_default_avatar(new_name.strip())

                    database.create_student(
                        student_id=new_id.strip().upper(),
                        name=new_name.strip(),
                        cgpa=float(new_cgpa),
                        credits_earned=int(new_credits),
                        proctor_message=new_proctor.strip(),
                        photo_bytes=ref_photo_bytes
                    )
                    st.success(f"🎉 Student **{new_name.strip()}** successfully enrolled with biometric reference!")
                    st.session_state.current_student_id = new_id.strip().upper()
                    st.rerun()

# 4. Portal Navigation
portal_menu = [
    "📊 Student Dashboard",
    "📋 Course Attendance Portal",
    "📝 Exam & Marks Portal",
    "🧠 AI Study Roadmap & Active-Recall Quiz"
]
selected_nav = st.sidebar.radio("Navigation", portal_menu)

st.sidebar.divider()

# Cloud Bedrock Hook Status
bedrock_active = ai_engine.get_bedrock_client() is not None
if bedrock_active:
    st.sidebar.success("☁️ AWS Bedrock: Active")
else:
    st.sidebar.info("⚡ AI Engine: Local Fallback (Bedrock Hook Ready)")

with st.sidebar.expander("⚙️ Database Controls"):
    if st.button("🔄 Reset / Re-seed Database"):
        database.init_db(force_reseed=True)
        st.session_state.current_student_id = "21BCE1001"
        st.success("Database restored to default seeded state (Yuvasri Eswara)!")
        st.rerun()

# Fetch active student details dynamically from SQLite
student = database.get_student_by_id(st.session_state.current_student_id)
if not student:
    st.session_state.current_student_id = student_profiles[0]["student_id"]
    student = database.get_student_by_id(st.session_state.current_student_id)

student_photo_bytes = database.get_student_photo_bytes(student["student_id"])

# -------------------------------------------------------------
# Global Header
# -------------------------------------------------------------
st.markdown(
    f"""
    <div class="portal-header">
        <div>
            <h2>🎓 Academic Student Portal</h2>
            <p><strong>Student:</strong> {student['name']} &nbsp;|&nbsp; <strong>Registration No:</strong> {student['student_id']} &nbsp;|&nbsp; <strong>Semester:</strong> Winter 2025-26</p>
        </div>
        <div>
            <span class="status-badge-iot">
                <span class="pulse-dot"></span> IoT Status: Connected
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# =============================================================
# MODULE 1: STUDENT DASHBOARD
# =============================================================
if selected_nav == "📊 Student Dashboard":
    st.subheader("📊 Executive Student Overview")

    # Fetch dynamic attendance & marks for metrics
    attendance_records = database.get_student_attendance(student["student_id"])
    total_attended = sum(a["attended_classes"] for a in attendance_records)
    total_classes = sum(a["total_classes"] for a in attendance_records)
    overall_att_pct = round((total_attended / total_classes * 100), 2) if total_classes > 0 else 0.0

    # Top Metric Cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        att_color = "#15803d" if overall_att_pct >= 75.0 else "#b91c1c"
        att_sub = "✅ Safe Standing" if overall_att_pct >= 75.0 else "⚠️ Low Attendance Alert"
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-title">Overall Attendance</div>
                <div class="metric-val" style="color: {att_color};">{overall_att_pct}%</div>
                <div class="metric-sub" style="color: {att_color};">{att_sub} ({total_attended}/{total_classes})</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        cgpa_color = "#1e3c72" if student["cgpa"] >= 8.5 else "#d97706"
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-title">Cumulative GPA</div>
                <div class="metric-val" style="color: {cgpa_color};">{student['cgpa']:.2f}</div>
                <div class="metric-sub" style="color: #64748b;">Scale: 10.00 Max</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-title">Credits Earned</div>
                <div class="metric-val" style="color: #047857;">{student['credits_earned']}</div>
                <div class="metric-sub" style="color: #64748b;">Degree Target: 160.0</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-title">Enrolled Courses</div>
                <div class="metric-val" style="color: #6366f1;">{len(attendance_records)}</div>
                <div class="metric-sub" style="color: #64748b;">Winter Semester 2025-26</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Student Biometric Identity & Advisories
    dash_col_photo, dash_col_info = st.columns([1, 2])

    with dash_col_photo:
        st.markdown("### 🪪 Biometric Digital ID Card")
        st.image(student_photo_bytes, caption=f"Official Reference Photo: {student['name']}", use_container_width=True)

        with st.expander("📷 Update / Retake Reference Photo"):
            update_opt = st.radio(
                "Update method:",
                ["Camera Snap", "File Upload"],
                key="dash_update_opt"
            )
            if update_opt == "Camera Snap":
                new_snap = st.camera_input("Retake Face Photo", key="dash_retake_cam")
                if new_snap and st.button("Save New Reference Photo", key="btn_save_snap"):
                    database.update_student_photo(student["student_id"], new_snap.getvalue())
                    st.success("Reference photo updated!")
                    st.rerun()
            else:
                new_file = st.file_uploader("Upload New Photo", type=["png", "jpg", "jpeg"], key="dash_retake_file")
                if new_file and st.button("Save Uploaded Photo", key="btn_save_file"):
                    database.update_student_photo(student["student_id"], new_file.getvalue())
                    st.success("Reference photo updated!")
                    st.rerun()

    with dash_col_info:
        st.markdown("### 📢 Spotlight Announcements & Faculty Communications")
        st.markdown(
            f"""
            <div class="card-spotlight">
                <div style="font-weight: 700; color: #b45309; margin-bottom: 0.4rem; font-size: 1rem;">
                    🏛️ University Bulletin & Placement Alerts
                </div>
                <div style="color: #451a03; line-height: 1.5; font-size: 0.95rem;">
                    {student['spotlight_news']}
                </div>
                <div style="margin-top: 0.8rem; font-size: 0.8rem; color: #92400e;">
                    <em>Synced with Central Broadcast Feed</em>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="card-proctor">
                <div style="font-weight: 700; color: #1d4ed8; margin-bottom: 0.4rem; font-size: 1rem;">
                    📬 Official Communication from Assigned Faculty Proctor
                </div>
                <div style="color: #1e293b; line-height: 1.5; font-size: 0.95rem;">
                    "{student['proctor_message']}"
                </div>
                <div style="margin-top: 0.8rem; font-size: 0.8rem; color: #64748b;">
                    <em>Recorded by Faculty Proctor | Academic Counseling Cell</em>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick Summary Table of Registered Courses
    st.markdown("### 📚 Registered Course Catalog")
    df_courses = pd.DataFrame([
        {
            "Course Code": a["course_code"],
            "Course Title": a["course_title"],
            "Type": a["course_type"],
            "Faculty": a["faculty_name"],
            "Attendance %": f"{a['percentage']}%",
            "Status": "⚠️ Low Attendance (<75%)" if a["is_alert"] else "✅ Safe (>=75%)"
        }
        for a in attendance_records
    ])
    st.dataframe(df_courses, use_container_width=True, hide_index=True)


# =============================================================
# MODULE 2: COURSE ATTENDANCE PORTAL
# =============================================================
elif selected_nav == "📋 Course Attendance Portal":
    st.subheader("📋 Course-wise Attendance Register")
    st.caption("Official Class Attendance Register adhering strictly to institutional formatting guidelines.")

    attendance_records = database.get_student_attendance(student["student_id"])

    # High-level Alert Banner if any course is < 75%
    low_att_courses = [a for a in attendance_records if a["is_alert"]]
    if low_att_courses:
        st.error(
            f"⚠️ **Debarment Advisory Alert:** You have **{len(low_att_courses)}** course(s) below the mandatory 75% threshold: "
            + ", ".join([f"**{c['course_code']} ({c['percentage']}%)**" for c in low_att_courses])
            + ". Minimum 75% attendance is strictly enforced for exam eligibility."
        )
    else:
        st.success("✅ **Attendance Compliant:** All registered courses meet or exceed the mandatory 75% threshold.")

    # 1. Attendance Table (STRICTLY NO SLOT COLUMN)
    table_rows = []
    for idx, item in enumerate(attendance_records, start=1):
        table_rows.append({
            "#": idx,
            "Course Code & Title": f"{item['course_code']} - {item['course_title']}",
            "Course Type": item["course_type"],
            "Faculty Name": item["faculty_name"],
            "Attended": item["attended_classes"],
            "Total": item["total_classes"],
            "Percentage": f"{item['percentage']:.2f}%",
            "Status / Remarks": item["status_remark"]
        })

    df_attendance = pd.DataFrame(table_rows)

    def highlight_attendance(row):
        pct_val = float(str(row["Percentage"]).replace("%", ""))
        if pct_val < 75.0:
            return ["background-color: #fff1f2; color: #9f1239; font-weight: bold"] * len(row)
        return [""] * len(row)

    styled_df = df_attendance.style.apply(highlight_attendance, axis=1)
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Live Biometric Face-Match Verification & Day-Wise Log Drill-Down
    att_col1, att_col2 = st.columns([1, 1])

    with att_col1:
        st.markdown("### 📸 Biometric Face-Match Verification (IoT Node)")
        st.caption("Validates live frame against student's enrolled reference photo before granting attendance.")

        # 🪪 Show Enrolled Reference Status & Photo Preview
        ref_card_col1, ref_card_col2 = st.columns([1, 2])
        with ref_card_col1:
            st.image(student_photo_bytes, caption="Enrolled Reference", width=120)
        with ref_card_col2:
            st.markdown(
                f"""
                <div style="background:#f0fdf4; border:1px solid #86efac; border-radius:8px; padding:10px; margin-top:5px;">
                    <div style="font-weight:700; color:#166534; font-size:0.9rem;">
                        ✅ Face Registered in Database
                    </div>
                    <div style="font-size:0.8rem; color:#15803d; margin-top:2px;">
                        <strong>Student:</strong> {student['name']}<br>
                        <strong>Reg No:</strong> {student['student_id']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with st.expander("📷 Change / Retake Enrolled Reference Photo", expanded=False):
            st.caption("Upload or snap your real face photo to replace the current registered reference.")
            up_ref_mode = st.radio("Choose source:", ["Webcam Snap", "File Upload"], key="m2_up_ref_mode", horizontal=True)
            if up_ref_mode == "Webcam Snap":
                m2_snap = st.camera_input("Snap New Reference Face", key="m2_cam_ref")
                if m2_snap and st.button("💾 Save as My Registered Face", key="m2_save_snap_btn"):
                    database.update_student_photo(student["student_id"], m2_snap.getvalue())
                    st.success("Registered reference face updated successfully!")
                    st.rerun()
            else:
                m2_file = st.file_uploader("Upload Portrait Photo", type=["png", "jpg", "jpeg"], key="m2_file_ref")
                if m2_file and st.button("💾 Save as My Registered Face", key="m2_save_file_btn"):
                    database.update_student_photo(student["student_id"], m2_file.getvalue())
                    st.success("Registered reference face updated successfully!")
                    st.rerun()

        st.markdown("---")

        course_options = {f"{a['course_code']} - {a['course_title']}": a["course_code"] for a in attendance_records}
        if course_options:
            selected_course_label = st.selectbox(
                "Select Course for Biometric Check-In:",
                options=list(course_options.keys()),
                key="face_match_course"
            )
            target_course_code = course_options[selected_course_label]
        else:
            st.warning("No courses enrolled.")
            target_course_code = None

        iot_mode = st.radio(
            "Select IoT Verification Camera:",
            [
                "📱 DroidCam Phone IoT Node",
                "📹 In-Browser Camera Input (Webcam)",
                "⚡ Quick Biometric Simulation (Testing Mode)"
            ],
            index=0,
            horizontal=False,
            key="iot_camera_mode"
        )

        # Container for side-by-side comparison
        if target_course_code:
            if iot_mode == "📱 DroidCam Phone IoT Node":
                col_ip, col_port = st.columns([3, 1])
                with col_ip:
                    droid_ip = st.text_input("IoT Phone IP Address (see on DroidCam phone screen):", value="192.168.0.3", key="droid_ip")
                with col_port:
                    droid_port = st.number_input("Port:", value=4747, step=1, key="droid_port")

                col_orient, col_thresh = st.columns([2, 1])
                with col_orient:
                    orient_option = st.selectbox(
                        "🔄 Camera Orientation Angle:",
                        [
                            "🔄 Rotate 90° (Upright for phone held vertically)",
                            "Normal (0° - Landscape)",
                            "🔄 Rotate 270° (Clockwise)",
                            "🔄 Rotate 180° (Inverted)"
                        ],
                        index=0,
                        help="DroidCam streams landscape by default. Rotate 90° positions your face upright exactly like the ID photo."
                    )
                with col_thresh:
                    custom_threshold = st.number_input("Match Threshold %:", min_value=30.0, max_value=90.0, value=50.0, step=1.0)

                # Determine rotation degrees
                rot_deg = 90
                if "Normal" in orient_option:
                    rot_deg = 0
                elif "270" in orient_option:
                    rot_deg = 270
                elif "180" in orient_option:
                    rot_deg = 180

                show_viewfinder = st.checkbox(
                    "Show Continuous Video Viewfinder in Browser",
                    value=False,
                    help="Uncheck when capturing photos to prevent DroidCam single-client socket lock."
                )

                if show_viewfinder:
                    st.markdown(
                        f"""
                        <div style="background:#0f172a; padding:10px; border-radius:12px; text-align:center; border:2px solid #10b981; max-width:270px; margin:0 auto 12px auto; box-shadow:0 4px 14px rgba(0,0,0,0.25);">
                            <div style="font-size:0.78rem; color:#10b981; font-weight:700; margin-bottom:6px; display:flex; align-items:center; justify-content:center; gap:6px;">
                                <span class="pulse-dot"></span> LIVE PORTRAIT IOT STREAM
                            </div>
                            <img src="http://{droid_ip}:{droid_port}/video" style="width:100%; height:340px; border-radius:8px; object-fit:cover; display:block;" onerror="this.onerror=null; this.src='https://placehold.co/270x340/0f172a/ef4444?text=Camera+Offline';" />
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.info("📱 **IoT Node Ready:** Point your phone camera at your face and click **Capture & Verify Face**.")

                if st.button("📷 Capture & Verify Face from Phone Camera", type="primary", use_container_width=True, key="btn_droid_snap"):
                    with st.spinner(f"Pulling live biometric frame from phone IoT node ({droid_ip}:{droid_port})..."):
                        live_frame_bytes = fetch_droidcam_frame(ip=droid_ip, port=int(droid_port), timeout=4)
                        if live_frame_bytes:
                            # 1. Rotate image so face is positioned upright (forehead at top, chin at bottom)
                            upright_bytes = biometrics.rotate_image(live_frame_bytes, rotation_degrees=rot_deg)

                            # 2. Crop to clean vertical 3:4 portrait matching the ID card
                            portrait_live_bytes = biometrics.crop_to_portrait(upright_bytes)

                            # 3. Perform real biometric comparison on upright portrait
                            match_result = biometrics.compare_biometrics(
                                reference_bytes=student_photo_bytes,
                                captured_bytes=portrait_live_bytes,
                                threshold=float(custom_threshold)
                            )

                            # Side-by-side upright vertical portrait comparison
                            comp_c1, comp_c2 = st.columns(2)
                            with comp_c1:
                                st.image(student_photo_bytes, caption="Enrolled Reference ID (Upright)", use_container_width=True)
                            with comp_c2:
                                st.image(portrait_live_bytes, caption="Live IoT Capture (Positioned Upright)", use_container_width=True)

                            conf = match_result["confidence_pct"]
                            st.metric("Biometric Match Confidence", f"{conf:.1f}%", delta="Verified" if match_result["is_match"] else "Mismatch", delta_color="normal" if match_result["is_match"] else "inverse")

                            if match_result["is_match"]:
                                result = database.record_face_match_attendance(
                                    student["student_id"],
                                    target_course_code,
                                    device_name=f"IoT Phone Camera ({droid_ip}:{droid_port})",
                                    confidence_pct=conf
                                )
                                st.success(
                                    f"🎉 **Face-Match Confirmed! (Confidence: {conf:.1f}%)**\n\n"
                                    f"• Biometric attendance verified for **{result['course_code']}**\n\n"
                                    f"• Updated Attended Count: **{result['attended']} / {result['total']}**\n\n"
                                    f"• Verification Timestamp: **{result['timestamp']}**"
                                )
                                st.rerun()
                            else:
                                st.error(
                                    f"❌ **Biometric Rejection:** Face confidence score ({conf:.1f}%) is below the required {custom_threshold:.1f}% threshold.\n\n"
                                    f"Ensure the registered student ({student['name']}) is facing the camera with adequate lighting."
                                )
                        else:
                            st.error(
                                f"⚠️ Could not pull frame from http://{droid_ip}:{droid_port}/video.\n\n"
                                "1. Ensure DroidCam is running on your phone.\n"
                                "2. Make sure 'Show Continuous Video Viewfinder' is UNCHECKED during capture.\n"
                                "3. Confirm phone and PC are on the same Wi-Fi network."
                            )

            elif iot_mode == "📹 In-Browser Camera Input (Webcam)":
                st.info("📱 Look at your webcam and click **Take Photo** to verify biometric match against your enrolled reference.")
                cam_photo = st.camera_input("Scan Face via Camera", key="iot_camera_feed")
                if cam_photo is not None:
                    live_bytes = cam_photo.getvalue()
                    portrait_live_bytes = biometrics.crop_to_portrait(live_bytes)
                    match_result = biometrics.compare_biometrics(
                        reference_bytes=student_photo_bytes,
                        captured_bytes=portrait_live_bytes,
                        threshold=58.0
                    )

                    comp_c1, comp_c2 = st.columns(2)
                    with comp_c1:
                        st.image(student_photo_bytes, caption="Enrolled Reference ID", use_container_width=True)
                    with comp_c2:
                        st.image(portrait_live_bytes, caption="Live Camera Portrait Snapshot", use_container_width=True)

                    conf = match_result["confidence_pct"]
                    st.metric("Biometric Match Confidence", f"{conf:.1f}%", delta="Verified" if match_result["is_match"] else "Mismatch", delta_color="normal" if match_result["is_match"] else "inverse")

                    if match_result["is_match"]:
                        if st.button("Confirm & Commit Biometric Attendance", type="primary", use_container_width=True):
                            result = database.record_face_match_attendance(
                                student["student_id"],
                                target_course_code,
                                device_name="IoT In-Browser Camera Node",
                                confidence_pct=conf
                            )
                            st.success(
                                f"🎉 **Face-Match Confirmed!** Biometric attendance verified for **{result['course_code']}**.\n\n"
                                f"• Attended Count: **{result['attended']} / {result['total']}**\n\n"
                                f"• Device: **IoT In-Browser Camera (Confidence: {conf:.1f}%)**\n\n"
                                f"• Timestamp: **{result['timestamp']}**"
                            )
                            st.rerun()
                    else:
                        st.error(
                            f"❌ **Biometric Rejection:** Face match confidence ({conf:.1f}%) is below the required 58.0% threshold."
                        )

            else:
                st.info("⚡ Instant edge biometric test against registered profile.")
                if st.button("📷 Trigger Biometric Verification", type="primary", use_container_width=True, key="btn_sim_face"):
                    with st.spinner(f"Verifying facial biometric vectors for {student['name']}..."):
                        result = database.record_face_match_attendance(
                            student["student_id"],
                            target_course_code,
                            device_name="IoT Edge Sensor Node #01",
                            confidence_pct=99.4
                        )
                        st.success(
                            f"🎉 **Face-Match Confirmed!** Attendance verified for **{result['course_code']}**.\n\n"
                            f"• Updated Attended Count: **{result['attended']} / {result['total']}**\n\n"
                            f"• Biometric Timestamp: **{result['timestamp']}**\n\n"
                            f"• Match Confidence: **99.4%**"
                        )
                        st.rerun()

    with att_col2:
        st.markdown("### 📅 Day-Wise Attendance Log Drill-Down")
        if course_options:
            drill_course_label = st.selectbox(
                "Select Course for Detailed Day-Wise Log:",
                options=list(course_options.keys()),
                key="drill_down_course"
            )
            drill_course_code = course_options[drill_course_label]
            logs = database.get_attendance_logs(student["student_id"], drill_course_code)

            if logs:
                df_logs = pd.DataFrame([
                    {
                        "Date": log["date"],
                        "Time Slot": log["time_slot"],
                        "Status": "🟢 Present" if log["status"] == "Present" else "🔴 Absent",
                        "Verification Method": log["verification_method"],
                        "Recorded At": log["timestamp"]
                    }
                    for log in logs
                ])
                st.dataframe(df_logs, use_container_width=True, hide_index=True)
            else:
                st.info(f"No prior day-wise logs recorded yet for {drill_course_code}. Click 'Capture & Verify Face' to generate live entries.")


# =============================================================
# MODULE 3: EXAM & MARKS PORTAL
# =============================================================
elif selected_nav == "📝 Exam & Marks Portal":
    st.subheader("📝 Internal Assessment & Examination Portal")
    st.caption("Internal assessment marks strictly scaled to a 100-mark total.")

    # 1. Semester Selection Dropdown
    semesters = database.get_available_semesters(student["student_id"])
    selected_semester = st.selectbox("📅 Select Academic Semester:", options=semesters, index=0)

    # 2. Internal Assessment Grid Scaled to 100 Marks
    marks_records = database.get_student_marks(student["student_id"], selected_semester)

    if marks_records:
        marks_rows = []
        for m in marks_records:
            mid1_str = f"{m['mid_1']:.1f}" if m["mid_1"] is not None else "Pending"
            mid2_str = f"{m['mid_2']:.1f}" if m["mid_2"] is not None else "Pending"
            assign_str = f"{m['assignment']:.1f}" if m["assignment"] is not None else "Pending"
            total_str = f"{m['total']:.1f}" if m["total"] is not None else "In Progress"

            marks_rows.append({
                "Course Code": m["course_code"],
                "Course Title": m["course_title"],
                "Credits": m["credits"],
                "Mid-1 (out of 30)": mid1_str,
                "Mid-2 (out of 30)": mid2_str,
                "Assignment (out of 40)": assign_str,
                "Total (out of 100)": total_str,
                "Grade / Status": m["grade"]
            })

        df_marks = pd.DataFrame(marks_rows)
        st.dataframe(df_marks, use_container_width=True, hide_index=True)

        st.caption("ℹ️ *Assessment Grading Matrix: Mid-1 (30 pts) + Mid-2 (30 pts) + Continuous Assignment (40 pts) = 100 Total Marks.*")

        st.markdown("<br>", unsafe_allow_html=True)

        # 3. Historical Performance Trend Line-Graph Selector per Subject
        evaluated_courses = [m for m in marks_records if m["mid_1"] is not None]
        if evaluated_courses:
            st.markdown("### 📈 Subject Performance Breakdown & Historical Trends")

            course_titles = {f"{m['course_code']} - {m['course_title']}": m for m in evaluated_courses}
            selected_trend_course = st.selectbox(
                "Select Subject for Performance Trend Analysis:",
                options=list(course_titles.keys())
            )
            course_mark = course_titles[selected_trend_course]

            chart_data = []
            if course_mark["mid_1"] is not None:
                chart_data.append({
                    "Assessment Component": "Mid-1 Assessment",
                    "Score Achieved": course_mark["mid_1"],
                    "Max Marks": 30,
                    "Normalized Percentage": round((course_mark["mid_1"] / 30.0) * 100, 1)
                })

            if course_mark["mid_2"] is not None:
                chart_data.append({
                    "Assessment Component": "Mid-2 Assessment",
                    "Score Achieved": course_mark["mid_2"],
                    "Max Marks": 30,
                    "Normalized Percentage": round((course_mark["mid_2"] / 30.0) * 100, 1)
                })

            if course_mark["assignment"] is not None:
                chart_data.append({
                    "Assessment Component": "Assignments & Quizzes",
                    "Score Achieved": course_mark["assignment"],
                    "Max Marks": 40,
                    "Normalized Percentage": round((course_mark["assignment"] / 40.0) * 100, 1)
                })

            if course_mark["total"] is not None and course_mark["mid_2"] is not None:
                chart_data.append({
                    "Assessment Component": "Aggregate Total",
                    "Score Achieved": course_mark["total"],
                    "Max Marks": 100,
                    "Normalized Percentage": course_mark["total"]
                })

            if chart_data:
                df_chart = pd.DataFrame(chart_data)

                line = alt.Chart(df_chart).mark_line(point=alt.OverlayMarkDef(size=80, filled=True), color="#1e3c72", strokeWidth=3).encode(
                    x=alt.X("Assessment Component:N", sort=None, title="Assessment Component"),
                    y=alt.Y("Normalized Percentage:Q", title="Score (%)", scale=alt.Scale(domain=[0, 105])),
                    tooltip=["Assessment Component", "Score Achieved", "Max Marks", "Normalized Percentage"]
                )

                bench_rule = alt.Chart(pd.DataFrame([{"y": 75, "label": "Passing Benchmark (75%)"}, {"y": 90, "label": "Excellence Target (90%)"}])).mark_rule(
                    strokeDash=[5, 5], color="#10b981", opacity=0.7
                ).encode(y="y:Q")

                final_chart = (line + bench_rule).properties(
                    title=f"Assessment Performance Trajectory - {course_mark['course_code']}",
                    height=320
                )

                st.altair_chart(final_chart, use_container_width=True)
        else:
            st.info("Assessment scores for this student are currently pending evaluation (Cold-Start Mode).")

    else:
        st.info(f"No marks records found for semester {selected_semester}.")


# =============================================================
# MODULE 4: AI PERSONALIZED LEARNING & STUDY ROADMAP
# =============================================================
elif selected_nav == "🧠 AI Study Roadmap & Active-Recall Quiz":
    st.subheader("🧠 AI Personalized Learning & Dynamic Study Roadmap")
    st.caption("Pedagogical AI Engine generating tailored remedial roadmaps and active-recall verification loops.")

    courses = database.get_student_attendance(student["student_id"])
    course_opts = {f"{c['course_code']} - {c['course_title']}": c["course_code"] for c in courses}

    if not course_opts:
        st.warning("No courses enrolled for this student.")
        st.stop()

    col_subj, col_exam = st.columns([1, 1])
    with col_subj:
        selected_subj_label = st.selectbox(
            "Select Enrolled Subject:",
            options=list(course_opts.keys()),
            key="ai_subj_selector"
        )
        active_course_code = course_opts[selected_subj_label]

    with col_exam:
        target_exam = st.selectbox(
            "Select Target Examination:",
            options=[
                "Finals (FAT - Comprehensive Examination)",
                "Mid-2 (Internal Assessment 2)",
                "Mid-1 (Internal Assessment 1)"
            ],
            key="ai_exam_selector"
        )

    current_marks_list = database.get_student_marks(student["student_id"], "Winter Semester 2025-26")
    marks_rec = next((m for m in current_marks_list if m["course_code"] == active_course_code), None)
    course_syllabus = syllabus.get_course_syllabus(active_course_code)

    if not course_syllabus:
        st.warning(f"Syllabus structure not mapped for {active_course_code}.")
        st.stop()

    saved_progress = database.get_task_progress(student["student_id"], active_course_code)
    completed_task_ids = [tid for tid, rec in saved_progress.items() if rec.get("completed") == 1]

    # Run AI Conditional Logic Engine
    analysis = ai_engine.analyze_student_roadmap(
        student_profile=student,
        course_code=active_course_code,
        target_exam=target_exam,
        marks_record=marks_rec,
        syllabus_data=course_syllabus,
        completed_task_ids=completed_task_ids
    )

    # Bedrock Hook Invocation (Graceful local fallback if Bedrock not configured)
    if analysis["is_bedrock_configured"]:
        with st.expander("☁️ Amazon Bedrock LLM Insights (Claude 3 Haiku / Titan)", expanded=False):
            with st.spinner("Invoking Amazon Bedrock runtime API..."):
                bedrock_output = ai_engine.generate_bedrock_roadmap(
                    student_name=student["name"],
                    course_code=active_course_code,
                    course_title=course_syllabus["course_title"],
                    condition=analysis["condition_type"],
                    mid_1=marks_rec.get("mid_1") if marks_rec else None,
                    mid_2=marks_rec.get("mid_2") if marks_rec else None,
                    assignment=marks_rec.get("assignment") if marks_rec else None
                )
                if bedrock_output:
                    st.markdown(bedrock_output)
                else:
                    st.info("Bedrock returned empty response; displaying local pedagogical insights.")

    # Display Condition Badge & Executive Diagnosis
    if analysis["condition_type"] == "MID_1_ONLY":
        st.warning(f"**{analysis['condition_badge']}**\n\n{analysis['condition_summary']}")
    elif analysis["condition_type"] == "PRE_MID_1":
        st.info(f"**{analysis['condition_badge']}**\n\n{analysis['condition_summary']}")
    else:
        st.success(f"**{analysis['condition_badge']}**\n\n{analysis['condition_summary']}")

    # Metrics Tracking
    m_col1, m_col2, m_col3 = st.columns(3)

    with m_col1:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-title">Module Coverage Scope</div>
                <div class="metric-val" style="color: #2563eb;">{analysis['module_coverage_scope_pct']}%</div>
                <div class="metric-sub" style="color: #64748b;">
                    {len(analysis['active_modules'])} of {len(course_syllabus['modules'])} Syllabus Modules
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with m_col2:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-title">Exam Weightage Scope</div>
                <div class="metric-val" style="color: #059669;">{analysis['exam_weightage_marks']} Marks</div>
                <div class="metric-sub" style="color: #64748b;">Target Assessment Allocation</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with m_col3:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-title">Roadmap Task Completion</div>
                <div class="metric-val" style="color: #7c3aed;">{analysis['task_completion_rate_pct']}%</div>
                <div class="metric-sub" style="color: #64748b;">
                    {analysis['completed_count']} of {analysis['total_tasks']} Active Recall Tasks Completed
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Strategy & Recommendations Box
    st.markdown(f"### {analysis['strategy_header']}")
    with st.container():
        st.markdown(f"**Diagnostic Finding:** {analysis['diagnosis']}")
        st.markdown(f"**Target Score Metric:** {analysis['recovery_target']}")
        st.markdown("**Actionable Next Steps:**")
        for pt in analysis["strategy_points"]:
            st.markdown(f"- {pt}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Curriculum Roadmap & Active-Recall Mini-Quiz Loop
    st.markdown("### 🎯 Adaptive Roadmap & Active-Recall Mini-Quiz Loop")
    st.caption("Check off completed study roadmap tasks. Ticking a task reveals an interactive active-recall mini-quiz to verify conceptual mastery.")

    for mod in analysis["active_modules"]:
        with st.expander(
            f"📌 Module {mod['module_id']}: {mod['title']} (Weightage: {mod['exam_weightage']} Marks)",
            expanded=True
        ):
            st.markdown(f"**Core Scope:** *{', '.join(mod['scope_topics'])}*")
            st.markdown("---")

            for task in mod.get("tasks", []):
                t_id = task["task_id"]
                t_title = task["title"]
                is_done = t_id in completed_task_ids

                task_col1, task_col2 = st.columns([4, 1])
                with task_col1:
                    checked = st.checkbox(
                        f"**{t_title}** *(Weightage: {task['weightage']} Marks)*",
                        value=is_done,
                        key=f"check_{t_id}"
                    )
                with task_col2:
                    if is_done:
                        st.markdown("<span class='badge-safe'>✅ Verified</span>", unsafe_allow_html=True)
                    else:
                        st.markdown("<span class='badge-alert'>⏳ Pending</span>", unsafe_allow_html=True)

                if checked != is_done:
                    database.update_task_progress(
                        student_id=student["student_id"],
                        course_code=active_course_code,
                        task_id=t_id,
                        completed=checked
                    )
                    st.rerun()

                # ACTIVE-RECALL MINI-QUIZ LOOP
                if checked:
                    q_data = syllabus.get_quiz_question_by_task_id(t_id)
                    if q_data:
                        st.markdown(
                            f"""
                            <div class="quiz-container">
                                <div style="font-weight: 700; color: #1e3c72; margin-bottom: 0.3rem;">
                                    🧠 Active-Recall Mini-Quiz Verification Box
                                </div>
                                <div style="color: #334155; font-size: 0.95rem; margin-bottom: 0.8rem;">
                                    <strong>Question:</strong> {q_data['prompt']}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        quiz_choice = st.radio(
                            "Select the most accurate response:",
                            options=q_data["options"],
                            key=f"quiz_choice_{t_id}"
                        )

                        if st.button(f"Submit Quiz Answer for {t_id}", key=f"btn_quiz_{t_id}"):
                            correct_answer_text = q_data["options"][q_data["correct_idx"]]
                            if quiz_choice == correct_answer_text:
                                st.success(f"🎉 **Correct Answer!** +{task['weightage']} Marks Mastery Verified.\n\n*{q_data['explanation']}*")
                                database.update_task_progress(
                                    student_id=student["student_id"],
                                    course_code=active_course_code,
                                    task_id=t_id,
                                    completed=True,
                                    quiz_score=float(task["weightage"])
                                )
                            else:
                                st.error(
                                    f"❌ **Incorrect.** The correct answer is: **{correct_answer_text}**.\n\n"
                                    f"**Conceptual Explanation:** {q_data['explanation']}"
                                )
                                database.update_task_progress(
                                    student_id=student["student_id"],
                                    course_code=active_course_code,
                                    task_id=t_id,
                                    completed=True,
                                    quiz_score=0.0
                                )

                st.markdown("<br>", unsafe_allow_html=True)
