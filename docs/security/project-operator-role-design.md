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

### Phase 2 — Session Manager access

Phase 2 has been implemented and validated.

- Allowed `ssm:StartSession` only for instances tagged `Project = AWSCloudSecurityLab`.
- Allowed use of the default `SSM-SessionManagerRunShell` session document.
- Allowed the assumed-role identity to open its own session data channel.
- Restricted resume and termination permissions to sessions belonging to the current identity.
- Added read-only Session Manager discovery and connection-status permissions.
- Did not grant `ssm:SendCommand`.
- Did not grant permission to create or modify Session Manager documents or preferences.
- Did not grant KMS permissions because session-data KMS encryption is not currently configured.

Live validation confirmed:

1. The tagged instance appeared as an available managed node.
2. The operator role successfully opened a browser-based session.
3. The operating-system identity was `ssm-user`.
4. The Amazon SSM Agent reported `active`.
5. The session terminated successfully.
6. The instance was returned to a stopped state.

### Phase 3 — Secure-data S3 access

Phase 3 has been implemented and validated.

- Allowed console discovery of S3 buckets without granting access to their contents.
- Allowed listing and viewing security settings for the approved secure-data bucket.
- Allowed reading, uploading, and deleting approved test objects.
- Allowed access to existing object versions for recovery and validation.
- Did not grant `s3:DeleteObjectVersion`, preventing permanent deletion of versioned objects.
- Did not grant permission to modify bucket policies, public-access controls, encryption, or versioning.
- Did not grant access to objects stored in the CloudTrail audit bucket.

Live validation confirmed:

1. The operator could open the secure-data bucket and view its existing objects.
2. A harmless validation file could be uploaded and downloaded successfully.
3. A normal deletion created a recoverable delete marker.
4. Permanent deletion of the original object version was denied.
5. The CloudTrail bucket remained visible for console navigation, but its objects could not be listed.
6. Policy Simulator allowed `ListBucket` and `GetBucketPublicAccessBlock`.
7. Policy Simulator denied `PutBucketPolicy`, `PutBucketPublicAccessBlock`, `DeleteBucketPolicy`, and `DeleteBucket`.

Evidence:

[Operator S3 least-privilege simulation](../evidence/08-operator-s3-least-privilege.png)

### Phase 4 — CloudTrail and IAM visibility

Phase 4 has been implemented and validated.

#### CloudTrail visibility

- Allowed discovery of trails in the AWS account.
- Allowed read-only access to the lab trail configuration, logging status, event selectors, Insights selectors, and tags.
- Did not grant `cloudtrail:LookupEvents`, preventing general access to account event history.
- Did not grant permission to stop logging, update the trail, or change event selectors.

Live validation confirmed:

1. The operator could view the trail list.
2. The lab trail configuration opened successfully.
3. Logging status and event selectors were visible.
4. CloudTrail Event history returned `AccessDeniedException`.
5. The CloudTrail audit bucket remained inaccessible.
6. Policy Simulator denied `StopLogging` and `UpdateTrail`.

Evidence:

[Operator CloudTrail least-privilege simulation](../evidence/09-operator-cloudtrail-least-privilege.png)

#### IAM visibility

- Allowed discovery of IAM roles and managed policies.
- Restricted detailed role access to resources using the `cloud-security-lab-` naming prefix.
- Restricted detailed customer-managed policy access to the same project prefix.
- Allowed visibility of the AWS-managed `SecurityAudit` policy used by the auditor role.
- Did not grant user enumeration, policy attachment, trust-policy modification, or `iam:PassRole`.

Live validation confirmed:

1. The operator could view the IAM role list.
2. The operator role details, trust relationship, and attached policy were visible.
3. The operator policy document and default version were visible.
4. The IAM Users page denied `iam:ListUsers`.
5. Policy Simulator denied `AttachRolePolicy`, `UpdateAssumeRolePolicy`, and `PassRole`.

Evidence:

[Operator IAM least-privilege simulation](../evidence/10-operator-iam-least-privilege.png)

### Remaining implementation

- Review console background-read errors individually.
- Reduce routine reliance on bootstrap administrator access after validation is complete.
