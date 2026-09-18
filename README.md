# AWS Cloud Security Lab

A hands-on cloud security project focused on building, securing, testing, monitoring, and automating a small AWS environment.

This repository documents the complete process—from the initial architecture and secure account setup to deliberate misconfigurations, detection, remediation, and Python-based security checks.

> **Status:** Stage 3 in progress — Controlled misconfiguration, detection, and remediation

## Current progress

- [x] Established the AWS account security baseline
- [x] Designed and implemented a segmented two-AZ VPC
- [x] Configured public and private route tables
- [x] Deployed an encrypted Amazon Linux EC2 instance
- [x] Removed inbound administrative access
- [x] Enabled administration through AWS Systems Manager
- [x] Required and validated IMDSv2
- [x] Documented an EC2 security-group configuration issue and resolution
- [x] Implemented secure Amazon S3 storage
- [x] Enabled and validated audit logging

### Stage 1 documentation

- [Account security baseline](docs/security/account-baseline.md)
- [Network architecture and implementation](architecture/network-design.md)
- [Secure EC2 administration](docs/security/ec2-secure-administration.md)
- [Security group troubleshooting](docs/troubleshooting/ec2-security-group-selection.md)
- [Secure S3 storage and recovery](docs/security/s3-secure-storage.md)
- [CloudTrail audit logging and validation](docs/security/cloudtrail-audit-logging.md)

## Stage 2 progress

- [x] Created an MFA-protected security auditor role
- [x] Validated auditor permissions using the IAM Policy Simulator and temporary console access
- [x] Created an MFA-protected project operator role
- [x] Restricted EC2 operations using project resource tags
- [x] Enabled controlled Session Manager access without SSH
- [x] Scoped S3 object operations to the approved secure-data bucket
- [x] Protected object versions and the CloudTrail audit bucket from the operator
- [x] Allowed read-only CloudTrail configuration visibility while denying logging changes
- [x] Allowed project IAM visibility while denying user enumeration and privilege escalation
- [x] Validated the operator policy through simulation and live role sessions
- [x] Reserved bootstrap administrator access for privileged configuration and recovery

### Stage 2 documentation

- [IAM security auditor role](docs/security/iam-security-auditor-role.md)
- [Project operator role design and validation](docs/security/project-operator-role-design.md)
- [Project operator IAM policy](policies/project-operator-policy.json)
- [Operator policy resource ARN troubleshooting](docs/troubleshooting/operator-policy-resource-arn.md)
- [Sanitized portfolio evidence](docs/evidence/README.md)

## Stage 3 progress

- [x] Established and documented a secure security-group baseline
- [x] Introduced a controlled public SSH rule on TCP port 22
- [x] Kept the EC2 instance stopped with no key pair during testing
- [x] Detected the insecure `0.0.0.0/0` source configuration
- [x] Removed the insecure rule and restored the zero-rule baseline
- [x] Investigated the authorization and revocation events in CloudTrail
- [x] Preserved sanitized before, during, and after evidence
- [ ] Complete additional controlled misconfiguration exercises

### Stage 3 documentation

- [Public SSH security-group exposure incident](docs/incidents/01-public-ssh-exposure.md)
- [Sanitized portfolio evidence](docs/evidence/README.md)

## Project objectives

- Build a functional AWS environment and understand every component.
- Apply least privilege, encryption, network segmentation, and secure access.
- Enable audit logging and security monitoring.
- Introduce controlled misconfigurations and document their risks.
- Detect and remediate security issues.
- Automate repeatable security checks with Python.
- Rebuild the environment with Terraform as Infrastructure as Code.

## Project stages

| Stage | Focus | Status |
|---|---|---|
| 1 | Build the AWS environment | Complete |
| 2 | Apply security controls | Complete |
| 3 | Introduce controlled misconfigurations | In progress |
| 4 | Detect and investigate changes | Planned |
| 5 | Automate security checks with Python | Planned |
| 6 | Rebuild with Terraform and finalize documentation | Planned |

## Planned AWS services

- Amazon VPC
- Public and private subnets
- Route tables and security groups
- Amazon EC2
- Amazon S3
- AWS Identity and Access Management (IAM)
- AWS CloudTrail
- Amazon CloudWatch
- AWS Key Management Service (KMS)

The design may evolve as security requirements and cost considerations are evaluated.

## Repository structure

```text
aws-cloud-security-lab/
├── architecture/       # Architecture diagrams
├── docs/
│   ├── build/          # Build process and verification
│   ├── security/       # Security controls and design decisions
│   ├── troubleshooting/# Issues, investigation, resolution, and lessons learned
│   ├── incidents/      # Misconfiguration and investigation write-ups
│   └── evidence/       # Sanitized screenshots and command output
├── policies/           # IAM and resource-policy examples
├── scripts/            # Python security-audit tools
├── terraform/          # Infrastructure as Code
├── .gitignore
├── LICENSE
└── README.md
```

Folders will be added as the corresponding project stages begin.

## Documentation approach

Each major implementation will document:

1. The security or operational requirement.
2. The configuration that was implemented.
3. How the configuration was validated.
4. The evidence collected.
5. Any issue encountered and how it was resolved.
6. What was learned from the exercise.

## Security notice

This is a controlled learning environment. No credentials, access keys, private keys, account numbers, sensitive billing information, or active resource identifiers will be published. Screenshots and logs will be reviewed and sanitized before being committed.

Deliberately vulnerable configurations will only be used temporarily in an isolated lab environment and will be remediated or removed immediately after testing.

## Author

**Rudolf Jansen van Vuuren**

CompTIA Security+ certified, with experience in Python, Linux, technical problem-solving, and automation. Currently building practical skills in cloud security, security engineering, and DevSecOps.

## License

This project is licensed under the [MIT License](LICENSE).
