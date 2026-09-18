# Incident 03 — IMDSv2 Enforcement Regression

## Objective

Temporarily weaken the EC2 instance metadata configuration by changing IMDSv2 from required to optional, detect and investigate the change, and restore the secure baseline.

This controlled exercise demonstrates the security impact of permitting tokenless IMDSv1 requests on an EC2 instance.

## Secure baseline

The lab EC2 instance used the following instance metadata configuration:

| Setting | Secure value |
|---|---|
| Instance metadata service | Enabled |
| IMDSv2 | Required |
| HTTP PUT response hop limit | 2 |
| Metadata-tag access | Unchanged |

With IMDSv2 required, requests to the Instance Metadata Service must include a valid session token and IMDSv1 requests are rejected.

## Misconfiguration

The IMDSv2 setting was temporarily changed from **Required** to **Optional**.

Optional mode does not disable IMDSv2. It allows both:

- Token-based IMDSv2 requests
- Tokenless IMDSv1 requests

The metadata endpoint remained enabled and the response hop limit remained set to `2`.

## Safety controls

- The EC2 instance remained stopped throughout the exercise.
- The instance had no EC2 key pair configured.
- The associated security group retained zero inbound rules.
- The instance was not assigned a reachable workload during the test.
- No IMDSv1 request was performed.
- Only the IMDSv2 token requirement was changed.
- The metadata endpoint remained enabled.
- The response hop limit remained set to `2`.
- Metadata-tag access was not modified.
- CloudTrail logging remained enabled.
- IMDSv2 enforcement was restored immediately after evidence was collected.

## Security risk

Allowing IMDSv1 enables tokenless requests to the EC2 Instance Metadata Service.

If a running workload contains a server-side request forgery vulnerability or another path allowing unintended metadata access, an attacker may be able to retrieve instance metadata or temporary role credentials more easily.

Requiring IMDSv2 adds a session-token requirement that strengthens protection against several metadata-access attack paths.

## Execution timeline

| Phase | Result |
|---|---|
| Secure baseline | IMDSv2 required, metadata enabled, and hop limit set to 2 |
| Safety validation | Instance stopped, no key pair, and zero inbound rules |
| Misconfiguration | IMDSv2 changed from Required to Optional |
| Detection | Metadata-options dialog confirmed Optional mode |
| Regression event | `ModifyInstanceMetadataOptions` recorded at 12:48:25 UTC+02:00 |
| Remediation | IMDSv2 changed back to Required |
| Restoration event | `ModifyInstanceMetadataOptions` recorded at 12:48:49 UTC+02:00 |
| Regression window | Approximately 24 seconds according to CloudTrail |
| Final state | IMDSv2 required, metadata enabled, hop limit 2, and instance stopped |

## CloudTrail investigation

CloudTrail Event history recorded both configuration changes as EC2 management events.

| Event | Event source | Identity type | `httpTokens` |
|---|---|---|---|
| `ModifyInstanceMetadataOptions` | `ec2.amazonaws.com` | `IAMUser` | `optional` |
| `ModifyInstanceMetadataOptions` | `ec2.amazonaws.com` | `IAMUser` | `required` |

The two events established:

- When IMDSv1 compatibility was enabled
- When IMDSv2 enforcement was restored
- Which AWS service processed the changes
- What identity type performed the actions
- The duration of the weakened configuration

Sensitive identity and resource identifiers were excluded from the published evidence.

## Detection

The regression was detected through:

1. Direct inspection of the instance metadata options.
2. Confirmation that IMDSv2 was set to Optional.
3. Comparison with the documented secure baseline.
4. CloudTrail filtering for `ModifyInstanceMetadataOptions`.
5. Inspection of `requestParameters.httpTokens` in each event record.

## Remediation

The IMDSv2 setting was changed back to **Required**.

Remediation was validated by:

- Reopening the instance metadata-options window
- Confirming that IMDSv2 was Required
- Confirming that the metadata service remained enabled
- Confirming that the response hop limit remained `2`
- Confirming that the instance remained stopped
- Confirming that the security group retained zero inbound rules
- Finding the restoration event with `httpTokens` set to `required`

## Impact assessment

The EC2 instance remained stopped throughout the exercise.

Because no workload was running, no process could query the Instance Metadata Service while IMDSv1 compatibility was temporarily enabled. No metadata or temporary credentials were requested or exposed.

The exercise demonstrated a configuration-level security regression without exposing a running workload.

## Lessons learned

- Optional mode supports both IMDSv1 and IMDSv2; it does not mean IMDSv2 only.
- Requiring IMDSv2 disables tokenless IMDSv1 requests.
- Instance metadata options can be modified on a stopped EC2 instance.
- CloudTrail records both the weakening and restoration actions.
- The `requestParameters.httpTokens` value distinguishes the two otherwise identical event names.
- Configuration evidence and audit evidence should be used together.
- A stopped instance reduces immediate exposure but does not make a weakened configuration acceptable.
- Security settings should be restored and independently verified after controlled testing.

## Evidence

- [IMDSv2-required secure baseline](../evidence/22-imdsv2-required-baseline.png)
- [IMDSv2-optional misconfiguration](../evidence/23-imdsv2-optional-misconfiguration.png)
- [IMDSv2-required remediated state](../evidence/24-imdsv2-required-remediated.png)
- [`ModifyInstanceMetadataOptions` CloudTrail events](../evidence/25-cloudtrail-modify-instance-metadata-options.png)

## Evidence checklist

- [x] IMDSv2-required secure baseline
- [x] IMDSv2-optional misconfiguration
- [x] Restored IMDSv2-required configuration
- [x] CloudTrail events for both metadata-option changes
- [x] Confirmation that the instance remained stopped
- [x] Confirmation that network exposure remained unchanged

## Status

Complete — Remediated
