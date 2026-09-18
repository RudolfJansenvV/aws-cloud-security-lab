# Portfolio Evidence

This directory contains sanitized screenshots and outputs collected while building and securing the AWS Cloud Security Lab.

## Evidence-handling rules

- Credentials, passwords, MFA information, account numbers, and personal information are never included.
- Unique AWS resource identifiers are removed or cropped where they do not contribute to the technical explanation.
- Screenshots retain relevant resource names, configurations, relationships, and security controls.
- Evidence supports the written documentation but does not replace explanations or verification steps.
- Files use numbered, descriptive names to keep the project history clear.

## Evidence index

| File | Demonstrates |
|---|---|
| [02-vpc-resource-map-redacted.png](02-vpc-resource-map-redacted.png) | Multi-AZ VPC structure, public/private subnet separation, route-table associations, and internet-gateway connectivity |
| [03-ec2-security-validation.png](03-ec2-security-validation.png) | Secure EC2 administration using Amazon Linux, Session Manager, the SSM Agent, and IMDSv2 |
| [04-s3-version-recovery-redacted.png](04-s3-version-recovery-redacted.png) | S3 versioning, delete-marker behavior, and recovery of a deleted object |
| [05-cloudtrail-s3-data-events.png](05-cloudtrail-s3-data-events.png) | CloudTrail S3 data events identified through the local Python analysis script |
| [06-iam-security-auditor-simulation.png](06-iam-security-auditor-simulation.png) | Read-only auditor access with administrative actions denied |
| [07-project-operator-policy-simulation.png](07-project-operator-policy-simulation.png) | Tag-restricted EC2 operation with termination and security-group modification denied |
| [08-operator-s3-least-privilege.png](08-operator-s3-least-privilege.png) | Approved S3 visibility with bucket-policy, public-access, and deletion controls denied |
| [09-operator-cloudtrail-least-privilege.png](09-operator-cloudtrail-least-privilege.png) | Read-only CloudTrail configuration access with trail modification and logging interruption denied |
| [10-operator-iam-least-privilege.png](10-operator-iam-least-privilege.png) | Project IAM visibility with policy attachment, trust-policy modification, and role passing denied |
| [11-ec2-stopped-no-key-pair.png](11-ec2-stopped-no-key-pair.png) | Stopped EC2 instance and absence of a key pair during the controlled test |
| [12-inbound-rules-secure-baseline.png](12-inbound-rules-secure-baseline.png) | Zero-rule security-group baseline before the controlled change |
| [13-public-ssh-misconfiguration.png](13-public-ssh-misconfiguration.png) | Temporary insecure SSH exposure on TCP port 22 from `0.0.0.0/0` |
| [14-inbound-rules-remediated.png](14-inbound-rules-remediated.png) | Restored zero-rule security-group baseline after remediation |
| [15-cloudtrail-authorize-security-group-ingress.png](15-cloudtrail-authorize-security-group-ingress.png) | CloudTrail authorization event recording creation of the insecure rule |
| [16-cloudtrail-revoke-security-group-ingress.png](16-cloudtrail-revoke-security-group-ingress.png) | CloudTrail revocation event confirming removal of the insecure rule |
| [17-s3-tls-policy-secure-baseline.png](17-s3-tls-policy-secure-baseline.png) | Secure S3 baseline with explicit denial of requests that do not use TLS |
| [18-s3-tls-policy-misconfiguration.png](18-s3-tls-policy-misconfiguration.png) | Temporary absence of the bucket policy while Block Public Access remained enabled |
| [19-s3-tls-policy-remediated.png](19-s3-tls-policy-remediated.png) | Restored `DenyInsecureTransport` bucket-policy control |
| [20-cloudtrail-delete-bucket-policy.png](20-cloudtrail-delete-bucket-policy.png) | CloudTrail event recording removal of the S3 bucket policy |
| [21-cloudtrail-put-bucket-policy.png](21-cloudtrail-put-bucket-policy.png) | CloudTrail event confirming restoration of the S3 bucket policy |
| [22-imdsv2-required-baseline.png](22-imdsv2-required-baseline.png) | Secure EC2 metadata baseline with IMDSv2 required |
| [23-imdsv2-optional-misconfiguration.png](23-imdsv2-optional-misconfiguration.png) | Temporary metadata regression allowing tokenless IMDSv1 requests |
| [24-imdsv2-required-remediated.png](24-imdsv2-required-remediated.png) | Restored IMDSv2-required configuration with the metadata service enabled |
| [25-cloudtrail-modify-instance-metadata-options.png](25-cloudtrail-modify-instance-metadata-options.png) | CloudTrail events recording the IMDSv2 regression and remediation |
