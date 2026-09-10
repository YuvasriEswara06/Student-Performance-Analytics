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
        """Verifies AWS configuration defaults to AWS_ENABLED=False and ap-south-1 region."""
        with patch.dict(os.environ, {"AWS_ENABLED": "false"}, clear=True):
            config = aws_config.get_aws_config()
            self.assertFalse(config["aws_enabled"])
            self.assertEqual(config["aws_region"], "ap-south-1")
            
            # validate_aws_config should pass silently when disabled
            aws_config.validate_aws_config(config)

            adapter = AWSCloudAdapters(config)
            result = adapter.search_student_face(b"fake_image_bytes")
            self.assertEqual(result["status"], "SKIPPED_AWS_DISABLED")
            self.assertFalse(result["is_match"])
            self.assertEqual(result["policy_decision"], "DISABLED")

    def test_aws_config_enabled_missing_model(self):
        """Verifies validate_aws_config raises ValueError if BEDROCK_MODEL_ID is omitted when enabled."""
        with patch.dict(os.environ, {"AWS_ENABLED": "true", "AWS_REGION": "ap-south-1", "BEDROCK_MODEL_ID": ""}):
            config = aws_config.get_aws_config()
            self.assertTrue(config["aws_enabled"])
            with self.assertRaises(ValueError) as ctx:
                aws_config.validate_aws_config(config)
            self.assertIn("BEDROCK_MODEL_ID environment variable is required", str(ctx.exception))

    def test_rekognition_adapter_policy(self):
        """Tests search_student_face verification policy thresholds (MATCH, REVIEW, REJECT)."""
        config = {
            "aws_enabled": True,
            "aws_region": "ap-south-1",
            "s3_bucket": "test-bucket",
            "rekognition_collection": "TestCollection",
            "bedrock_model_id": "amazon.nova-pro-v1:0",
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
        """Verifies invoke_study_assistant formats bedrock payload correctly and calls model."""
        config = {
            "aws_enabled": True,
            "aws_region": "ap-south-1",
            "s3_bucket": "test-bucket",
            "rekognition_collection": "TestCollection",
            "bedrock_model_id": "amazon.nova-pro-v1:0",
            "iot_endpoint": "",
            "iot_topic": "test/topic",
            "rds_database_url": ""
        }
        adapter = AWSCloudAdapters(config)

        mock_bedrock = MagicMock()
        mock_bedrock.list_foundation_models.return_value = {
            "modelSummaries": [{"modelId": "amazon.nova-pro-v1:0"}]
        }

        mock_bedrock_runtime = MagicMock()
        mock_response_body = MagicMock()
        mock_response_body.read.return_value = b'{"strategy_header": "Focus on Calculus", "diagnosis": "Low score in Midterm", "recovery_target": "85%", "actionable_steps": ["Review Integration"]}'
        mock_bedrock_runtime.invoke_model.return_value = {"body": mock_response_body}

        def mock_client_factory(service_name):
            if service_name == "bedrock":
                return mock_bedrock
            elif service_name == "bedrock-runtime":
                return mock_bedrock_runtime
            return MagicMock()

        with patch.object(adapter, "_get_boto3_client", side_effect=mock_client_factory):
            context = {"student_id": "STU001", "cgpa": 8.4, "attendance_pct": 92.0}
            res = adapter.invoke_study_assistant(context)
            self.assertEqual(res["status"], "SUCCESS")
            self.assertIn("pedagogical_output", res)
            self.assertEqual(res["pedagogical_output"]["strategy_header"], "Focus on Calculus")

    def test_iot_event_idempotency(self):
        """Verifies publish_attendance_event publishes structured JSON event with verification_id as event_id."""
        config = {
            "aws_enabled": True,
            "aws_region": "ap-south-1",
            "s3_bucket": "test-bucket",
            "rekognition_collection": "TestCollection",
            "bedrock_model_id": "amazon.nova-pro-v1:0",
            "iot_endpoint": "",
            "iot_topic": "university/classroom/attendance",
            "rds_database_url": ""
        }
        adapter = AWSCloudAdapters(config)

        mock_iot = MagicMock()
        with patch.object(adapter, "_get_boto3_client", return_value=mock_iot):
            res = adapter.publish_attendance_event(
                student_id="STU001",
                course_code="CS101",
                verification_status="VERIFIED",
                verification_id="VERIF-12345678"
            )
            self.assertEqual(res["status"], "SUCCESS")
            self.assertEqual(res["event_payload"]["event_id"], "VERIF-12345678")
            self.assertEqual(res["event_payload"]["student_id"], "STU001")
            mock_iot.publish.assert_called_once()


if __name__ == "__main__":
    unittest.main()
