import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIRECTORY = PROJECT_ROOT / "scripts"

sys.path.insert(0, str(SCRIPTS_DIRECTORY))

from detect_security_changes import detect_security_change


def create_event(event_name, event_source, request_parameters=None):
    return {
        "eventTime": "2026-01-01T00:00:00Z",
        "eventName": event_name,
        "eventSource": event_source,
        "requestParameters": request_parameters or {},
    }


def create_ssh_parameters(ipv4_ranges=None, ipv6_ranges=None):
    return {
        "ipPermissions": {
            "items": [
                {
                    "ipProtocol": "tcp",
                    "fromPort": 22,
                    "toPort": 22,
                    "ipRanges": {
                        "items": ipv4_ranges or [],
                    },
                    "ipv6Ranges": {
                        "items": ipv6_ranges or [],
                    },
                }
            ]
        }
    }


class SecurityChangeDetectionTests(unittest.TestCase):
    def test_detects_public_ipv4_ssh_authorization(self):
        event = create_event(
            "AuthorizeSecurityGroupIngress",
            "ec2.amazonaws.com",
            create_ssh_parameters(
                ipv4_ranges=[{"cidrIp": "0.0.0.0/0"}]
            ),
        )

        finding = detect_security_change(event)

        self.assertIsNotNone(finding)
        self.assertEqual(finding["severity"], "HIGH")
        self.assertEqual(finding["status"], "OPEN")

    def test_detects_public_ipv6_ssh_authorization(self):
        event = create_event(
            "AuthorizeSecurityGroupIngress",
            "ec2.amazonaws.com",
            create_ssh_parameters(
                ipv6_ranges=[{"cidrIpv6": "::/0"}]
            ),
        )

        finding = detect_security_change(event)

        self.assertIsNotNone(finding)
        self.assertEqual(
            finding["finding"],
            "Public SSH access was authorized",
        )

    def test_ignores_private_ssh_authorization(self):
        event = create_event(
            "AuthorizeSecurityGroupIngress",
            "ec2.amazonaws.com",
            create_ssh_parameters(
                ipv4_ranges=[{"cidrIp": "10.0.0.0/8"}]
            ),
        )

        self.assertIsNone(detect_security_change(event))

    def test_detects_public_ssh_revocation(self):
        event = create_event(
            "RevokeSecurityGroupIngress",
            "ec2.amazonaws.com",
            create_ssh_parameters(
                ipv4_ranges=[{"cidrIp": "0.0.0.0/0"}]
            ),
        )

        finding = detect_security_change(event)

        self.assertIsNotNone(finding)
        self.assertEqual(finding["status"], "REMEDIATED")

    def test_detects_bucket_policy_deletion(self):
        event = create_event(
            "DeleteBucketPolicy",
            "s3.amazonaws.com",
        )

        finding = detect_security_change(event)

        self.assertIsNotNone(finding)
        self.assertEqual(finding["severity"], "HIGH")
        self.assertEqual(finding["status"], "OPEN")

    def test_marks_bucket_policy_update_for_review(self):
        event = create_event(
            "PutBucketPolicy",
            "s3.amazonaws.com",
        )

        finding = detect_security_change(event)

        self.assertIsNotNone(finding)
        self.assertEqual(finding["severity"], "REVIEW")
        self.assertEqual(finding["status"], "CHANGED")

    def test_detects_flattened_imdsv2_optional_schema(self):
        event = create_event(
            "ModifyInstanceMetadataOptions",
            "ec2.amazonaws.com",
            {
                "httpTokens": "optional",
            },
        )

        finding = detect_security_change(event)

        self.assertIsNotNone(finding)
        self.assertEqual(finding["severity"], "HIGH")
        self.assertEqual(
            finding["finding"],
            "IMDSv1 compatibility was enabled",
        )

    def test_detects_nested_pascal_case_imdsv2_required_schema(self):
        event = create_event(
            "ModifyInstanceMetadataOptions",
            "ec2.amazonaws.com",
            {
                "ModifyInstanceMetadataOptionsRequest": {
                    "HttpTokens": "required",
                }
            },
        )

        finding = detect_security_change(event)

        self.assertIsNotNone(finding)
        self.assertEqual(finding["status"], "REMEDIATED")
        self.assertEqual(
            finding["finding"],
            "IMDSv2 enforcement was restored",
        )

    def test_ignores_unrelated_event(self):
        event = create_event(
            "DescribeInstances",
            "ec2.amazonaws.com",
        )

        self.assertIsNone(detect_security_change(event))


if __name__ == "__main__":
    unittest.main()