"""
tests/test_aws_adapters.py - Unit Test Suite for AWS Adapters
Validates AWS configuration parsing, Rekognition biometric policies, Bedrock payload contracts,
and IoT Core event formatting using unittest.mock without requiring live AWS credentials or network calls.
"""

import os
import unittest
from unittest.mock import patch, MagicMock

import aws_config
from aws_integration import AWSCloudAdapters


class TestAWSAdapters(unittest.TestCase):

    def test_aws_config_disabled(self):
        """Verifies AWS configuration defaults to AWS_ENABLED=False and ap-south-2 region."""
        with patch.dict(os.environ, {"AWS_ENABLED": "false"}, clear=True):
            config = aws_config.get_aws_config()
            self.assertFalse(config["aws_enabled"])
            self.assertEqual(config["aws_region"], "ap-south-2")
            self.assertEqual(config["s3_bucket"], "student-performance-analytics-2026-2933")
            self.assertEqual(config["dynamodb_table"], "StudentAttendanceEvents")
            self.assertIn("openai.gpt-5.6-luna", config["bedrock_model_id"])
            self.assertEqual(config["iot_region"], "ap-south-1")
            
            # validate_aws_config should pass silently when disabled
            aws_config.validate_aws_config(config)

            adapter = AWSCloudAdapters(config)
            result = adapter.search_student_face(b"fake_image_bytes")
            self.assertEqual(result["status"], "SKIPPED_AWS_DISABLED")
            self.assertFalse(result["is_match"])
            self.assertEqual(result["policy_decision"], "DISABLED")

    def test_aws_config_enabled_missing_model(self):
        """Verifies validate_aws_config passes when default BEDROCK_MODEL_ID is set."""
        with patch.dict(os.environ, {"AWS_ENABLED": "true", "AWS_REGION": "ap-south-2"}):
            config = aws_config.get_aws_config()
            self.assertTrue(config["aws_enabled"])
            self.assertIn("openai.gpt-5.6-luna", config["bedrock_model_id"])
            aws_config.validate_aws_config(config)

    def test_rekognition_adapter_policy(self):
        """Tests search_student_face verification policy thresholds (MATCH, REVIEW, REJECT)."""
        config = {
            "aws_enabled": True,
            "aws_region": "ap-south-2",
            "s3_bucket": "student-performance-analytics-2026-2933",
            "rekognition_collection": "TestCollection",
            "bedrock_model_id": "arn:aws:bedrock:ap-south-2:008485359374:inference-profile/global.openai.gpt-5.6-luna",
            "iot_endpoint": "",
            "iot_topic": "test/topic",
            "rds_database_url": ""
        }
        adapter = AWSCloudAdapters(config)

        # 1. Match >= 80% threshold -> MATCH
        mock_rek = MagicMock()
        mock_rek.search_faces_by_image.return_value = {
            "FaceMatches": [
                {"Similarity": 92.5, "Face": {"ExternalImageId": "STU001"}}
            ]
        }
        with patch.object(adapter, "_get_boto3_client", return_value=mock_rek):
            res = adapter.search_student_face(b"bytes", threshold=80.0)
            self.assertEqual(res["status"], "SUCCESS")
            self.assertTrue(res["is_match"])
            self.assertEqual(res["policy_decision"], "MATCH")
            self.assertEqual(res["matched_student_id"], "STU001")
            self.assertEqual(res["confidence_pct"], 92.5)

        # 2. Match between 65% and 80% -> REVIEW
        mock_rek.search_faces_by_image.return_value = {
            "FaceMatches": [
                {"Similarity": 71.0, "Face": {"ExternalImageId": "STU002"}}
            ]
        }
        with patch.object(adapter, "_get_boto3_client", return_value=mock_rek):
            res = adapter.search_student_face(b"bytes", threshold=80.0)
            self.assertEqual(res["status"], "SUCCESS")
            self.assertFalse(res["is_match"])
            self.assertEqual(res["policy_decision"], "REVIEW")

        # 3. Match < 65% -> REJECT
        mock_rek.search_faces_by_image.return_value = {"FaceMatches": []}
        with patch.object(adapter, "_get_boto3_client", return_value=mock_rek):
            res = adapter.search_student_face(b"bytes", threshold=80.0)
            self.assertEqual(res["status"], "NO_MATCH_FOUND")
            self.assertFalse(res["is_match"])
            self.assertEqual(res["policy_decision"], "REJECT")

    def test_bedrock_payload_contract(self):
        """Verifies invoke_study_assistant formats bedrock converse payload correctly for global.openai.gpt-5.6-luna."""
        config = {
            "aws_enabled": True,
            "aws_region": "ap-south-2",
            "s3_bucket": "student-performance-analytics-2026-2933",
            "rekognition_collection": "TestCollection",
            "bedrock_model_id": "arn:aws:bedrock:ap-south-2:008485359374:inference-profile/global.openai.gpt-5.6-luna",
            "iot_endpoint": "",
            "iot_topic": "test/topic",
            "rds_database_url": ""
        }
        adapter = AWSCloudAdapters(config)

        mock_bedrock_runtime = MagicMock()
        mock_bedrock_runtime.converse.return_value = {
            "output": {"message": {"content": [{"text": "Strategic roadmap for DBMS"}]}}
        }

        with patch.object(adapter, "_get_boto3_client", return_value=mock_bedrock_runtime):
            context = {"student_id": "STU001", "cgpa": 8.4, "attendance_pct": 92.0}
            res = adapter.invoke_study_assistant(context)
            self.assertEqual(res["status"], "SUCCESS")
            self.assertIn("text", res)
            self.assertEqual(res["text"], "Strategic roadmap for DBMS")

    def test_multi_service_attendance_event(self):
        """Verifies publish_attendance_verification_event dispatches to IoT, DynamoDB, S3, and SNS."""
        config = {
            "aws_enabled": True,
            "aws_region": "ap-south-2",
            "s3_bucket": "student-performance-analytics-2026-2933",
            "s3_region": "ap-south-2",
            "dynamodb_table": "StudentAttendanceEvents",
            "dynamodb_region": "ap-south-2",
            "sns_topic_name": "StudentAttendanceNotifications",
            "sns_topic_arn": "arn:aws:sns:ap-south-2:123456789012:StudentAttendanceNotifications",
            "sns_region": "ap-south-2",
            "iot_topic": "university/classroom/attendance",
            "iot_region": "ap-south-1",
            "bedrock_model_id": "in.openai.gpt-5.6-luna",
            "bedrock_region": "ap-south-2"
        }
        adapter = AWSCloudAdapters(config)

        mock_s3 = MagicMock()
        mock_iot = MagicMock()
        mock_dynamodb = MagicMock()
        mock_sns = MagicMock()

        def mock_client_factory(service_name, **kwargs):
            if service_name == "s3":
                return mock_s3
            elif service_name == "iot-data":
                return mock_iot
            elif service_name == "dynamodb":
                return mock_dynamodb
            elif service_name == "sns":
                return mock_sns
            return MagicMock()

        with patch.object(adapter, "_get_boto3_client", side_effect=mock_client_factory):
            res = adapter.publish_attendance_verification_event(
                student_id="STU001",
                course_code="CSE3002",
                verification_status="MATCH",
                confidence_pct=99.4,
                image_bytes=b"sample_jpeg_bytes",
                verification_id="VERIF-TEST123456"
            )
            self.assertEqual(res["status"], "SUCCESS")
            self.assertEqual(res["event_payload"]["event_id"], "VERIF-TEST123456")
            self.assertEqual(res["results"]["s3"], "SUCCESS")
            self.assertEqual(res["results"]["iot"], "SUCCESS")
            self.assertEqual(res["results"]["dynamodb"], "SUCCESS")
            self.assertEqual(res["results"]["sns"], "SUCCESS")

            mock_s3.put_object.assert_called_once()
            mock_iot.publish.assert_called_once()
            mock_dynamodb.put_item.assert_called_once()
            mock_sns.publish.assert_called_once()


if __name__ == "__main__":
    unittest.main()
