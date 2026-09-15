# AWS CloudTrail Audit Logging

## Objective

Create persistent audit logging for AWS account activity and validate that
management and selected S3 object-level events are captured.

## Trail configuration

The multi-Region trail `cloud-security-lab-trail` was configured with:

- Read and write management events
- Log-file validation
- A dedicated S3 audit-log bucket
- S3 data events scoped to one secure-data bucket
- Read and write S3 data events
- No organization-wide configuration
- No CloudTrail Insights events
- No network activity events

The exact audit-bucket name and AWS account identifiers are intentionally
excluded from this repository.

## Audit-log storage

CloudTrail logs are delivered to a dedicated S3 bucket separate from workload
data.

The audit bucket uses:

- S3 Block Public Access
- Bucket-owner-enforced Object Ownership
- Disabled ACLs
- SSE-S3 encryption
- S3 Versioning
- Audit-log classification tags
- A CloudTrail-generated delivery policy

The automatically generated bucket policy was preserved because it grants the
CloudTrail service the permissions required to validate the bucket and deliver
log objects.
