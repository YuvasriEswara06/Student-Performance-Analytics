"""
aws_config.py - Environment & AWS Service Configuration Layer
Strictly encapsulates AWS environment parsing and adapter configurations.
Defaults to AWS_ENABLED=False to preserve 100% offline local execution.
"""

import os
from typing import Dict, Any, Optional


def load_dotenv() -> None:
    """Loads environment variables from local .env file if present."""
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_file):
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, val = line.split("=", 1)
                        key = key.strip()
                        val = val.strip().strip("'\"")
                        if key and key not in os.environ:
                            os.environ[key] = val
        except Exception:
            pass


def get_aws_config() -> Dict[str, Any]:
    """
    Parses and returns AWS configuration settings from environment variables.
    Does not make network calls or require active AWS credentials on startup.
    """
    load_dotenv()
    aws_enabled_str = os.getenv("AWS_ENABLED", "false").strip().lower()
    aws_enabled = aws_enabled_str in ("true", "1", "yes")

    # Primary AWS region: ap-south-2 (Hyderabad)
    aws_region = os.getenv("AWS_REGION", "ap-south-2").strip()

    # S3 Storage Configuration
    s3_bucket = os.getenv("S3_BUCKET", "student-performance-analytics-2026-2933").strip()
    s3_region = os.getenv("S3_REGION", aws_region).strip()

    # DynamoDB Event Store Configuration
    dynamodb_table = os.getenv("DYNAMODB_TABLE", "StudentAttendanceEvents").strip()
    dynamodb_region = os.getenv("DYNAMODB_REGION", aws_region).strip()

    # SNS Notification Configuration
    sns_topic_arn = os.getenv("SNS_TOPIC_ARN", "").strip()
    sns_topic_name = os.getenv("SNS_TOPIC", "StudentAttendanceNotifications").strip()
    sns_region = os.getenv("SNS_REGION", aws_region).strip()

    # IoT Core Telemetry Configuration (ap-south-1 Mumbai)
    iot_endpoint = os.getenv("IOT_ENDPOINT", "").strip()
    iot_topic = os.getenv("IOT_TOPIC", "university/classroom/attendance").strip()
    iot_region = os.getenv("IOT_REGION", "ap-south-1").strip()
    iot_thing_name = os.getenv("IOT_THING_NAME", "StudentAnalyticsPortal").strip()
    iot_policy_name = os.getenv("IOT_POLICY_NAME", "StudentAnalyticsIoTPolicy").strip()

    # Bedrock Pedagogical Assistant (amazon.nova-lite-v1:0)
    bedrock_model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0").strip()
    bedrock_region = os.getenv("BEDROCK_REGION", aws_region).strip()

    rekognition_collection = os.getenv("REKOGNITION_COLLECTION", "StudentBiometricCollection").strip()
    rds_database_url = os.getenv("RDS_DATABASE_URL", "").strip()

    return {
        "aws_enabled": aws_enabled,
        "aws_region": aws_region,
        "s3_bucket": s3_bucket,
        "s3_region": s3_region,
        "dynamodb_table": dynamodb_table,
        "dynamodb_region": dynamodb_region,
        "sns_topic_arn": sns_topic_arn,
        "sns_topic_name": sns_topic_name,
        "sns_region": sns_region,
        "iot_endpoint": iot_endpoint,
        "iot_topic": iot_topic,
        "iot_region": iot_region,
        "iot_thing_name": iot_thing_name,
        "iot_policy_name": iot_policy_name,
        "bedrock_model_id": bedrock_model_id,
        "bedrock_region": bedrock_region,
        "rekognition_collection": rekognition_collection,
        "rds_database_url": rds_database_url
    }


def validate_aws_config(config: Dict[str, Any]) -> None:
    """
    Validates mandatory parameters when AWS_ENABLED is True.
    Raises ValueError for missing cloud configuration parameters.
    """
    if not config["aws_enabled"]:
        return

    if not config["bedrock_model_id"]:
        raise ValueError(
            "BEDROCK_MODEL_ID environment variable is required when AWS_ENABLED=true. "
            "Example: BEDROCK_MODEL_ID='amazon.nova-pro-v1:0'"
        )
