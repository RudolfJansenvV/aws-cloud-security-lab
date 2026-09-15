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

## Management events and data events

Management events record control-plane activity such as creating resources,
modifying policies, and changing service configurations.

S3 object operations are data-plane activity and require data-event logging.

To limit unnecessary logging and cost, S3 data events were enabled only for
the secure-data bucket. The CloudTrail destination bucket was deliberately
excluded to avoid recursive or unnecessary object-event logging.

## Log-file validation

CloudTrail log-file validation was enabled. CloudTrail produces digest files
that can be used to determine whether delivered log files were modified or
deleted after delivery.

## Controlled validation

A test object was used to generate three S3 API operations:

1. Uploading the object generated `PutObject`.
2. Downloading the object generated `GetObject`.
3. Deleting the current object generated `DeleteObject`.

The delivered CloudTrail logs confirmed:

| Event | Event source | Read-only value |
|---|---|---:|
| `PutObject` | `s3.amazonaws.com` | `False` |
| `GetObject` | `s3.amazonaws.com` | `True` |
| `DeleteObject` | `s3.amazonaws.com` | `False` |

This correctly classifies downloading as a read operation and uploading or
deleting as write operations.
