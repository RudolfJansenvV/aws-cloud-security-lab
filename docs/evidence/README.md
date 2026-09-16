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
