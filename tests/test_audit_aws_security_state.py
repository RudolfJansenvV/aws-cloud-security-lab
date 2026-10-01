import unittest

from scripts.audit_aws_security_state import (
    count_public_ssh_rules,
    evaluate_ec2_security,
    permission_allows_public_ssh,
)


class TestPublicSshDetection(unittest.TestCase):
    def test_detects_public_ipv4_ssh(self):
        permission = {
            "IpProtocol": "tcp",
            "FromPort": 22,
            "ToPort": 22,
            "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
        }

        self.assertTrue(
            permission_allows_public_ssh(permission)
        )

    def test_detects_public_ipv6_ssh(self):
        permission = {
            "IpProtocol": "tcp",
            "FromPort": 22,
            "ToPort": 22,
            "Ipv6Ranges": [{"CidrIpv6": "::/0"}],
        }

        self.assertTrue(
            permission_allows_public_ssh(permission)
        )

    def test_detects_ssh_inside_port_range(self):
        permission = {
            "IpProtocol": "tcp",
            "FromPort": 20,
            "ToPort": 25,
            "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
        }

        self.assertTrue(
            permission_allows_public_ssh(permission)
        )

    def test_ignores_private_ssh(self):
        permission = {
            "IpProtocol": "tcp",
            "FromPort": 22,
            "ToPort": 22,
            "IpRanges": [{"CidrIp": "10.0.0.0/8"}],
        }

        self.assertFalse(
            permission_allows_public_ssh(permission)
        )

    def test_ignores_public_https(self):
        permission = {
            "IpProtocol": "tcp",
            "FromPort": 443,
            "ToPort": 443,
            "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
        }

        self.assertFalse(
            permission_allows_public_ssh(permission)
        )

    def test_counts_public_ssh_rules(self):
        groups = [
            {
                "IpPermissions": [
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 22,
                        "ToPort": 22,
                        "IpRanges": [
                            {"CidrIp": "0.0.0.0/0"}
                        ],
                    },
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 443,
                        "ToPort": 443,
                        "IpRanges": [
                            {"CidrIp": "0.0.0.0/0"}
                        ],
                    },
                ]
            }
        ]

        self.assertEqual(
            count_public_ssh_rules(groups),
            1,
        )


class TestSecurityEvaluation(unittest.TestCase):
    def setUp(self):
        self.secure_instance = {
            "State": {"Name": "stopped"},
            "MetadataOptions": {
                "HttpTokens": "required",
                "HttpEndpoint": "enabled",
                "HttpPutResponseHopLimit": 2,
            },
            "SecurityGroups": [],
        }

    def test_secure_instance_passes_all_checks(self):
        checks = evaluate_ec2_security(
            [self.secure_instance],
            [],
        )

        self.assertEqual(len(checks), 6)
        self.assertTrue(
            all(check["passed"] for check in checks)
        )

    def test_optional_imdsv2_fails(self):
        instance = {
            **self.secure_instance,
            "MetadataOptions": {
                **self.secure_instance["MetadataOptions"],
                "HttpTokens": "optional",
            },
        }

        checks = evaluate_ec2_security([instance], [])
        results = {
            check["name"]: check["passed"]
            for check in checks
        }

        self.assertFalse(
            results["IMDSv2 enforcement"]
        )

    def test_attached_key_pair_fails(self):
        instance = {
            **self.secure_instance,
            "KeyName": "example-key",
        }

        checks = evaluate_ec2_security([instance], [])
        results = {
            check["name"]: check["passed"]
            for check in checks
        }

        self.assertFalse(
            results["EC2 key-pair exposure"]
        )

    def test_public_ssh_fails(self):
        groups = [
            {
                "IpPermissions": [
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 22,
                        "ToPort": 22,
                        "IpRanges": [
                            {"CidrIp": "0.0.0.0/0"}
                        ],
                    }
                ]
            }
        ]

        checks = evaluate_ec2_security(
            [self.secure_instance],
            groups,
        )

        results = {
            check["name"]: check["passed"]
            for check in checks
        }

        self.assertFalse(
            results["Public SSH exposure"]
        )

    def test_no_instances_fails_discovery(self):
        checks = evaluate_ec2_security([], [])

        self.assertEqual(len(checks), 1)
        self.assertFalse(checks[0]["passed"])


if __name__ == "__main__":
    unittest.main()