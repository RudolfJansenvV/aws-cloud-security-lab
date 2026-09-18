# Incident 02 — Missing S3 TLS Enforcement

## Objective

Temporarily remove the secure-data bucket policy that requires encrypted transport, detect and investigate the configuration change, and restore the security control.

This controlled exercise demonstrates how removing a resource-based policy can weaken data-in-transit protection even when the bucket remains private.

## Secure baseline

The secure-data bucket used an explicit deny statement with the following condition:

```json
"Bool": {
  "aws:SecureTransport": "false"
}
```
This policy denied S3 actions when a request did not use secure transport.

The policy applied to both:

- The S3 bucket
- All objects stored within the bucket

## Misconfiguration

The bucket policy containing the DenyInsecureTransport statement was temporarily deleted.

During this period:

- The bucket no longer explicitly enforced secure transport through its resource policy.
- Permitted requests would no longer be denied solely because aws:SecureTransport was false.
- S3 Block Public Access remained fully enabled.
- The bucket was not made public.
- No non-TLS request was performed.

## Safety controls
- The exercise affected only the project secure-data bucket.
- The CloudTrail log bucket was not modified.
- All four S3 Block Public Access settings remained enabled.
- The complete policy was copied locally before removal.
- No bucket ACLs or public-access settings were changed.
- No objects were uploaded, downloaded, modified, or deleted during the test.
- No HTTP or other non-TLS request was attempted.
- CloudTrail logging remained enabled.
- The policy was restored immediately after evidence was collected.

## Security risk

Without an explicit secure-transport requirement, an authorized principal could potentially use a non-TLS request if the client and endpoint permitted it.

That would weaken protection for data in transit and could expose request contents, object data, or authentication information to interception.

Block Public Access does not replace transport-security enforcement. It limits public access but does not require authorized requests to use TLS.

## Execution timeline
|Phase |	Result |
|---|---|
|Secure baseline |	DenyInsecureTransport policy present |
|Safety validation |	Block Public Access enabled and recovery policy saved |
|Misconfiguration	| Bucket policy deleted |
|Detection |	Bucket policy section displayed No policy to display |
|Deletion event |	DeleteBucketPolicy recorded at 11:34:14 UTC+02:00 |
|Remediation |	Original TLS-enforcement policy restored |
|Restoration event	| PutBucketPolicy recorded at 11:34:34 UTC+02:00 |
|Policy-absence window |	Approximately 20 seconds according to CloudTrail |
|Final state |	TLS denial policy restored and Block Public Access still enabled |

## CloudTrail investigation

CloudTrail Event history recorded both policy changes as S3 management events.

| Event|	Event source	| Identity type |
|---|---|---|
| DeleteBucketPolicy |	s3.amazonaws.com |	IAMUser |
| PutBucketPolicy	| s3.amazonaws.com |	IAMUser |

The events established:
- Which configuration actions occurred
- When the policy was removed
- When the policy was restored
- Which AWS service processed the requests
- What identity type performed the actions

Sensitive identity and resource identifiers were excluded from the published evidence.

## Detection

The missing security control was detected through:

1. Direct inspection of the bucket-policy configuration.
2. Confirmation that the console displayed `No policy to display`.
3. Comparison with the documented secure baseline.
4. CloudTrail filtering for `DeleteBucketPolicy`.
5. CloudTrail filtering for `PutBucketPolicy`.

## Remediation

The original bucket policy was restored from the locally saved recovery copy.

Remediation was validated by:

- Confirming that DenyInsecureTransport was present
- Confirming that aws:SecureTransport was set to false within the deny condition
- Confirming that both the bucket and object resources were covered
- Confirming that Block Public Access remained enabled
- Locating the corresponding PutBucketPolicy event in CloudTrail

## Impact assessment

The bucket remained private throughout the exercise because all Block Public Access settings remained enabled.

No insecure transport request was performed, and no object access or modification occurred while the policy was absent.

The exercise therefore demonstrated a configuration-level security weakness without intentionally transmitting data insecurely or exposing the bucket publicly.

## Lessons learned
- Bucket privacy and transport-security enforcement are separate controls.
- Block Public Access does not replace a policy requiring secure transport.
- Resource-policy deletion is visible through CloudTrail management events.
- Recovery copies should be prepared before changing security policies.
- Baseline, misconfigured, and remediated evidence provides a complete incident record.
- CloudTrail timestamps provide a more reliable control-gap duration than a manual estimate.
- Remediation must be validated by inspecting both the restored configuration and its audit event.

## Evidence

- [Secure TLS-enforcement baseline](../evidence/17-s3-tls-policy-secure-baseline.png)
- [Missing bucket-policy misconfiguration](../evidence/18-s3-tls-policy-misconfiguration.png)
- [Restored TLS-enforcement policy](../evidence/19-s3-tls-policy-remediated.png)
- [`DeleteBucketPolicy` CloudTrail event](../evidence/20-cloudtrail-delete-bucket-policy.png)
- [`PutBucketPolicy` CloudTrail event](../evidence/21-cloudtrail-put-bucket-policy.png)

## Evidence checklist
- [x] Secure TLS-enforcement baseline
- [x] Missing-policy configuration
- [x] Restored TLS-enforcement policy
- [x] `DeleteBucketPolicy` CloudTrail event
- [x] `PutBucketPolicy` CloudTrail event
- [x] Confirmation that Block Public Access remained enabled

## Status

Complete — Remediated
