# Project Operator Role Design

## Objective

Create an IAM role for routine operation of the AWS cloud security lab without granting full administrator access.

The role will provide enough permission to operate approved lab resources while protecting IAM, audit logging, network security controls, and unrelated AWS resources.

## Role name

`cloud-security-lab-operator-role`

## Security principles

- Require MFA before the role can be assumed.
- Grant only the permissions required for routine lab work.
- Restrict write actions to approved project resources where AWS supports resource-level controls.
- Keep IAM and CloudTrail administration outside the operator role.
- Continue using the bootstrap administrator account as a temporary recovery path.
- Add permissions only when a legitimate requirement is identified.

## Initial permission design

| Service | Permitted | Not permitted |
|---|---|---|
| EC2 | View instances; start, stop, and reboot approved lab instances | Create or terminate instances |
| Systems Manager | Connect to approved lab instances using Session Manager | Modify Systems Manager security configuration |
| S3 secure-data bucket | List, read, upload, and delete test objects | Change the bucket policy, encryption, versioning, or public-access controls |
| CloudTrail | View trail configuration and status | Stop, delete, or modify the trail |
| VPC | View the VPC, subnets, route tables, and security groups | Change routes, security groups, subnets, or internet connectivity |
| IAM | View relevant roles and policies | Create identities, attach policies, change trust policies, or escalate privileges |
| Audit-log bucket | No routine object access | Read, modify, or delete audit logs |

## Protected controls

The operator role must not be able to:

- Stop or delete CloudTrail logging.
- Modify the CloudTrail audit bucket.
- Change S3 public-access protections.
- Modify IAM roles or policies.
- Attach administrator permissions.
- Pass arbitrary IAM roles to AWS services.
- Change security-group or routing rules.
- Operate unrelated resources in the AWS account.

## Why the role begins with limited permissions

The initial role is intentionally narrow. Permissions will be added iteratively when a real operational requirement is demonstrated.

This reduces the risk of privilege escalation, accidental exposure, audit-log tampering, and unintended changes to the lab environment.

## Validation plan

The role will be tested using the IAM Policy Simulator and temporary console access.

Expected tests include:

| Test action | Expected result |
|---|---|
| View EC2 instances | Allowed |
| Start an approved lab instance | Allowed |
| Terminate an EC2 instance | Denied |
| Connect through Session Manager | Allowed |
| Read an object from the secure-data bucket | Allowed |
| Modify the secure-data bucket policy | Denied |
| View CloudTrail status | Allowed |
| Stop CloudTrail logging | Denied |
| View IAM roles | Allowed |
| Attach an IAM policy | Denied |

## Implementation status

### Phase 1 — EC2 operations

Phase 1 has been implemented and validated.

- Created the `cloud-security-lab-operator-role`.
- Required MFA in the role trust policy.
- Attached only the customer-managed `cloud-security-lab-operator-policy`.
- Allowed EC2 and network visibility.
- Restricted start, stop, and reboot operations using the `Project = AWSCloudSecurityLab` resource tag.
- Confirmed that instance termination and security-group modification remain denied.
- Validated the policy using both the IAM Policy Simulator and a live role session.
- Retained the bootstrap administrator identity as a temporary recovery path.

Evidence:

[Operator policy simulation](../evidence/07-project-operator-policy-simulation.png)

Troubleshooting:

[Operator policy resource ARN troubleshooting](../troubleshooting/operator-policy-resource-arn.md)

### Remaining implementation

- Add project-scoped Session Manager access.
- Add access to approved objects in the secure-data bucket.
- Add read-only CloudTrail and relevant IAM visibility.
- Review console background-read errors individually.
- Reduce routine reliance on bootstrap administrator access after validation is complete.
