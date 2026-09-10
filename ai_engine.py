"""
ai_engine.py - AI Personalized Learning & Study Roadmap Engine
Provides:
1. Production-ready Amazon Bedrock boto3 integration hooks with graceful local fallback.
2. High-performance deterministic local pedagogical intelligence engine:
   - Mid-1 Completed only: Retrospective remedial recovery plan (Modules 1 & 2).
   - Mid-1 & Mid-2 Completed: Comparative trend analysis & forward-looking prep for finals.
3. Roadmap metrics computation (Module Coverage Scope, Exam Weightage, Task Completion Rate).
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Try importing boto3; handled gracefully if not configured
try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


def get_bedrock_client():
    """
    Initializes and returns an Amazon Bedrock runtime client if AWS credentials
    and region are configured in the environment. Returns None if unconfigured.
    """
    if not BOTO3_AVAILABLE:
        return None

    aws_region = os.environ.get("AWS_DEFAULT_REGION") or os.environ.get("AWS_REGION")
    aws_access_key = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")

    if not (aws_region and aws_access_key and aws_secret_key):
        return None

    try:
        client = boto3.client(
            service_name="bedrock-runtime",
            region_name=aws_region
        )
        return client
    except Exception as exc:
        logger.warning(f"Could not initialize Bedrock client: {exc}")
        return None


def generate_bedrock_roadmap(
    student_name: str,
    course_code: str,
    course_title: str,
    condition: str,
    mid_1: Optional[float],
    mid_2: Optional[float],
    assignment: Optional[float]
) -> Optional[str]:
    """
    Invokes Amazon Bedrock (Anthropic Claude 3 Haiku or Amazon Titan) if credentials exist.
    Returns None when unconfigured so caller immediately uses the local fallback engine.
    """
    client = get_bedrock_client()
    if not client:
        return None

    prompt = f"""You are an elite academic tutor advising {student_name} on {course_code}: {course_title}.
Current Status: {condition}.
Mid-1 Score: {mid_1}/30.
Mid-2 Score: {mid_2 if mid_2 is not None else 'Not Completed'}/30.
Assignment Score: {assignment}/40.

Generate a structured study roadmap with:
1. Executive Performance Diagnosis
2. High-Yield Topic Prioritization
3. Week-by-Week Action Items
"""

    try:
        # Anthropic Claude 3 Haiku payload structure
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.4
        })
        response = client.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            body=body,
            contentType="application/json",
            accept="application/json"
        )
        response_body = json.loads(response.get("body").read())
        return response_body["content"][0]["text"]
    except Exception as exc:
        logger.info(f"Bedrock invocation bypassed (using local fallback engine): {exc}")
        return None


def analyze_student_roadmap(
    student_profile: Dict[str, Any],
    course_code: str,
    target_exam: str,
    marks_record: Optional[Dict[str, Any]],
    syllabus_data: Dict[str, Any],
    completed_task_ids: List[str]
) -> Dict[str, Any]:
    """
    Core Conditional Logic Engine:
    - Determines if student has Mid-1 completed only OR both Mid-1 & Mid-2 completed.
    - Tailors remedial vs comparative trend analytics.
    - Computes:
      * Module Coverage Scope (%)
      * Exam Weightage (Marks)
      * Roadmap Task Completion Rate (%)
    """
    mid_1 = marks_record.get("mid_1") if marks_record else None
    mid_2 = marks_record.get("mid_2") if marks_record else None
    assignment = marks_record.get("assignment") if marks_record else 0.0

    # Determine condition
    has_mid_1 = mid_1 is not None
    has_mid_2 = mid_2 is not None

    all_modules = syllabus_data.get("modules", [])
    total_curriculum_modules = len(all_modules)

    # -------------------------------------------------------------
    # CASE A: Mid-1 Completed ONLY (Mid-2 is None or Pending)
    # -------------------------------------------------------------
    if has_mid_1 and not has_mid_2:
        condition_type = "MID_1_ONLY"
        condition_badge = "⚡ Retrospective Remedial Recovery Mode (Mid-1 Completed Only)"
        condition_summary = (
            f"Only Mid-1 assessment evaluated ({mid_1:.1f}/30). "
            f"Activating retroactive diagnostic remediation focusing on foundation Modules 1 & 2."
        )

        # Focus explicitly on Modules 1 and 2
        active_modules = [m for m in all_modules if m["module_id"] in (1, 2)]
        scope_pct = round((len(active_modules) / total_curriculum_modules) * 100, 1)
        exam_weightage = sum(m["exam_weightage"] for m in active_modules)

        # Performance diagnosis
        mid_1_pct = (mid_1 / 30.0) * 100
        if mid_1_pct < 65.0:
            severity = "CRITICAL"
            diagnosis = (
                f"Deficit Alert: Your Mid-1 score of {mid_1:.1f}/30 ({mid_1_pct:.1f}%) is in the danger zone. "
                f"Core gaps detected in Module 1 & 2 conceptual fundamentals."
            )
            # Calculations for recovery
            needed_for_A = max(0.0, 80.0 - (mid_1 + (assignment or 0.0)))
            target_mid_2 = min(30.0, max(22.0, needed_for_A))
            recovery_target = (
                f"To reach an 'A' grade (>=80/100 aggregate), you must score at least "
                f"{target_mid_2:.1f}/30 in Mid-2 and maintain {assignment or 30.0:.1f}/40 in coursework assignments."
            )
        else:
            severity = "STABLE"
            diagnosis = (
                f"Solid Foundation: Mid-1 score of {mid_1:.1f}/30 ({mid_1_pct:.1f}%). "
                f"Address minor conceptual friction in Modules 1 & 2 to lock in maximum marks for Mid-2."
            )
            recovery_target = (
                f"Maintain your momentum with targeted practice. Target >= 26.0/30 in Mid-2 for an 'S' grade trajectory."
            )

        strategy_header = "🛠️ Retrospective Remedial Recovery Plan"
        strategy_points = [
            f"Remediate weak topics in Module 1: {', '.join(active_modules[0]['scope_topics'][:2])}.",
            f"Deepen structural mastery in Module 2: {', '.join(active_modules[1]['scope_topics'][:2])}.",
            "Complete active-recall mini-quizzes below to solidify retention before Mid-2 commences.",
            "Schedule office hours or tutoring clinics for ambiguous algorithmic concepts."
        ]

    # -------------------------------------------------------------
    # CASE B: Mid-1 & Mid-2 Completed (Comparative Trend & Finals Prep)
    # -------------------------------------------------------------
    elif has_mid_1 and has_mid_2:
        condition_type = "MID_1_AND_2_COMPLETED"
        condition_badge = "🚀 Comparative Trend Analysis & Forward-Looking Prep for Finals (Mid-1 & Mid-2 Completed)"
        condition_summary = (
            f"Both internal mid-terms completed (Mid-1: {mid_1:.1f}/30, Mid-2: {mid_2:.1f}/30). "
            f"Internal marks accumulated: {(mid_1 + mid_2 + (assignment or 0.0)):.1f}/100."
        )

        # Delta & Velocity calculation
        delta = mid_2 - mid_1
        if delta > 1.0:
            trend_label = f"📈 Positive Growth (+{delta:.1f} pts)"
            trend_desc = f"Great upward velocity! You gained +{delta:.1f} marks from Mid-1 to Mid-2, indicating strong adaptation to advanced topics."
            trend_color = "green"
        elif delta < -1.0:
            trend_label = f"📉 Performance Dip ({delta:.1f} pts)"
            trend_desc = f"Score dropped by {abs(delta):.1f} marks in Mid-2. Module 3 & 4 topics require urgent reinforcement before final exams."
            trend_color = "red"
        else:
            trend_label = "⚖️ Steady Consistency (±1.0 pts)"
            trend_desc = "High consistency across both internal assessments. Ready to advance to comprehensive final review."
            trend_color = "blue"

        # Scope for finals includes full syllabus with heavy focus on Modules 3, 4, 5
        if target_exam == "Mid-2 (Internal Assessment 2)":
            active_modules = [m for m in all_modules if m["module_id"] in (3, 4)]
        else:
            # Finals / FAT
            active_modules = all_modules

        scope_pct = round((len(active_modules) / total_curriculum_modules) * 100, 1)
        exam_weightage = sum(m["exam_weightage"] for m in active_modules)

        diagnosis = f"{trend_label}: {trend_desc}"
        recovery_target = (
            f"Current internal subtotal: {(mid_1 + mid_2 + (assignment or 0.0)):.1f}/100. "
            f"Finals (FAT) carries heavy weightage on Modules 3, 4 & 5 (total {sum(m['exam_weightage'] for m in all_modules if m['module_id'] >= 3)} marks)."
        )

        strategy_header = "🎯 Forward-Looking Final Exam (FAT) Strategic Roadmap"
        strategy_points = [
            "Heavy Focus on High-Weightage Modules: Prioritize Modules 3, 4 & 5 (60-70% of final paper).",
            "Synthesize Cross-Module Integration: Practice problems combining Module 2 architecture with Module 4 scalability.",
            "Simulate Timed Practice: Solve past year university final papers under strict 3-hour constraints.",
            "Verify all roadmap tasks below to achieve 100% mastery."
        ]

    # -------------------------------------------------------------
    # CASE C: Initial state / Upcoming Mid-1
    # -------------------------------------------------------------
    else:
        condition_type = "PRE_MID_1"
        condition_badge = "📅 Pre-Assessment Onboarding (Mid-1 Prep)"
        condition_summary = "Assessments have not yet commenced. Prepare foundation Modules 1 & 2."
        active_modules = [m for m in all_modules if m["module_id"] in (1, 2)]
        scope_pct = round((len(active_modules) / total_curriculum_modules) * 100, 1)
        exam_weightage = sum(m["exam_weightage"] for m in active_modules)
        diagnosis = "Get ahead early by mastering early lecture concepts."
        recovery_target = "Target 28+/30 in Mid-1 to establish an elite semester baseline."
        strategy_header = "📚 Foundation Study Roadmap"
        strategy_points = [
            "Review lecture notes for Module 1.",
            "Clarify key terminology and definitions.",
            "Complete assigned weekly homework."
        ]

    # Calculate task completion rate
    total_tasks = sum(len(m.get("tasks", [])) for m in active_modules)
    all_task_ids = [t["task_id"] for m in active_modules for t in m.get("tasks", [])]
    completed_count = sum(1 for tid in all_task_ids if tid in completed_task_ids)
    task_completion_rate = round((completed_count / total_tasks * 100), 1) if total_tasks > 0 else 0.0

    return {
        "condition_type": condition_type,
        "condition_badge": condition_badge,
        "condition_summary": condition_summary,
        "active_modules": active_modules,
        "module_coverage_scope_pct": scope_pct,
        "exam_weightage_marks": exam_weightage,
        "task_completion_rate_pct": task_completion_rate,
        "completed_count": completed_count,
        "total_tasks": total_tasks,
        "diagnosis": diagnosis,
        "recovery_target": recovery_target,
        "strategy_header": strategy_header,
        "strategy_points": strategy_points,
        "is_bedrock_configured": get_bedrock_client() is not None
    }
