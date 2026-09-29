# CloudTrail Security Change Detection

## Objective

Build a local Python detector that analyzes downloaded AWS CloudTrail records and identifies security-relevant configuration changes.

The detector focuses on the three controlled incidents performed during Stage 3:

- Public SSH security-group exposure
- Removal of S3 TLS-enforcement policy
- Regression from IMDSv2-required to IMDSv2-optional

## Detection scope

| CloudTrail event | Condition | Severity | Status |
|---|---|---|---|
| `AuthorizeSecurityGroupIngress` | TCP port 22 exposed to `0.0.0.0/0` or `::/0` | High | Open |
| `RevokeSecurityGroupIngress` | Public TCP port 22 rule removed | Info | Remediated |
| `DeleteBucketPolicy` | An S3 bucket policy was deleted | High | Open |
| `PutBucketPolicy` | An S3 bucket policy was created or updated | Review | Changed |
| `ModifyInstanceMetadataOptions` | `HttpTokens` changed to `optional` | High | Open |
| `ModifyInstanceMetadataOptions` | `HttpTokens` changed to `required` | Info | Remediated |

## Input handling

The detector recursively reads:

- Uncompressed `.json` files
- Gzip-compressed `.json.gz` files
- Standard CloudTrail payloads containing a `Records` array

Raw CloudTrail files are stored locally under:

```text
cloudtrail-logs/
```

This directory is excluded through .gitignore because raw logs can contain:
- AWS account IDs
- IAM usernames
- Resource identifiers
- ARNs
- Source IP addresses
- Session information
- Request parameters
Only the sanitized detector output is published.

## Usage

Run the detector from the repository root:
```powershell
python .\scripts\detect_security_changes.py
```

The detector reports:
- Files successfully read
- Records processed
- Unreadable files
- Security-relevant changes
- Event timestamps
- Severity
- Event status
- Event name
- Sanitized finding description
- Severity totals

## Privacy-aware output
The detector deliberately excludes:
- Account IDs
- Usernames
- Instance IDs
- Security-group IDs
- Bucket names
- ARNs
- Event IDs
- Source IP addresses
- Access-key and session identifiers
Unreadable-file errors also avoid printing CloudTrail filenames because those filenames can contain an AWS account ID.

## CloudTrail schema handling
During testing, EC2 metadata-option events used a nested request structure:
```text
requestParameters
└── ModifyInstanceMetadataOptionsRequest
    └── HttpTokens
```

The original parser expected `httpTokens` directly beneath `requestParameters`, causing the IMDS events to be missed.
The detector was updated to:
1. Detect the nested request object.
2. Fall back to the top-level request parameters when necessary.
3. Match field names case-insensitively.
4. Support both flattened and nested CloudTrail formats.
This investigation demonstrated that detection logic must account for service-specific and format-specific log structures.

## Validation results
The detector was tested against the Cape Town CloudTrail logs generated during the three controlled Stage 3 incidents.
|Metric |	Result|
|---|---|
|CloudTrail files read |	129|
|CloudTrail records processed |	1,133|
|Unreadable files |	0|
|Security-relevant changes |	6|
|High-severity events |	3|
|Review events |	1|
|Informational events |	2|


All six expected changes were detected:
1. Public SSH access authorized
2. Public SSH access revoked
3. S3 bucket policy deleted
4. S3 bucket policy restored or changed
5. IMDSv1 compatibility enabled
6. IMDSv2 enforcement restored

## Interpretation limitations
This script detects security-relevant events; it does not independently validate the current AWS configuration.
Important limitations include:
- `PutBucketPolicy` proves that a policy changed but does not prove the correct TLS policy was restored.
- A remediation event should still be validated against the live configuration.
- The current status labels describe individual events and do not correlate resource state across multiple accounts or resources.
- Results depend on the completeness of the supplied CloudTrail logs.
- Legitimate administrative changes may still require review.
- CloudTrail timestamps are displayed in UTC.
These limitations prevent the detector from claiming that a resource is secure based solely on the presence of a later change event.

##  Evidence
- [Sanitized detector output](../evidence/26-cloudtrail-security-change-detector.png)

## Status
Implemented and validated
