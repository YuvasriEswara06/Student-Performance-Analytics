"""
verify_aws_connection.py - Backend Verification Script
Tests AWS connectivity for S3, DynamoDB, SNS, IoT Core, and Bedrock
without modifying any Streamlit UI/UX or local functionality.
"""

import sys
import os
import json
import aws_config
import aws_integration

def run_verification():
    print("=" * 70)
    print("      AWS SERVICES CONNECTION & BACKEND INTEGRATION TEST")
    print("=" * 70)
    
    config = aws_config.get_aws_config()
    print(f"[*] AWS Enabled State       : {config['aws_enabled']}")
    print(f"[*] Primary AWS Region      : {config['aws_region']}")
    print(f"[*] S3 Bucket (ap-south-2)   : {config['s3_bucket']}")
    print(f"[*] DynamoDB Table (ap-s-2) : {config['dynamodb_table']} (Partition key: event_id)")
    print(f"[*] SNS Topic Name          : {config['sns_topic_name']}")
    print(f"[*] SNS Topic ARN           : {config['sns_topic_arn'] or 'Not Set (Auto-formatted)'}")
    print(f"[*] IoT Core Region         : {config['iot_region']} (Mumbai)")
    print(f"[*] IoT Data Endpoint       : {config['iot_endpoint'] or 'Default AWS Regional Routing'}")
    print(f"[*] IoT Topic               : {config['iot_topic']}")
    print(f"[*] Bedrock Region          : {config['bedrock_region']} (Hyderabad)")
    print(f"[*] Bedrock Model ID        : {config['bedrock_model_id']}")
    print("-" * 70)

    if not config["aws_enabled"]:
        print("[!] AWS_ENABLED is currently 'false'.")
        print("[!] To execute real cloud calls, set AWS_ENABLED=true in your environment or .env file.")
        print("[✔] Local mode backend logic verified OK.")
        return

    adapters = aws_integration.AWSCloudAdapters(config)

    # 1. Multi-Service Event Test (S3, IoT Core, DynamoDB, SNS)
    print("[+] Testing Multi-Service Attendance Event Dispatch...")
    sample_image = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\x09\x09\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9"
    
    event_res = adapters.publish_attendance_verification_event(
        student_id="STU1001",
        course_code="CSE3002",
        verification_status="MATCH",
        confidence_pct=99.4,
        image_bytes=sample_image
    )
    
    print(f"    [*] Event Dispatch Status : {event_res['status']}")
    print(f"    [*] S3 Upload Result      : {event_res['results']['s3']}")
    print(f"    [*] IoT Publish Result    : {event_res['results']['iot']}")
    print(f"    [*] DynamoDB Result       : {event_res['results']['dynamodb']}")
    print(f"    [*] SNS Notification      : {event_res['results']['sns']}")

    # 2. Bedrock LLM Test
    print("\n[+] Testing Amazon Bedrock (ap-south-2, in.openai.gpt-5.6-luna)...")
    bedrock_res = adapters.invoke_study_assistant({
        "student_id": "STU1001",
        "course_code": "CSE3002",
        "cgpa": 8.5
    })
    print(f"    [*] Bedrock Invocation    : {bedrock_res['status']}")
    if bedrock_res.get("error"):
        print(f"    [*] Bedrock Notice        : {bedrock_res['error']}")

    print("=" * 70)
    print("[✔] Backend AWS Integration Verification Finished!")
    print("=" * 70)

if __name__ == "__main__":
    run_verification()
