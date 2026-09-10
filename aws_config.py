"""
aws_config.py - Environment & AWS Service Configuration Layer
Strictly encapsulates AWS environment parsing and adapter configurations.
Defaults to AWS_ENABLED=False to preserve 100% offline local execution.
"""

import os
from typing import Dict, Any, Optional


def get_aws_config() -> Dict[str, Any]:
    """
    Parses and returns AWS configuration settings from environment variables.
    Does not make network calls or require active AWS credentials on startup.
    """
    aws_enabled_str = os.getenv("AWS_ENABLED", "false").strip().lower()
    aws_enabled = aws_enabled_str in ("true", "1", "yes")

    aws_region = os.getenv("AWS_REGION", "ap-south-1").strip()
    s3_bucket = os.getenv("S3_BUCKET", "student-performance-analytics-assets").strip()
    rekognition_collection = os.getenv("REKOGNITION_COLLECTION", "StudentBiometricCollection").strip()
    bedrock_model_id = os.getenv("BEDROCK_MODEL_ID", "").strip()
    iot_endpoint = os.getenv("IOT_ENDPOINT", "").strip()
    iot_topic = os.getenv("IOT_TOPIC", "university/classroom/attendance").strip()
    rds_database_url = os.getenv("RDS_DATABASE_URL", "").strip()

    return {
        "aws_enabled": aws_enabled,
        "aws_region": aws_region,
        "s3_bucket": s3_bucket,
        "rekognition_collection": rekognition_collection,
        "bedrock_model_id": bedrock_model_id,
        "iot_endpoint": iot_endpoint,
        "iot_topic": iot_topic,
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
