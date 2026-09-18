# Incident 01 — Public SSH Security-Group Exposure

## Objective

Temporarily introduce an overly permissive SSH security-group rule, detect and investigate the configuration change, and restore the secure baseline.

This controlled exercise demonstrates how a simple network change can expose an administrative service to the public internet.

## Misconfiguration

The lab EC2 security group temporarily allowed:

| Type | Protocol | Port | Source |
|---|---|---:|---|
| SSH | TCP | 22 | `0.0.0.0/0` |

This configuration would permit IPv4 traffic from any internet address to reach TCP port 22 when an associated resource is running and reachable.

## Safety controls

- The EC2 instance remained stopped throughout the exercise.
- The instance had no EC2 key pair configured.
- The rule was added only to the project EC2 security group.
- No additional ports were opened.
- CloudTrail logging remained enabled.
- The rule was removed immediately after evidence was collected.
- No real credentials, sensitive data, or production resources were involved.

## Security risk

Allowing SSH from `0.0.0.0/0` unnecessarily exposes an administrative service to internet scanning, brute-force attempts, credential attacks, and exploitation of vulnerable SSH services.

Administrative access for this lab is provided through AWS Systems Manager Session Manager, so an inbound SSH rule is not operationally required.

## Execution timeline

| Phase | Result |
|---|---|
| Secure baseline | Instance stopped, no key pair, and zero inbound rules |
| Misconfiguration | SSH on TCP 22 allowed from `0.0.0.0/0` |
| Detection | Insecure rule confirmed in the security-group configuration |
| Authorization event | `AuthorizeSecurityGroupIngress` recorded at 09:27:13 UTC+02:00 |
| Remediation | Temporary SSH rule removed |
| Revocation event | `RevokeSecurityGroupIngress` recorded at 09:28:45 UTC+02:00 |
| Exposure window | Approximately 92 seconds according to CloudTrail event timestamps |
| Final state | Zero inbound rules and instance still stopped |

## CloudTrail investigation

CloudTrail Event history recorded both security-group changes as management events.

| Event | Event source | Identity type |
|---|---|---|
| `AuthorizeSecurityGroupIngress` | `ec2.amazonaws.com` | `IAMUser` |
| `RevokeSecurityGroupIngress` | `ec2.amazonaws.com` | `IAMUser` |

The events established:

- What configuration action occurred
- When the change occurred
- Which AWS service processed it
- What identity type performed it
- When the insecure configuration was removed

Sensitive identity and resource identifiers were excluded from the published evidence.

## Detection

The misconfiguration was detected through:

1. Direct inspection of the security group’s inbound rules.
2. Identification of SSH on TCP port 22 from `0.0.0.0/0`.
3. CloudTrail Event history filtering for `AuthorizeSecurityGroupIngress`.
4. Comparison with the original secure baseline.

## Remediation

The temporary SSH rule was removed from the security group.

Remediation was validated by:

- Confirming the inbound-rule count returned to zero
- Locating `RevokeSecurityGroupIngress` in CloudTrail
- Confirming the EC2 instance remained stopped
- Confirming no key pair was configured
- Preserving Systems Manager Session Manager as the approved administration method

## Impact assessment

No workload was running during the test, and no reachable SSH service was available.

The exercise demonstrated a configuration-level security exposure without placing a running host or real data at risk.

## Lessons learned

- Security-group changes are recorded as CloudTrail management events.
- `AuthorizeSecurityGroupIngress` and `RevokeSecurityGroupIngress` provide a clear configuration-change timeline.
- A stopped instance reduces immediate exposure but does not make an insecure rule acceptable.
- Administrative ports should not be publicly exposed when Session Manager is available.
- Baseline and post-remediation evidence are both necessary to prove restoration.
- CloudTrail timestamps provide a more reliable exposure window than a manual estimate.
- Identity type, event source, action, and time can support an investigation without publishing sensitive identifiers.

## Evidence

- [Stopped EC2 instance with no key pair](../evidence/11-ec2-stopped-no-key-pair.png)
- [Secure inbound-rule baseline](../evidence/12-inbound-rules-secure-baseline.png)
- [Temporary public SSH misconfiguration](../evidence/13-public-ssh-misconfiguration.png)
- [Remediated inbound-rule baseline](../evidence/14-inbound-rules-remediated.png)
- [`AuthorizeSecurityGroupIngress` event](../evidence/15-cloudtrail-authorize-security-group-ingress.png)
- [`RevokeSecurityGroupIngress` event](../evidence/16-cloudtrail-revoke-security-group-ingress.png)

## Evidence checklist

- [x] Secure baseline before the change
- [x] Temporary public SSH rule
- [x] `AuthorizeSecurityGroupIngress` CloudTrail event
- [x] Restored security-group baseline
- [x] `RevokeSecurityGroupIngress` CloudTrail event
- [x] Final confirmation that the instance remained stopped

## Status

Complete — Remediated
