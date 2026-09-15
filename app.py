"""
app.py - Academic Student Portal Prototype
Built with Python and Streamlit.
Strictly adheres to:
1. Corporate UI Standards (Zero emojis, clean typography, executive layout).
2. Canonical Academic World Specification (Semester 5 - Fall 2026 Academic Session, Reference Date: Sept 10, 2026 - Week 8 of 14).
3. Authoritative database values and mathematical consistency (Zero fake fallbacks).
4. Dynamic student profiles & personas (Yuvasri Eswara 3rd Year vs A Jenita Roselin Onboarding).
5. Temporal Attendance Register (Conducted, Applicable, Attended, Absent, %, Safe Leaves, Needed Classes).
6. Dynamic Credit-Weighted Transcript & CGPA breakdown.
7. Flexible Assessment State Machine (PUBLISHED, UPCOMING, PENDING_EVALUATION, NOT_APPLICABLE, ABSENT).
8. Embedded AI Study Assistant with state-preserving Active-Recall Mini-Quiz loop.
9. Executive Navigation Buttons & System-wide Blue Transitions (Zero White Backgrounds on Hover/Selection).
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
# Page Configuration & Professional Corporate Theme Styling
# -------------------------------------------------------------
st.set_page_config(
    page_title="Academic Student Portal",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for executive corporate academic portal aesthetic with universal blue hover/selected transitions
st.markdown(
    """
    <style>
    /* 1. Main Page Layout */
    .main .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2.5rem;
        max-width: 96%;
    }
    
    /* 2. Top Dark Blue Header Card Banner */
    div[data-testid="stHorizontalBlock"]:has(.portal-header-marker) {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
        color: white !important;
        padding: 1.2rem 1.8rem !important;
        border-radius: 8px !important;
        margin-bottom: 1.5rem !important;
        border: 1px solid #334155 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06) !important;
        align-items: center !important;
    }

    /* 3. Popover +User Button Styling (Dark blue matching card, solid 2px white border, lighter blue on hover/selected) */
    html body div[data-testid="stPopover"] button,
    html body div[data-testid="stPopoverButton"] button,
    html body button[data-testid="stBaseButton-secondary"],
    div[data-testid="stPopover"] button,
    div[data-testid="stPopoverButton"] button,
    div[data-testid="stPopover"] > button {
        background-color: #0f172a !important;
        background: #0f172a !important;
        color: #ffffff !important;
        border: 2px solid #ffffff !important;
        border-radius: 6px !important;
        padding: 5px 16px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        transition: all 0.2s ease-in-out !important;
        box-shadow: none !important;
    }
    html body div[data-testid="stPopover"] button *,
    html body div[data-testid="stPopoverButton"] button *,
    html body button[data-testid="stBaseButton-secondary"] *,
    div[data-testid="stPopover"] button * {
        color: #ffffff !important;
    }
    html body div[data-testid="stPopover"] button:hover,
    html body div[data-testid="stPopover"] button:focus,
    html body div[data-testid="stPopover"] button:active,
    html body div[data-testid="stPopover"] button[aria-expanded="true"],
    html body div[data-testid="stPopoverButton"] button:hover,
    html body div[data-testid="stPopoverButton"] button[aria-expanded="true"],
    html body button[data-testid="stBaseButton-secondary"]:hover,
    html body button[data-testid="stBaseButton-secondary"][aria-expanded="true"],
    div[data-testid="stPopover"] button:hover,
    div[data-testid="stPopover"] button[aria-expanded="true"] {
        background-color: #2563eb !important; /* Lighter vibrant blue */
        background: #2563eb !important;
        color: #ffffff !important;
        border: 2px solid #60a5fa !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.45) !important;
    }
    html body div[data-testid="stPopover"] button:hover *,
    html body div[data-testid="stPopover"] button[aria-expanded="true"] * {
        color: #ffffff !important;
    }

    /* 4. Streamlined Horizontal Tabs (Universal Blue Selection/Hover - Zero White Backgrounds) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 2px solid #cbd5e1;
        margin-bottom: 1.2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        white-space: pre;
        border-radius: 6px 6px 0px 0px;
        padding-left: 18px;
        padding-right: 18px;
        font-weight: 600;
        font-size: 0.92rem;
        color: #334155;
        background-color: #f1f5f9;
        border: 1px solid #cbd5e1;
        border-bottom: none;
        transition: all 0.2s ease-in-out;
    }
    /* Unselected tab hover -> soft light blue */
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #dbeafe !important;
        color: #1d4ed8 !important;
        border-color: #93c5fd !important;
    }
    /* Active selected tab -> Dark blue */
    .stTabs [aria-selected="true"] {
        background-color: #0f172a !important;
        color: #ffffff !important;
        border-color: #0f172a !important;
    }
    /* Active selected tab hover -> Lighter vibrant blue (NEVER white) */
    .stTabs [aria-selected="true"]:hover {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border-color: #60a5fa !important;
    }

    /* 5. Sidebar Navigation Links & Button States */
    section[data-testid="stSidebar"] {
        background-color: #0f172a;
        color: #f8fafc;
    }
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stCaption {
        color: #cbd5e1 !important;
    }

    section[data-testid="stSidebar"] div.stButton > button {
        background-color: #1e293b !important;
        color: #cbd5e1 !important;
        border: 1px solid #334155 !important;
        border-radius: 6px !important;
        padding: 10px 14px !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        text-align: left !important;
        justify-content: flex-start !important;
        transition: all 0.2s ease-in-out !important;
        margin-bottom: 4px !important;
        width: 100% !important;
    }
    /* Inactive button hover -> Lighter royal blue */
    section[data-testid="stSidebar"] div.stButton > button:hover {
        background-color: #1e3a8a !important;
        color: #ffffff !important;
        border-color: #3b82f6 !important;
        transform: translateX(2px);
    }
    /* Active button -> Vibrant blue */
    section[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border-color: #60a5fa !important;
        font-weight: 600 !important;
        box-shadow: 0 3px 8px rgba(37,99,235,0.35) !important;
    }
    /* Active button hover -> Slightly lighter vibrant blue (NEVER white) */
    section[data-testid="stSidebar"] div.stButton > button[kind="primary"]:hover {
        background-color: #3b82f6 !important;
        color: #ffffff !important;
        border-color: #93c5fd !important;
    }

    /* 6. Primary Action Buttons & Submits Across the App */
    div.stButton > button[kind="primary"],
    button[data-testid="stFormSubmitButton"] {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border: 1px solid #3b82f6 !important;
        transition: all 0.2s ease-in-out !important;
    }
    div.stButton > button[kind="primary"]:hover,
    div.stButton > button[kind="primary"]:focus,
    div.stButton > button[kind="primary"]:active,
    button[data-testid="stFormSubmitButton"]:hover,
    button[data-testid="stFormSubmitButton"]:focus {
        background-color: #1d4ed8 !important; /* Lighter royal blue on hover */
        color: #ffffff !important;
        border-color: #60a5fa !important;
        box-shadow: 0 4px 12px rgba(37,99,235,0.4) !important;
    }

    /* 7. IoT Status Badge Styling */
    .status-badge-iot {
        background-color: #064e3b;
        color: #6ee7b7;
        border: 1px solid #059669;
        padding: 0.35rem 0.75rem;
        border-radius: 6px;
        font-size: 0.82rem;
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

    /* 8. Metric Cards & Cards */
    .metric-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-box:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 14px rgba(0,0,0,0.06);
    }
    .metric-title {
        font-size: 0.82rem;
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
        color: #9f1239;
        border: 1px solid #fecaca;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.82rem;
    }
    .badge-safe {
        background-color: #f0fdf4;
        color: #166534;
        border: 1px solid #bbf7d0;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.82rem;
    }
    .badge-pending {
        background-color: #fefce8;
        color: #854d0e;
        border: 1px solid #fef08a;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.82rem;
    }

    .card-proctor {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-left: 4px solid #2563eb;
        border-radius: 6px;
        padding: 1.2rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .card-spotlight {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-left: 4px solid #d97706;
        border-radius: 6px;
        padding: 1.2rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }

    .quiz-container {
        background: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 1.2rem;
        margin-top: 0.8rem;
    }

    .sidebar-header {
        padding: 0.5rem 0 0.8rem 0;
        border-bottom: 1px solid #334155;
        margin-bottom: 1rem;
    }
    .sidebar-header h3 {
        color: #ffffff !important;
        margin: 0;
        font-size: 1.15rem;
        font-weight: 700;
    }
    .sidebar-header p {
        color: #94a3b8 !important;
        margin: 0.2rem 0 0 0;
        font-size: 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------------------
# Database Bootstrap & Timeline Init
# -------------------------------------------------------------
database.init_db(force_reseed=False)
timeline = database.get_academic_timeline()

# -------------------------------------------------------------
# Functional Corporate Sidebar (Primary Navigation Tool)
# -------------------------------------------------------------
st.sidebar.markdown(
    f"""
    <div class="sidebar-header">
        <h3>ACADEMIC STUDENT PORTAL</h3>
        <p>{timeline['term_name']}<br>Week {timeline['current_week']} of {timeline['total_weeks']}</p>
    </div>
    """,
    unsafe_allow_html=True
)

# 1. Profile Switcher (Personas)
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

st.sidebar.markdown("**ACTIVE STUDENT PROFILE**")
selected_profile_name = st.sidebar.selectbox(
    "Active Student Profile",
    options=list(profile_map.keys()),
    index=list(profile_map.keys()).index(current_display_name),
    label_visibility="collapsed"
)

active_student_id = profile_map[selected_profile_name]
if active_student_id != st.session_state.current_student_id:
    st.session_state.current_student_id = active_student_id
    st.rerun()

st.sidebar.markdown("<br>", unsafe_allow_html=True)

# 2. Biometric Reference Profile Expander
current_photo_bytes = database.get_student_photo_bytes(st.session_state.current_student_id)
with st.sidebar.expander("Biometric Reference Photo", expanded=False):
    st.image(current_photo_bytes, caption=f"Enrolled: {selected_profile_name}", use_container_width=True)
    st.markdown(
        """
        <div style="font-size:0.75rem; color:#15803d; background:#f0fdf4; border:1px solid #bbf7d0; border-radius:4px; padding:4px; text-align:center; margin-top:4px;">
            Verified Reference in Database
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.caption("Update Reference Photo")
    up_opt = st.radio("Source:", ["Webcam Snap", "File Upload"], key="sidebar_photo_up_opt", horizontal=True)
    if up_opt == "Webcam Snap":
        side_snap = st.camera_input("Snap Reference", key="side_cam_snap")
        if side_snap and st.button("Save New Reference", key="side_save_snap_btn"):
            database.update_student_photo(st.session_state.current_student_id, side_snap.getvalue())
            st.success("Reference photo updated.")
            st.rerun()
    else:
        side_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"], key="side_file_snap")
        if side_file and st.button("Save New Reference", key="side_save_file_btn"):
            database.update_student_photo(st.session_state.current_student_id, side_file.getvalue())
            st.success("Reference photo updated.")
            st.rerun()

# 3. System Status Indicator
st.sidebar.markdown(
    """
    <div style="margin: 0.6rem 0 1.0rem 0;">
        <span class="status-badge-iot">
            <span class="pulse-dot"></span> IoT Node Status: Connected
        </span>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("---")

# 4. Primary Navigation Buttons (Pure Button Navigation - Zero Radio Circles/Dots)
portal_menu = [
    "Student Dashboard",
    "Course Attendance Register",
    "Examinations & Internal Marks",
    "Academic Performance & Study Assistant"
]

if "nav_choice" not in st.session_state or st.session_state.nav_choice not in portal_menu:
    st.session_state.nav_choice = portal_menu[0]

for nav_item in portal_menu:
    is_active = (st.session_state.nav_choice == nav_item)
    btn_type = "primary" if is_active else "secondary"
    if st.sidebar.button(nav_item, key=f"nav_btn_{nav_item}", type=btn_type, use_container_width=True):
        st.session_state.nav_choice = nav_item
        st.rerun()

selected_nav = st.session_state.nav_choice

st.sidebar.markdown("---")

# 5. System Administration Drawer
with st.sidebar.expander("System Administration Controls", expanded=False):
    st.caption("Database Controls & Environment State Management")
    if st.button("Reset Data State"):
        database.init_db(force_reseed=True)
        st.session_state.current_student_id = "21BCE1001"
        st.session_state.nav_choice = "Student Dashboard"
        st.success("Academic database restored to default state.")
        st.rerun()

# Fetch active student details dynamically
student = database.get_student_by_id(st.session_state.current_student_id)
if not student:
    st.session_state.current_student_id = student_profiles[0]["student_id"]
    student = database.get_student_by_id(st.session_state.current_student_id)

student_photo_bytes = database.get_student_photo_bytes(student["student_id"])

# -------------------------------------------------------------
# Global Dark Blue Header Card Enclosing Title, IoT Badge, and +User Popover
# -------------------------------------------------------------
header_container = st.container()

with header_container:
    h_col1, h_col2 = st.columns([5, 2])
    with h_col1:
        st.markdown(
            f"""
            <div class="portal-header-marker">
                <h2 style="color: #ffffff !important; margin: 0; font-size: 1.6rem; font-weight: 700; letter-spacing: -0.5px;">Academic Student Portal</h2>
                <p style="color: #94a3b8 !important; margin: 0.25rem 0 0 0; font-size: 0.9rem;">
                    <strong>Active Student:</strong> {student['name']} &nbsp;|&nbsp; 
                    <strong>Reg No:</strong> {student['student_id']} &nbsp;|&nbsp; 
                    <strong>Term:</strong> {timeline['term_name']} (Week {timeline['current_week']} of {timeline['total_weeks']})
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with h_col2:
        h_sub1, h_sub2 = st.columns([1, 1])
        with h_sub1:
            st.markdown(
                """
                <span class="status-badge-iot" style="margin-top: 4px;">
                    <span class="pulse-dot"></span> IoT Connected
                </span>
                """,
                unsafe_allow_html=True
            )
        with h_sub2:
            with st.popover("+ User", help="Enroll New Student (Pop-Up Onboarding Bubble)", use_container_width=True):
                st.markdown("### Enroll New Student")
                st.caption("Quickly register a new student baseline profile.")

                with st.form("form_register_student_header_popover", clear_on_submit=False):
                    pop_name = st.text_input("Full Student Name *", placeholder="e.g. A Jenita Roselin")
                    pop_id = st.text_input("Registration Number *", placeholder="e.g. 24BLC1033")
                    pop_proctor = st.text_area(
                        "Faculty Advisory Note",
                        value="Welcome to the academic semester! Maintain continuous attendance above 75% once classes commence.",
                        height=80
                    )

                    st.markdown("**Baseline Photo Source:**")
                    pop_enroll_mode = st.radio(
                        "Source Mode:",
                        ["Webcam Snap", "File Upload", "System Avatar"],
                        index=0,
                        key="pop_photo_mode_header",
                        horizontal=True
                    )

                    pop_snapped = None
                    pop_uploaded = None
                    if pop_enroll_mode == "Webcam Snap":
                        pop_snapped = st.camera_input("Snap Photo", key="pop_cam_enroll_hdr")
                    elif pop_enroll_mode == "File Upload":
                        pop_uploaded = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], key="pop_file_enroll_hdr")

                    btn_pop_submit = st.form_submit_button("Register & Enroll", type="primary", use_container_width=True)

                    if btn_pop_submit:
                        if not pop_name.strip() or not pop_id.strip():
                            st.error("Please fill Name and Registration Number.")
                        else:
                            existing_check = database.get_student_by_id(pop_id.strip().upper())
                            if existing_check:
                                st.error(f"Student ID '{pop_id.strip().upper()}' already exists.")
                            else:
                                ref_photo_bytes = None
                                if pop_snapped is not None:
                                    ref_photo_bytes = pop_snapped.getvalue()
                                elif pop_uploaded is not None:
                                    ref_photo_bytes = pop_uploaded.getvalue()
                                else:
                                    ref_photo_bytes = biometrics.generate_default_avatar(pop_name.strip())

                                database.create_student(
                                    student_id=pop_id.strip().upper(),
                                    name=pop_name.strip(),
                                    proctor_message=pop_proctor.strip(),
                                    photo_bytes=ref_photo_bytes
                                )
                                st.session_state.current_student_id = pop_id.strip().upper()
                                st.session_state.nav_choice = "Student Dashboard"
                                st.success(f"Enrolled {pop_name.strip()} ({pop_id.strip().upper()}).")
                                st.rerun()


# =============================================================
# MODULE 1: STUDENT DASHBOARD
# =============================================================
if selected_nav == "Student Dashboard":
    st.subheader("Student Dashboard")

    attendance_records = database.get_student_attendance(student["student_id"])
    total_attended = sum(a["classes_attended"] for a in attendance_records)
    total_applicable = sum(a["classes_applicable"] for a in attendance_records)

    tab_dash_overview, tab_dash_transcript, tab_dash_catalog = st.tabs([
        "Executive Overview",
        "Academic Transcript",
        "Registered Course Catalog"
    ])

    with tab_dash_overview:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if total_applicable == 0:
                st.markdown(
                    """
                    <div class="metric-box">
                        <div class="metric-title">Overall Attendance</div>
                        <div class="metric-val" style="color: #64748b;">—</div>
                        <div class="metric-sub" style="color: #64748b;">No classes recorded since enrollment</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                overall_att_pct = database.calculate_overall_attendance([(a["classes_attended"], a["classes_applicable"]) for a in attendance_records])
                shortage_count = sum(1 for a in attendance_records if a["status_type"] == "SHORTAGE")
                safe_count = sum(1 for a in attendance_records if a["status_type"] == "SAFE")
                
                att_color = "#15803d" if overall_att_pct >= 80.0 else "#b91c1c"
                sub_text = f"{safe_count} courses safe · {shortage_count} courses require attention"
                st.markdown(
                    f"""
                    <div class="metric-box">
                        <div class="metric-title">Overall Attendance</div>
                        <div class="metric-val" style="color: {att_color};">{overall_att_pct}%</div>
                        <div class="metric-sub" style="color: {att_color};">{sub_text} ({total_attended}/{total_applicable})</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        with col2:
            if student["cgpa"] is None:
                st.markdown(
                    """
                    <div class="metric-box">
                        <div class="metric-title">Cumulative GPA</div>
                        <div class="metric-val" style="color: #64748b;">—</div>
                        <div class="metric-sub" style="color: #64748b;">No semester results published yet</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                cgpa_val = student["cgpa"]
                cgpa_color = "#0f172a" if cgpa_val >= 8.5 else "#d97706"
                st.markdown(
                    f"""
                    <div class="metric-box">
                        <div class="metric-title">Cumulative GPA</div>
                        <div class="metric-val" style="color: {cgpa_color};">{cgpa_val:.2f}</div>
                        <div class="metric-sub" style="color: #64748b;">Scale: 10.00 Max (Derived)</div>
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
                    <div class="metric-val" style="color: #2563eb;">{len(attendance_records)}</div>
                    <div class="metric-sub" style="color: #64748b;">Fall Semester 2026 (Week {timeline['current_week']})</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        dash_col_photo, dash_col_info = st.columns([1, 2])

        with dash_col_photo:
            st.markdown("### Biometric Digital ID Card")
            st.image(student_photo_bytes, caption=f"Official Reference Photo: {student['name']}", use_container_width=True)

        with dash_col_info:
            st.markdown("### Spotlight Announcements & Faculty Advisory")
            st.markdown(
                f"""
                <div class="card-spotlight">
                    <div style="font-weight: 700; color: #b45309; margin-bottom: 0.4rem; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 0.5px;">
                        University Bulletin & Placement Alerts
                    </div>
                    <div style="color: #334155; line-height: 1.5; font-size: 0.95rem;">
                        {student['spotlight_news']}
                    </div>
                    <div style="margin-top: 0.8rem; font-size: 0.8rem; color: #64748b;">
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
                    <div style="font-weight: 700; color: #1d4ed8; margin-bottom: 0.4rem; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 0.5px;">
                        Official Communication from Assigned Faculty Proctor
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

    with tab_dash_transcript:
        st.markdown("### Academic Transcript & CGPA Progression")
        st.caption("Credit-weighted semester performance history and cumulative grade point average.")
        transcript_records = database.get_student_transcript(student["student_id"])

        if transcript_records:
            t_rows = []
            for t in transcript_records:
                t_rows.append({
                    "Semester": t["semester"],
                    "Credits Earned": t["credits"],
                    "GPA": f"{t['gpa']:.2f}"
                })
            if student["cgpa"] is not None:
                t_rows.append({
                    "Semester": f"{timeline['term_name']} (Current)",
                    "Credits Earned": 19,
                    "GPA": f"{student['cgpa']:.2f} (Provisional)"
                })
            df_transcript = pd.DataFrame(t_rows)
            st.dataframe(df_transcript, use_container_width=True, hide_index=True)
        else:
            st.info("Newly Enrolled Student: No prior semester transcript records found. Attendance and assessment records will accumulate dynamically as classes are recorded.")

    with tab_dash_catalog:
        st.markdown("### Registered Course Catalog")
        st.caption("Currently enrolled course list and current attendance standing.")
        catalog_rows = []
        for a in attendance_records:
            pct_str = f"{a['percentage']}%" if a['percentage'] is not None else "—"
            catalog_rows.append({
                "Course Code": a["course_code"],
                "Course Title": a["course_title"],
                "Type": a["course_type"],
                "Faculty": a["faculty_name"],
                "Attendance": pct_str,
                "Status": a["status_remark"]
            })
        df_courses = pd.DataFrame(catalog_rows)
        st.dataframe(df_courses, use_container_width=True, hide_index=True)


# =============================================================
# MODULE 2: COURSE ATTENDANCE PORTAL
# =============================================================
elif selected_nav == "Course Attendance Register":
    st.subheader("Course Attendance Register")
    st.caption(f"Official Class Attendance Register for {timeline['term_name']} (Week {timeline['current_week']} of {timeline['total_weeks']}).")

    attendance_records = database.get_student_attendance(student["student_id"])

    tab_att_summary, tab_att_biometric, tab_att_logs = st.tabs([
        "Attendance Register & Compliance",
        "IoT Biometric Check-In",
        "Day-Wise Audit Logs"
    ])

    with tab_att_summary:
        shortage_courses = [a for a in attendance_records if a["status_type"] == "SHORTAGE"]
        if shortage_courses:
            st.error(
                f"Attendance Shortage Warning: You have **{len(shortage_courses)}** course(s) below the mandatory 75% threshold: "
                + ", ".join([f"**{c['course_code']} ({c['percentage']}%)**" for c in shortage_courses])
                + ". Minimum 75% attendance is strictly enforced for final exam eligibility."
            )
        elif all(a["status_type"] == "NEWLY_ENROLLED" for a in attendance_records):
            st.info("Newly Enrolled Student: No classes recorded since enrollment. Classes conducted prior to enrollment are excluded from your record.")
        else:
            st.success("Attendance Compliant: All registered courses meet or exceed the mandatory 75% threshold.")

        table_rows = []
        for idx, item in enumerate(attendance_records, start=1):
            pct_str = f"{item['percentage']:.1f}%" if item["percentage"] is not None else "—"
            table_rows.append({
                "#": idx,
                "Course Code & Title": f"{item['course_code']} - {item['course_title']}",
                "Course Type": item["course_type"],
                "Faculty Name": item["faculty_name"],
                "Attended": item["classes_attended"],
                "Applicable": item["classes_applicable"],
                "Conducted": item["classes_conducted"],
                "Percentage": pct_str,
                "Status / Remarks": item["status_remark"]
            })

        df_attendance = pd.DataFrame(table_rows)

        def highlight_attendance(row):
            pct_val = row["Percentage"]
            if pct_val != "—" and float(str(pct_val).replace("%", "")) < 75.0:
                return ["background-color: #fff1f2; color: #9f1239; font-weight: bold"] * len(row)
            return [""] * len(row)

        styled_df = df_attendance.style.apply(highlight_attendance, axis=1)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

    with tab_att_biometric:
        st.markdown("### Biometric Face-Match Verification (IoT Node)")
        st.caption("Validates live frame against student's enrolled reference photo before granting attendance.")

        ref_card_col1, ref_card_col2 = st.columns([1, 2])
        with ref_card_col1:
            st.image(student_photo_bytes, caption="Enrolled Reference", width=120)
        with ref_card_col2:
            st.markdown(
                f"""
                <div style="background:#f0fdf4; border:1px solid #86efac; border-radius:6px; padding:10px; margin-top:5px;">
                    <div style="font-weight:700; color:#166534; font-size:0.85rem;">
                        Verified Reference in Database
                    </div>
                    <div style="font-size:0.8rem; color:#15803d; margin-top:2px;">
                        <strong>Student:</strong> {student['name']}<br>
                        <strong>Reg No:</strong> {student['student_id']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("---")

        course_options = {f"{a['course_code']} - {a['course_title']}": a["course_code"] for a in attendance_records}
        target_course_code = list(course_options.values())[0] if course_options else None

        if course_options:
            selected_course_label = st.selectbox("Select Course for Check-In:", options=list(course_options.keys()), key="face_match_course")
            target_course_code = course_options[selected_course_label]

        iot_mode = st.radio(
            "Select IoT Verification Camera Mode:",
            [
                "DroidCam Phone IoT Node (Rotate 90° Upright)",
                "In-Browser Camera Input (Webcam)",
                "Quick Biometric Simulation (Testing Mode)"
            ],
            index=0,
            key="iot_camera_mode"
        )

        if target_course_code:
            if iot_mode == "DroidCam Phone IoT Node (Rotate 90° Upright)":
                col_ip, col_port = st.columns([3, 1])
                with col_ip:
                    droid_ip = st.text_input("IoT Phone IP Address:", value="192.168.0.3", key="droid_ip")
                with col_port:
                    droid_port = st.number_input("Port:", value=4747, step=1, key="droid_port")

                orient_option = st.selectbox(
                    "Camera Orientation Alignment:",
                    ["Rotate 90° Upright (PIL ROTATE_270)", "Normal (0° Landscape)", "Rotate 180° Inverted"],
                    index=0
                )

                show_viewfinder = st.checkbox("Show Continuous Video Viewfinder", value=False)
                if show_viewfinder:
                    st.markdown(
                        f"""
                        <div style="background:#0f172a; padding:10px; border-radius:8px; text-align:center; border:1px solid #334155; max-width:270px; margin:0 auto 12px auto;">
                            <div style="font-size:0.75rem; color:#10b981; font-weight:700; margin-bottom:6px;">LIVE IOT STREAM</div>
                            <img src="http://{droid_ip}:{droid_port}/video" style="width:100%; height:340px; border-radius:6px; object-fit:cover;" onerror="this.onerror=null; this.src='https://placehold.co/270x340/0f172a/ef4444?text=Camera+Offline';" />
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                if st.button("Capture & Verify Face from Phone Camera", type="primary", use_container_width=True, key="btn_droid_snap"):
                    with st.spinner("Pulling live biometric frame..."):
                        live_frame_bytes = fetch_droidcam_frame(ip=droid_ip, port=int(droid_port), timeout=4)
                        if live_frame_bytes:
                            rot_deg = 90 if "90°" in orient_option else (180 if "180°" in orient_option else 0)
                            upright_bytes = biometrics.rotate_image(live_frame_bytes, rotation_degrees=rot_deg)
                            portrait_live_bytes = biometrics.crop_to_portrait(upright_bytes)

                            match_result = biometrics.compare_biometrics(
                                reference_bytes=student_photo_bytes,
                                captured_bytes=portrait_live_bytes,
                                threshold=50.0
                            )

                            comp_c1, comp_c2 = st.columns(2)
                            with comp_c1:
                                st.image(student_photo_bytes, caption="Enrolled Reference ID", use_container_width=True)
                            with comp_c2:
                                st.image(portrait_live_bytes, caption="Live IoT Capture (Upright)", use_container_width=True)

                            conf = match_result["confidence_pct"]
                            st.metric("Biometric Match Confidence", f"{conf:.1f}%", delta="Verified" if match_result["is_match"] else "Mismatch")

                            if match_result["is_match"]:
                                result = database.record_face_match_attendance(
                                    student["student_id"],
                                    target_course_code,
                                    device_name=f"IoT Phone Camera ({droid_ip}:{droid_port})",
                                    confidence_pct=conf,
                                    image_bytes=portrait_live_bytes
                                )
                                st.success(f"Biometric Verification Confirmed ({conf:.1f}%). Attendance recorded for {result['course_code']} (Attended: {result['attended']}/{result['total']}).")
                                st.rerun()
                        else:
                            st.error("Could not pull frame from DroidCam stream. Ensure phone and PC are on the same Wi-Fi network.")

            elif iot_mode == "In-Browser Camera Input (Webcam)":
                cam_photo = st.camera_input("Scan Face via Camera", key="iot_camera_feed")
                if cam_photo is not None:
                    live_bytes = cam_photo.getvalue()
                    portrait_live_bytes = biometrics.crop_to_portrait(live_bytes)
                    match_result = biometrics.compare_biometrics(
                        reference_bytes=student_photo_bytes,
                        captured_bytes=portrait_live_bytes,
                        threshold=50.0
                    )

                    comp_c1, comp_c2 = st.columns(2)
                    with comp_c1:
                        st.image(student_photo_bytes, caption="Enrolled Reference ID", use_container_width=True)
                    with comp_c2:
                        st.image(portrait_live_bytes, caption="Live Camera Portrait Snapshot", use_container_width=True)

                    conf = match_result["confidence_pct"]
                    if match_result["is_match"]:
                        if st.button("Confirm & Commit Biometric Attendance", type="primary", use_container_width=True):
                            result = database.record_face_match_attendance(
                                student["student_id"],
                                target_course_code,
                                device_name="IoT In-Browser Camera Node",
                                confidence_pct=conf,
                                image_bytes=portrait_live_bytes
                            )
                            st.success(f"Biometric verification confirmed for {result['course_code']}.")
                            st.rerun()

            else:
                if st.button("Trigger Biometric Verification", type="primary", use_container_width=True, key="btn_sim_face"):
                    result = database.record_face_match_attendance(
                        student["student_id"],
                        target_course_code,
                        device_name="IoT Edge Sensor Node #01",
                        confidence_pct=99.4,
                        image_bytes=student_photo_bytes
                    )
                    st.success(f"Biometric verification confirmed for {result['course_code']} (Attended: {result['attended']}/{result['total']}).")
                    st.rerun()

    with tab_att_logs:
        st.markdown("### Day-Wise Attendance Log Drill-Down")
        st.caption("Historical verification timestamps and method audit trail for enrolled courses.")
        if course_options:
            drill_course_label = st.selectbox("Select Course for Detailed Day-Wise Log:", options=list(course_options.keys()), key="drill_down_course")
            drill_course_code = course_options[drill_course_label]
            logs = database.get_attendance_logs(student["student_id"], drill_course_code)

            if logs:
                df_logs = pd.DataFrame([
                    {
                        "Date": log["date"],
                        "Time Slot": log["time_slot"],
                        "Status": log["status"],
                        "Verification Method": log["verification_method"],
                        "Recorded At": log["timestamp"]
                    }
                    for log in logs
                ])
                st.dataframe(df_logs, use_container_width=True, hide_index=True)
            else:
                st.info(f"No prior day-wise logs recorded yet for {drill_course_code}. Perform a face match check-in to generate live entries.")


# =============================================================
# MODULE 3: EXAM & MARKS PORTAL
# =============================================================
elif selected_nav == "Examinations & Internal Marks":
    st.subheader("Internal Assessment & Examination Portal")
    st.caption("Realistic assessment timeline with dynamic state machine statuses.")

    assessments = database.get_student_assessments(student["student_id"])

    tab_marks_grid, tab_marks_analytics = st.tabs([
        "Assessment Marks Grid",
        "Performance Trajectory Analytics"
    ])

    with tab_marks_grid:
        if assessments:
            marks_rows = []
            for m in assessments:
                if m["status"] == "PUBLISHED":
                    achieved_str = f"{m['achieved_marks']:.1f} / {m['max_marks']:.0f}"
                    status_str = "Published"
                elif m["status"] == "UPCOMING":
                    achieved_str = f"— / {m['max_marks']:.0f}"
                    status_str = "Upcoming"
                elif m["status"] == "NOT_APPLICABLE":
                    achieved_str = "—"
                    status_str = "Not Applicable (Enrolled Post-Assessment)"
                else:
                    achieved_str = f"— / {m['max_marks']:.0f}"
                    status_str = "Pending Evaluation"

                marks_rows.append({
                    "Course Code": m["course_code"],
                    "Course Title": m["course_title"],
                    "Assessment Name": m["name"],
                    "Assessment Type": m["type"],
                    "Scheduled Date": m["date"],
                    "Marks Achieved": achieved_str,
                    "Status": status_str
                })

            df_marks = pd.DataFrame(marks_rows)
            st.dataframe(df_marks, use_container_width=True, hide_index=True)
        else:
            st.info("No assessment records found.")

    with tab_marks_analytics:
        published_marks = [m for m in assessments if m["status"] == "PUBLISHED"]
        if published_marks:
            st.markdown("### Subject Performance Breakdown & Trajectory")
            st.caption("Comparative assessment trends against academic benchmarks.")
            evaluated_courses = sorted(list(set(m["course_code"] for m in published_marks)))
            course_code_sel = st.selectbox("Select Subject for Performance Trajectory:", options=evaluated_courses)

            course_published = [m for m in published_marks if m["course_code"] == course_code_sel]
            chart_data = []
            for m in course_published:
                norm_pct = (m["achieved_marks"] / m["max_marks"]) * 100.0
                chart_data.append({
                    "Assessment": m["name"],
                    "Score Achieved": m["achieved_marks"],
                    "Max Marks": m["max_marks"],
                    "Normalized Percentage": round(norm_pct, 1)
                })

            if chart_data:
                df_chart = pd.DataFrame(chart_data)
                line = alt.Chart(df_chart).mark_line(point=alt.OverlayMarkDef(size=80, filled=True), color="#1e293b", strokeWidth=3).encode(
                    x=alt.X("Assessment:N", sort=None, title="Assessment Component"),
                    y=alt.Y("Normalized Percentage:Q", title="Score (%)", scale=alt.Scale(domain=[0, 105])),
                    tooltip=["Assessment", "Score Achieved", "Max Marks", "Normalized Percentage"]
                )
                bench_rule = alt.Chart(pd.DataFrame([{"y": 75, "label": "Passing Benchmark (75%)"}, {"y": 90, "label": "Excellence Target (90%)"}])).mark_rule(
                    strokeDash=[5, 5], color="#10b981", opacity=0.7
                ).encode(y="y:Q")

                final_chart = (line + bench_rule).properties(
                    title=f"Assessment Performance Trajectory - {course_code_sel}",
                    height=340
                )
                st.altair_chart(final_chart, use_container_width=True)
        else:
            st.info("Newly Enrolled Student: No published internal assessment scores available yet.")


# =============================================================
# MODULE 4: AI STUDY ASSISTANT & QUIZ
# =============================================================
elif selected_nav == "Academic Performance & Study Assistant":
    st.subheader("Academic Performance & Study Assistant")
    st.caption("Embedded pedagogical study assistant providing structured topic roadmaps and verified active-recall practice.")

    courses = database.get_student_attendance(student["student_id"])
    course_opts = {f"{c['course_code']} - {c['course_title']}": c["course_code"] for c in courses}

    if not course_opts:
        st.warning("No courses enrolled for this student.")
        st.stop()

    col_subj, col_exam = st.columns([1, 1])
    with col_subj:
        selected_subj_label = st.selectbox("Select Enrolled Subject:", options=list(course_opts.keys()), key="ai_subj_selector")
        active_course_code = course_opts[selected_subj_label]

    with col_exam:
        target_exam = st.selectbox(
            "Select Target Examination:",
            ["Finals (FAT - Comprehensive Examination)", "Mid-2 (Internal Assessment 2)", "Mid-1 (Internal Assessment 1)"],
            key="ai_exam_selector"
        )

    course_syllabus = syllabus.get_course_syllabus(active_course_code)
    if not course_syllabus:
        st.warning(f"Syllabus structure not mapped for {active_course_code}.")
        st.stop()

    saved_progress = database.get_task_progress(student["student_id"], active_course_code)
    completed_task_ids = [tid for tid, rec in saved_progress.items() if rec.get("completed") == 1]

    if "quiz_state" not in st.session_state:
        st.session_state.quiz_state = {}

    analysis = ai_engine.analyze_student_roadmap(
        student_profile=student,
        course_code=active_course_code,
        target_exam=target_exam,
        marks_record=None,
        syllabus_data=course_syllabus,
        completed_task_ids=completed_task_ids
    )

    tab_ai_strategy, tab_ai_roadmap, tab_ai_quiz = st.tabs([
        "Strategy & Diagnostics",
        "Adaptive Study Roadmap",
        "Active-Recall Practice"
    ])

    with tab_ai_strategy:
        st.info(f"**{analysis['condition_badge']}**\n\n{analysis['condition_summary']}")

        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.markdown(
                f"""
                <div class="metric-box">
                    <div class="metric-title">Module Coverage Scope</div>
                    <div class="metric-val" style="color: #2563eb;">{analysis['module_coverage_scope_pct']}%</div>
                    <div class="metric-sub" style="color: #64748b;">{len(analysis['active_modules'])} of {len(course_syllabus['modules'])} Modules</div>
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
                    <div class="metric-sub" style="color: #64748b;">Target Allocation</div>
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
                    <div class="metric-sub" style="color: #64748b;">{analysis['completed_count']} of {analysis['total_tasks']} Tasks Completed</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(f"### {analysis['strategy_header']}")
        st.markdown(f"**Diagnostic Finding:** {analysis['diagnosis']}")
        st.markdown(f"**Target Metric:** {analysis['recovery_target']}")
        st.markdown("**Actionable Next Steps:**")
        for pt in analysis["strategy_points"]:
            st.markdown(f"- {pt}")

    with tab_ai_roadmap:
        st.markdown("### Adaptive Study Roadmap & Task Checklists")
        st.caption("Check off completed study tasks to track progress and unlock interactive active-recall mini-quizzes.")

        for mod in analysis["active_modules"]:
            with st.expander(f"Module {mod['module_id']}: {mod['title']} (Weightage: {mod['exam_weightage']} Marks)", expanded=True):
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
                            st.markdown("<span class='badge-safe'>Verified</span>", unsafe_allow_html=True)
                        else:
                            st.markdown("<span class='badge-pending'>Pending</span>", unsafe_allow_html=True)

                    if checked != is_done:
                        database.update_task_progress(student["student_id"], active_course_code, t_id, checked)
                        st.rerun()

    with tab_ai_quiz:
        st.markdown("### Active-Recall Practice & Mastery Verification")
        st.caption("Interactive mini-quizzes for verified study topics to ensure conceptual mastery.")

        completed_tasks_list = []
        for mod in analysis["active_modules"]:
            for task in mod.get("tasks", []):
                if task["task_id"] in completed_task_ids:
                    completed_tasks_list.append(task)

        if not completed_tasks_list:
            st.info("No study tasks verified yet. Switch to the 'Adaptive Study Roadmap' tab and check off completed tasks to unlock active-recall practice quizzes.")
        else:
            for task in completed_tasks_list:
                t_id = task["task_id"]
                t_title = task["title"]
                q_data = syllabus.get_quiz_question_by_task_id(t_id)

                if q_data:
                    with st.expander(f"Quiz: {t_title} (Weightage: {task['weightage']} Marks)", expanded=True):
                        st.markdown(
                            f"""
                            <div class="quiz-container">
                                <div style="font-weight: 700; color: #0f172a; margin-bottom: 0.3rem;">
                                    Active-Recall Quick Check
                                </div>
                                <div style="color: #334155; font-size: 0.95rem; margin-bottom: 0.8rem;">
                                    <strong>Question:</strong> {q_data['prompt']}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        quiz_choice_key = f"quiz_choice_{t_id}"
                        quiz_choice = st.radio(
                            "Select your response:",
                            options=q_data["options"],
                            key=quiz_choice_key
                        )

                        if st.button(f"Submit Quiz Answer", key=f"btn_quiz_{t_id}"):
                            st.session_state.quiz_state[t_id] = quiz_choice
                            correct_text = q_data["options"][q_data["correct_idx"]]
                            if quiz_choice == correct_text:
                                st.success(f"Correct Answer. +{task['weightage']} Marks Mastery Verified.\n\n*{q_data['explanation']}*")
                                database.update_task_progress(student["student_id"], active_course_code, t_id, True, float(task["weightage"]))
                            else:
                                st.error(f"Incorrect. Correct answer: **{correct_text}**.\n\n**Explanation:** {q_data['explanation']}")
                                database.update_task_progress(student["student_id"], active_course_code, t_id, True, 0.0)
