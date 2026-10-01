# EC2 Security State Audit

## Overview

The EC2 security state auditor evaluates the current configuration
of project-tagged EC2 instances and their associated security groups.

Unlike the CloudTrail detector, which analyzes historical events,
this script checks the live AWS configuration at the time it runs.

The script uses read-only AWS CLI operations and does not print
AWS account IDs, resource IDs, ARNs, security-group IDs, or other
sensitive identifiers.

## Security checks

| Check | Expected secure state |
|---|---|
| Project instance discovery | At least one matching instance exists |
| Public SSH exposure | No TCP port 22 access from `0.0.0.0/0` or `::/0` |
| IMDSv2 enforcement | `HttpTokens` is set to `required` |
| Metadata endpoint | Instance metadata endpoint is enabled |
| Metadata response hop limit | Hop limit is between 1 and 2 |
| EC2 key-pair exposure | No EC2 key pair is attached |

These checks represent the intended security baseline for this lab.
They are not a universal baseline for every AWS environment.

## Resource discovery

Instances are discovered using the project tag:

```text
Project=AWSCloudSecurityLab
```

This avoids hardcoding instance IDs or other environment-specific
resource identifiers in the repository.

## Requirements

- Python 3
- AWS CLI version 2
- An authenticated AWS CLI profile
- Permission to perform:
    - `ec2:DescribeInstances`
    - `ec2:DescribeSecurityGroups`

The script uses only the Python standard library and AWS CLI. It does
not require Boto3 or additional Python packages.

## Running the audit

Authenticate through the AWS CLI:

```powershell
aws login --profile lab-admin
```

From the repository root, run:
```powershell
python .\scripts\audit_aws_security_state.py
```

After completing the audit, close the authenticated CLI session:

```powershell
aws logout --profile lab-admin
```

Alternative profiles, regions, and project tags can be supplied:

```powershell
python .\scripts\audit_aws_security_state.py `
    --profile PROFILE_NAME `
    --region AWS_REGION `
    --project-tag PROJECT_TAG_VALUE
```

## Exit codes
|Exit code |	Meaning |
|---|---|
|0 |	All security checks passed |
|1 |	One or more security checks failed |
|2 |	The audit could not complete |


The non-zero exit codes allow the auditor to be used later in
automated security checks and CI workflows.

## Example secure result

```text
AWS EC2 Security State Audit

[PASS] Project instance discovery: 1 matching instance(s)
[PASS] Public SSH exposure: No public TCP/22 rules detected
[PASS] IMDSv2 enforcement: Required on all matching instances
[PASS] Metadata endpoint: Enabled on all matching instances
[PASS] Metadata response hop limit: All values are between 1 and 2
[PASS] EC2 key-pair exposure: No key pairs attached
[INFO] Instance states: stopped=1

Checks passed: 6
Checks failed: 0
```

## Unit testing

The audit logic is tested with synthetic EC2 and security-group data.
The unit tests do not connect to AWS.

Run all project tests with:

```powershell
python -m unittest discover -s tests -v
```

The tests cover:
- Public IPv4 SSH exposure
- Public IPv6 SSH exposure
- Port ranges containing TCP port 22
- Private SSH rules
- Unrelated public ports
- Public SSH rule counting
- A fully secure instance
- Optional IMDSv2 tokens
- Attached EC2 key pairs
- Public SSH audit failure
- Missing project instances

## Evidence

### Current-state audit
 
### Unit tests
 
## Limitations

- The auditor currently evaluates EC2 configuration only.
- It checks instances matching one project-tag value.
- It reports configuration state but does not modify resources.
- It does not replace AWS Config, Security Hub, GuardDuty, or a
  full cloud security posture management platform.
- Results reflect the AWS configuration at the time the script runs.
